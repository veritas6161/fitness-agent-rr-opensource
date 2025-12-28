"""
Fitness Agent - Main Orchestrator

Handles the complete workflow:
1. Receive trigger (cron or manual)
2. Determine day type
3. Load past workouts from Sheets
4. Call Generator Agent
5. Call Eval Agent (loop up to 3 times)
6. Send email + write to Sheets
"""

import functions_framework
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from config import SPREADSHEET_ID, MAX_EVAL_ATTEMPTS
import sheets_client
import generator_agent
import eval_agent
import email_client


# Day type rotation (excluding Friday = trainer day)
DAY_TYPES = [
    "Lower Body Strength",
    "Upper Body Strength",
    "Conditioning/HIIT",
    "Full Body",
    "Zone 2 Cardio",
    "Active Recovery",
]


def get_sheets_service():
    """
    Initialize Google Sheets API service.
    
    Returns:
        Google Sheets API service object, or None if credentials not set
    """
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    
    if not creds_json:
        print("Warning: GOOGLE_CREDENTIALS not set - Sheets operations will be skipped")
        return None
    
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    
    return build('sheets', 'v4', credentials=credentials)


def determine_day_type(
    service,
    spreadsheet_id: str,
    day_of_week: str,
    past_workouts: List[Dict[str, Any]],
) -> str:
    """
    Determine what type of workout to generate based on recent history.
    
    Args:
        service: Google Sheets API service
        spreadsheet_id: Spreadsheet ID
        day_of_week: Current day name
        past_workouts: Recent workout data
    
    Returns:
        Day type string (e.g., "Lower Body Strength")
    """
    # Friday = trainer day, should not trigger
    if day_of_week.lower() == "friday":
        raise RuntimeError("Friday is trainer day - no agent workouts")
    
    # Look at last few workouts to determine rotation
    if not past_workouts:
        # No history, start with Lower Body
        return "Lower Body Strength"
    
    # Find what was done recently
    recent_types = []
    for workout in past_workouts[:5]:
        tab_name = workout.get("tab_name", "")
        for day_type in DAY_TYPES:
            if day_type.lower() in tab_name.lower():
                recent_types.append(day_type)
                break
    
    # Smart rotation: pick least recent type, respecting 48h rule
    for day_type in DAY_TYPES:
        if day_type not in recent_types:
            return day_type
    
    # All types done recently, cycle back
    return DAY_TYPES[len(past_workouts) % len(DAY_TYPES)]


def get_sheet_link(spreadsheet_id: str, tab_name: str) -> str:
    """
    Generate Google Sheets link for the workout tab.
    
    Args:
        spreadsheet_id: Spreadsheet ID
        tab_name: Tab name
    
    Returns:
        Google Sheets URL
    """
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"


@functions_framework.http
def generate_workout(request):
    """
    Main entry point for Cloud Function.
    
    Handles:
    - GET request (cron trigger or manual)
    - POST request (webhook)
    
    Query params (optional):
    - day_type: Override day type
    - trigger: "manual" for manual trigger
    """
    try:
        # Parse request
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            day_type_override = data.get("day_type")
            trigger_source = data.get("source", "webhook")
        else:
            day_type_override = request.args.get("day_type")
            trigger_source = request.args.get("trigger", "cron")
        
        print(f"Trigger source: {trigger_source}")
        
        # Get current date info
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        day_of_week = now.strftime("%A")
        
        print(f"Date: {date_str}, Day: {day_of_week}")
        
        # Friday check
        if day_of_week.lower() == "friday":
            return json.dumps({
                "status": "skipped",
                "reason": "Friday is trainer day",
                "date": date_str
            }), 200, {"Content-Type": "application/json"}
        
        # Initialize Sheets service (may be None if no credentials)
        service = get_sheets_service()
        
        # Load past workouts (skip if no service)
        past_workouts = []
        if service:
            try:
                past_workouts = sheets_client.read_past_workouts(
                    service=service,
                    spreadsheet_id=SPREADSHEET_ID,
                    days=14,
                )
                print(f"Loaded {len(past_workouts)} past workouts")
            except Exception as e:
                print(f"Warning: Could not load past workouts: {e}")
        else:
            print("Skipping past workouts (no Sheets credentials)")
        
        # Determine day type
        if day_type_override:
            day_type = day_type_override
        else:
            day_type = determine_day_type(service, SPREADSHEET_ID, day_of_week, past_workouts)
        
        print(f"Day type: {day_type}")
        
        # Generation loop (max 3 attempts)
        attempts = []
        best_attempt = None
        best_score = -1
        passed = False
        
        for attempt_num in range(1, MAX_EVAL_ATTEMPTS + 1):
            print(f"\n=== Attempt {attempt_num}/{MAX_EVAL_ATTEMPTS} ===")
            
            # Get feedback from previous attempt (if any)
            feedback = None
            if attempts:
                last_eval = attempts[-1].get("eval", {})
                if last_eval.get("issues"):
                    feedback = "Previous attempt issues:\n" + "\n".join(
                        f"- {issue}" for issue in last_eval["issues"]
                    )
            
            # Call Generator
            try:
                gen_result = generator_agent.generate_workout(
                    date=date_str,
                    day_of_week=day_of_week,
                    day_type=day_type,
                    past_workouts=past_workouts,
                    feedback=feedback,
                )
                print(f"Generator: {gen_result.get('model_used', 'unknown')}")
            except Exception as e:
                print(f"Generator error: {e}")
                attempts.append({"error": str(e), "eval": {"decision": "FAIL", "overall": 0}})
                continue
            
            # Call Eval
            try:
                eval_result = eval_agent.evaluate_workout(
                    workout_email=gen_result.get("email", ""),
                    workout_json=gen_result.get("json"),
                    date=date_str,
                    day_of_week=day_of_week,
                    day_type=day_type,
                    past_workouts=past_workouts,
                )
                print(f"Eval: {eval_result.get('decision', 'UNKNOWN')} ({eval_result.get('overall', 0)}/5)")
            except Exception as e:
                print(f"Eval error: {e}")
                eval_result = {"decision": "FAIL", "overall": 0, "summary": str(e), "issues": [str(e)]}
            
            # Store attempt
            attempts.append({
                "attempt": attempt_num,
                "gen": gen_result,
                "eval": eval_result,
            })
            
            # Track best attempt
            score = eval_result.get("overall", 0)
            if score > best_score:
                best_score = score
                best_attempt = attempts[-1]
            
            # Check if passed
            if eval_result.get("decision") == "PASS":
                passed = True
                print("Eval PASSED!")
                break
            else:
                print(f"Eval FAILED: {eval_result.get('summary', 'No summary')}")
        
        # Determine final output
        if passed:
            final_attempt = attempts[-1]
            is_warning = False
        else:
            final_attempt = best_attempt or attempts[-1]
            is_warning = True
            print(f"\nAll {MAX_EVAL_ATTEMPTS} attempts failed. Using best attempt (score: {best_score})")
        
        # Extract final content
        workout_email = final_attempt.get("gen", {}).get("email", "")
        workout_json = final_attempt.get("gen", {}).get("json")
        eval_result = final_attempt.get("eval", {})
        
        # Build eval append for email
        if is_warning:
            eval_append = eval_agent.format_failed_attempts_for_email(
                [a.get("eval", {}) for a in attempts]
            )
        else:
            eval_append = eval_result.get("email_append", "")
        
        # Write to Sheets
        tab_name = f"Workout_{date_str}"
        try:
            if workout_json and workout_json.get("rows"):
                # Build data for sheet
                headers = ["Exercise", "Set", "Weight", "Reps", "RIR", "Feel", "Notes"]
                rows = [headers]
                for row in workout_json["rows"]:
                    rows.append([
                        row.get("exercise", ""),
                        row.get("set", ""),
                        row.get("weight", ""),
                        row.get("reps", ""),
                        row.get("rir", ""),
                        row.get("feel", ""),
                        row.get("notes", ""),
                    ])
                
                # Create tab and write
                if not sheets_client.tab_exists(service, SPREADSHEET_ID, tab_name):
                    sheets_client.create_tab(service, SPREADSHEET_ID, tab_name)
                
                sheets_client.write_data(service, SPREADSHEET_ID, tab_name, rows)
                print(f"Wrote to Sheet: {tab_name}")
            else:
                print("Warning: No JSON rows to write to Sheet")
        except Exception as e:
            print(f"Sheets write error: {e}")
        
        # Send email
        sheet_link = get_sheet_link(SPREADSHEET_ID, tab_name)
        try:
            email_result = email_client.send_workout_email(
                workout_email=workout_email,
                eval_append=eval_append,
                date=date_str,
                day_type=day_type,
                sheet_link=sheet_link,
                is_warning=is_warning,
            )
            print(f"Email: {email_result}")
        except Exception as e:
            print(f"Email error: {e}")
            email_result = {"success": False, "error": str(e)}
        
        # Return response
        response = {
            "status": "success" if passed else "warning",
            "date": date_str,
            "day_type": day_type,
            "attempts": len(attempts),
            "passed": passed,
            "eval_score": eval_result.get("overall", 0),
            "sheet_tab": tab_name,
            "email_sent": email_result.get("success", False),
        }
        
        return json.dumps(response), 200, {"Content-Type": "application/json"}
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return json.dumps({"status": "error", "error": str(e)}), 500, {"Content-Type": "application/json"}


# For local testing
if __name__ == "__main__":
    from unittest.mock import Mock
    
    # Create mock request
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.args = {"trigger": "manual"}
    mock_request.get_json = lambda silent=False: None
    
    # Run
    result = generate_workout(mock_request)
    print("\n=== RESULT ===")
    print(result)
