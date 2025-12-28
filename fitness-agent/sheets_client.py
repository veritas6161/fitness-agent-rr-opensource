"""
Generic Google Sheets Client - Reusable across agents

All functions accept spreadsheet_id as a parameter (not hardcoded).
Designed to work with any spreadsheet_id (fitness, nutrition, other agents).
Uses googleapiclient.discovery pattern (not gspread).
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


def read_data(
    service,
    spreadsheet_id: str,
    tab_name: str,
    range_notation: Optional[str] = None
) -> List[List[Any]]:
    """
    Generic read function - reads data from a sheet tab.
    
    Args:
        service: Google Sheets API service object
        spreadsheet_id: The ID of the spreadsheet
        tab_name: Name of the tab to read from
        range_notation: Optional A1 notation range (e.g., "A1:G100"). If None, reads entire tab.
    
    Returns:
        List of rows, where each row is a list of cell values
    """
    if range_notation:
        full_range = f"{tab_name}!{range_notation}"
    else:
        full_range = tab_name
    
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=full_range
    ).execute()
    
    return result.get("values", [])


def write_data(
    service,
    spreadsheet_id: str,
    tab_name: str,
    data: List[List[Any]],
    range_notation: Optional[str] = None,
    value_input_option: str = "USER_ENTERED"
) -> Dict[str, Any]:
    """
    Generic write function - writes data to a sheet tab.
    
    Args:
        service: Google Sheets API service object
        spreadsheet_id: The ID of the spreadsheet
        tab_name: Name of the tab to write to
        data: List of rows to write, where each row is a list of cell values
        range_notation: Optional A1 notation range. If None, writes starting at A1.
        value_input_option: How to interpret input data ("RAW" or "USER_ENTERED")
    
    Returns:
        API response dict
    """
    if range_notation:
        full_range = f"{tab_name}!{range_notation}"
    else:
        full_range = f"{tab_name}!A1"
    
    body = {"values": data}
    
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=full_range,
        valueInputOption=value_input_option,
        body=body
    ).execute()
    
    return result


def append_data(
    service,
    spreadsheet_id: str,
    tab_name: str,
    data: List[List[Any]],
    value_input_option: str = "USER_ENTERED"
) -> Dict[str, Any]:
    """
    Append data to the end of a sheet tab.
    
    Args:
        service: Google Sheets API service object
        spreadsheet_id: The ID of the spreadsheet
        tab_name: Name of the tab to append to
        data: List of rows to append
        value_input_option: How to interpret input data
    
    Returns:
        API response dict
    """
    body = {"values": data}
    
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!A1",
        valueInputOption=value_input_option,
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()
    
    return result


def get_sheet_tabs(service, spreadsheet_id: str) -> List[str]:
    """
    Get list of all tab names in the spreadsheet.
    
    Args:
        service: Google Sheets API service object
        spreadsheet_id: The ID of the spreadsheet
    
    Returns:
        List of tab names
    """
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = spreadsheet.get("sheets", [])
    return [sheet.get("properties", {}).get("title", "") for sheet in sheets]


def create_tab(
    service,
    spreadsheet_id: str,
    tab_name: str,
    headers: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new tab in the spreadsheet.
    
    Args:
        service: Google Sheets API service object
        spreadsheet_id: The ID of the spreadsheet
        tab_name: Name for the new tab
        headers: Optional list of header strings for the first row
    
    Returns:
        API response dict
    """
    # Create the new sheet
    request_body = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": tab_name
                    }
                }
            }
        ]
    }
    
    result = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=request_body
    ).execute()
    
    # If headers provided, write them to the first row
    if headers:
        write_data(service, spreadsheet_id, tab_name, [headers])
    
    return result


def tab_exists(service, spreadsheet_id: str, tab_name: str) -> bool:
    """
    Check if a tab exists in the spreadsheet.
    
    Args:
        service: Google Sheets API service object
        spreadsheet_id: The ID of the spreadsheet
        tab_name: Name of the tab to check
    
    Returns:
        True if tab exists, False otherwise
    """
    existing_tabs = get_sheet_tabs(service, spreadsheet_id)
    return tab_name in existing_tabs


def read_exercise_library(
    service,
    spreadsheet_id: str,
    tab_name: str = "Exercise Library"
) -> List[Dict[str, Any]]:
    """
    Read exercise library tab and return as list of dicts.
    
    Args:
        service: Google Sheets API service object
        spreadsheet_id: The ID of the spreadsheet
        tab_name: Name of the exercise library tab
    
    Returns:
        List of exercise dicts with header keys
    """
    data = read_data(service, spreadsheet_id, tab_name)
    
    if not data or len(data) < 2:
        return []
    
    headers = data[0]
    exercises = []
    
    for row in data[1:]:
        exercise = {}
        for i, header in enumerate(headers):
            exercise[header] = row[i] if i < len(row) else ""
        exercises.append(exercise)
    
    return exercises


def read_past_workouts(
    service,
    spreadsheet_id: str,
    days: int = 14,
    tab_prefix: str = "Workout"
) -> List[Dict[str, Any]]:
    """
    Read workout tabs from the last N days.
    
    Args:
        service: Google Sheets API service object
        spreadsheet_id: The ID of the spreadsheet
        days: Number of days to look back (default 14)
        tab_prefix: Prefix for workout tab names (e.g., "Workout" matches "Workout_2025-12-07")
    
    Returns:
        List of workout dicts with date, day_type, and exercises
    """
    existing_tabs = get_sheet_tabs(service, spreadsheet_id)
    
    # Generate date strings for the past N days
    today = datetime.now()
    date_strings = []
    for i in range(days):
        date = today - timedelta(days=i)
        date_strings.append(date.strftime("%Y-%m-%d"))
    
    workouts = []
    
    for tab_name in existing_tabs:
        # Check if tab matches the workout pattern (e.g., "Workout_2025-12-07")
        # Use prefix + "_" to avoid matching tabs like "WorkoutTemplate"
        if not tab_name.startswith(f"{tab_prefix}_"):
            continue
        
        # Extract date from tab name
        try:
            tab_date = tab_name.split("_")[-1]
            if tab_date not in date_strings:
                continue
        except (IndexError, ValueError):
            continue
        
        # Read the workout data
        try:
            data = read_data(service, spreadsheet_id, tab_name)
            if data:
                workout = {
                    "tab_name": tab_name,
                    "date": tab_date,
                    "data": data
                }
                workouts.append(workout)
        except Exception as e:
            # Log warning but continue processing other tabs
            print(f"Warning: Could not read tab {tab_name}: {e}")
            continue
    
    # Sort by date (most recent first)
    workouts.sort(key=lambda x: x["date"], reverse=True)
    
    return workouts


def create_workout_tab(
    service,
    spreadsheet_id: str,
    date: str,
    day_type: str,
    exercises: List[List[Any]],
    tab_headers: List[str]
) -> Dict[str, Any]:
    """
    Create a new workout tab with exercises.
    
    Args:
        service: Google Sheets API service object
        spreadsheet_id: The ID of the spreadsheet
        date: Date string (e.g., "2025-12-07")
        day_type: Day type (e.g., "Day 4")
        exercises: List of exercise rows to write
        tab_headers: Header row for the workout table
    
    Returns:
        API response dict
    """
    tab_name = f"Workout_{date}"
    
    # Check if tab already exists
    if tab_exists(service, spreadsheet_id, tab_name):
        # Delete existing tab and recreate
        _delete_tab(service, spreadsheet_id, tab_name)
    
    # Create the tab with headers
    create_tab(service, spreadsheet_id, tab_name, tab_headers)
    
    # Write day type info and exercises
    all_data = [
        [f"Date: {date}", f"Day Type: {day_type}"],
        [],  # Empty row for spacing
        tab_headers,
    ] + exercises
    
    write_data(service, spreadsheet_id, tab_name, all_data)
    
    return {"tab_name": tab_name, "rows_written": len(exercises)}


def create_workout_tab_with_eval(
    service,
    spreadsheet_id: str,
    date: str,
    day_type: str,
    exercises: List[List[Any]],
    tab_headers: List[str],
    eval_scores: Dict[str, Any],
    attempts: int
) -> Dict[str, Any]:
    """
    Create workout tab with eval scores below the workout table.
    
    Schema:
    - Workout Table (top): Exercise | Set | Weight | Reps | RIR | Feel | Notes
    - Eval Scores (below): Date | Day Type | Structure Score | Selection Score | 
                           Progression Score | Spatial Score | Overall Score | Attempts | Errors/Warnings
    
    Args:
        service: Google Sheets API service object
        spreadsheet_id: The ID of the spreadsheet
        date: Date string (e.g., "2025-12-07")
        day_type: Day type (e.g., "Day 4")
        exercises: List of exercise rows to write
        tab_headers: Header row for the workout table
        eval_scores: Dict with structure, selection, progression, spatial, overall scores
        attempts: Number of generation attempts before passing eval
    
    Returns:
        API response dict
    """
    tab_name = f"Workout_{date}"
    
    # Check if tab already exists
    if tab_exists(service, spreadsheet_id, tab_name):
        _delete_tab(service, spreadsheet_id, tab_name)
    
    # Create the tab
    create_tab(service, spreadsheet_id, tab_name)
    
    # Build the complete data structure
    # Workout section
    workout_data = [
        [f"Date: {date}", f"Day Type: {day_type}"],
        [],  # Empty row
        tab_headers,
    ] + exercises
    
    # Add spacing before eval section
    workout_data.append([])
    workout_data.append([])
    
    # Eval section headers
    eval_headers = [
        "Date", "Day Type", "Structure Score", "Selection Score",
        "Progression Score", "Spatial Score", "Overall Score", "Attempts", "Errors/Warnings"
    ]
    workout_data.append(eval_headers)
    
    # Eval section data
    errors = eval_scores.get("errors", "")
    eval_row = [
        date,
        day_type,
        eval_scores.get("structure", ""),
        eval_scores.get("selection", ""),
        eval_scores.get("progression", ""),
        eval_scores.get("spatial", ""),
        eval_scores.get("overall", ""),
        attempts,
        errors
    ]
    workout_data.append(eval_row)
    
    # Write all data
    write_data(service, spreadsheet_id, tab_name, workout_data)
    
    return {
        "tab_name": tab_name,
        "workout_rows": len(exercises),
        "eval_included": True
    }


def _delete_tab(service, spreadsheet_id: str, tab_name: str) -> None:
    """
    Delete a tab from the spreadsheet (internal helper).
    
    Args:
        service: Google Sheets API service object
        spreadsheet_id: The ID of the spreadsheet
        tab_name: Name of the tab to delete
    """
    # Get sheet ID
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = spreadsheet.get("sheets", [])
    
    sheet_id = None
    for sheet in sheets:
        if sheet.get("properties", {}).get("title") == tab_name:
            sheet_id = sheet.get("properties", {}).get("sheetId")
            break
    
    if sheet_id is None:
        return
    
    # Delete the sheet
    request_body = {
        "requests": [
            {
                "deleteSheet": {
                    "sheetId": sheet_id
                }
            }
        ]
    }
    
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=request_body
    ).execute()

