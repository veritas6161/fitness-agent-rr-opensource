"""
Eval Agent - Evaluates generated workouts for quality

Model fallback: GPT 5.2 → Gemini 1.5 Flash → Claude Opus 4.5
Outputs: PASS/FAIL decision with scores and feedback
"""

import json
import os
from typing import Dict, Any, Optional, List, Tuple

from config import (
    EVAL_MODEL_PRIORITY,
    ANTHROPIC_API_KEY,
    OPENAI_API_KEY,
    GEMINI_API_KEY,
)


def load_kb_files() -> Dict[str, str]:
    """Load all KB files from the kb/ directory."""
    kb_dir = os.path.join(os.path.dirname(__file__), "kb")
    kb_files = {}
    
    kb_file_names = [
        "goals.md",
        "status.md", 
        "preferences.md",
        "exercise_library.md",
        "gym_layout.md",
    ]
    
    for filename in kb_file_names:
        filepath = os.path.join(kb_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                kb_name = filename.replace(".md", "")
                kb_files[kb_name] = f.read()
        except FileNotFoundError:
            print(f"Warning: KB file not found: {filepath}")
            kb_files[filename.replace(".md", "")] = ""
        except Exception as e:
            print(f"Warning: Error reading KB file {filepath}: {e}")
            kb_files[filename.replace(".md", "")] = ""
    
    return kb_files


def load_system_prompt() -> str:
    """Load the eval system prompt."""
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "eval_prompt.md")
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise RuntimeError(f"Eval prompt not found: {prompt_path}")
    except Exception as e:
        raise RuntimeError(f"Error loading eval prompt: {e}")


def build_user_message(
    workout_email: str,
    workout_json: Optional[Dict[str, Any]],
    date: str,
    day_of_week: str,
    day_type: str,
    kb_files: Dict[str, str],
    past_workouts: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Build the user message for evaluation."""
    message_parts = []
    
    message_parts.append("## Workout to Evaluate")
    message_parts.append(f"**Date:** {date}")
    message_parts.append(f"**Day of Week:** {day_of_week}")
    message_parts.append(f"**Day Type:** {day_type}")
    message_parts.append("")
    
    # KB Files
    message_parts.append("---")
    message_parts.append("## Knowledge Base Files")
    message_parts.append("")
    for kb_name, kb_content in kb_files.items():
        if kb_content:
            message_parts.append(f"### {kb_name.replace('_', ' ').title()}")
            message_parts.append(kb_content)
            message_parts.append("")
    
    # Past workouts
    if past_workouts:
        message_parts.append("---")
        message_parts.append("## Previous Workouts (Last 14 Days)")
        message_parts.append("")
        for workout in past_workouts[:7]:
            message_parts.append(f"### {workout.get('tab_name', 'Unknown')}")
            message_parts.append(f"Date: {workout.get('date', 'Unknown')}")
            if workout.get('data'):
                for row in workout['data'][:20]:
                    message_parts.append(" | ".join(str(cell) for cell in row))
            message_parts.append("")
    
    # Generated workout
    message_parts.append("---")
    message_parts.append("## Generated Workout (Email Format)")
    message_parts.append(workout_email)
    message_parts.append("")
    
    if workout_json:
        message_parts.append("---")
        message_parts.append("## Generated Workout (JSON Format)")
        message_parts.append(json.dumps(workout_json, indent=2))
        message_parts.append("")
    
    message_parts.append("---")
    message_parts.append("## Evaluation Required")
    message_parts.append("Evaluate this workout and return ONLY a JSON object with:")
    message_parts.append("- decision: 'PASS' or 'FAIL'")
    message_parts.append("- overall: average score (0-5)")
    message_parts.append("- scores: {structure, selection, progression, spatial}")
    message_parts.append("- summary: 1-2 sentence summary")
    message_parts.append("- issues: array of specific issues (empty if PASS)")
    message_parts.append("")
    message_parts.append("Return ONLY the JSON, no other text.")
    
    return "\n".join(message_parts)


def call_openai(system_prompt: str, user_message: str) -> Tuple[str, bool]:
    """Call OpenAI API."""
    if not OPENAI_API_KEY:
        return "OpenAI API key not configured", False
    
    try:
        import openai
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-5.2",
            max_completion_tokens=2000,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        
        return response.choices[0].message.content, True
        
    except Exception as e:
        return f"OpenAI API error: {e}", False


def call_gemini(system_prompt: str, user_message: str) -> Tuple[str, bool]:
    """Call Gemini API."""
    if not GEMINI_API_KEY:
        return "Gemini API key not configured", False
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Try gemini-1.5-flash or fallback to gemini-1.5-pro
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_prompt
            )
        except:
            try:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-pro",
                    system_instruction=system_prompt
                )
            except:
                model = genai.GenerativeModel(
                    model_name="gemini-pro",
                    system_instruction=system_prompt
                )
        
        response = model.generate_content(user_message)
        
        return response.text, True
        
    except Exception as e:
        return f"Gemini API error: {e}", False


def call_anthropic(system_prompt: str, user_message: str) -> Tuple[str, bool]:
    """Call Anthropic Claude API."""
    if not ANTHROPIC_API_KEY:
        return "Anthropic API key not configured", False
    
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        response = client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        return response.content[0].text, True
        
    except Exception as e:
        return f"Anthropic API error: {e}", False


def call_model_with_fallback(system_prompt: str, user_message: str) -> Tuple[str, str, List[str]]:
    """Call models with fallback logic."""
    errors = []
    
    for model_config in EVAL_MODEL_PRIORITY:
        provider = model_config["provider"]
        model = model_config["model"]
        
        print(f"Trying {provider} ({model})...")
        
        if provider == "openai":
            response, success = call_openai(system_prompt, user_message)
        elif provider == "gemini":
            response, success = call_gemini(system_prompt, user_message)
        elif provider == "anthropic":
            response, success = call_anthropic(system_prompt, user_message)
        else:
            errors.append(f"Unknown provider: {provider}")
            continue
        
        if success:
            print(f"Success with {provider} ({model})")
            return response, f"{provider}:{model}", errors
        else:
            error_msg = f"{provider} ({model}) failed: {response}"
            errors.append(error_msg)
            print(error_msg)
    
    # All models failed
    raise RuntimeError(f"All eval models failed. Errors: {errors}")


def parse_eval_response(response: str) -> Dict[str, Any]:
    """Parse the eval response JSON."""
    result = {
        "decision": "FAIL",
        "overall": 0,
        "scores": {
            "structure": 0,
            "selection": 0,
            "progression": 0,
            "spatial": 0,
        },
        "summary": "Could not parse eval response",
        "issues": [],
        "parse_error": None,
    }
    
    # Try to extract JSON from response
    try:
        # Find JSON object in response
        start_idx = response.find("{")
        end_idx = response.rfind("}") + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = response[start_idx:end_idx]
            parsed = json.loads(json_str)
            
            # Validate and set fields
            if "decision" in parsed:
                result["decision"] = parsed["decision"]
            if "overall" in parsed:
                result["overall"] = float(parsed["overall"])
            if "scores" in parsed:
                result["scores"] = parsed["scores"]
            if "summary" in parsed:
                result["summary"] = parsed["summary"]
            if "issues" in parsed:
                result["issues"] = parsed["issues"]
        else:
            result["parse_error"] = "Could not find JSON object in response"
    except json.JSONDecodeError as e:
        result["parse_error"] = f"JSON parse error: {e}"
    except Exception as e:
        result["parse_error"] = f"Parse error: {e}"
    
    return result


def evaluate_workout(
    workout_email: str,
    workout_json: Optional[Dict[str, Any]],
    date: str,
    day_of_week: str,
    day_type: str,
    past_workouts: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Evaluate a generated workout.
    
    Args:
        workout_email: Email format workout content
        workout_json: JSON format workout data
        date: Date string (YYYY-MM-DD)
        day_of_week: Day name
        day_type: Workout day type
        past_workouts: Optional past workout data
    
    Returns:
        Dict with decision, overall, scores, summary, issues, email_append
    """
    result = {
        "decision": "FAIL",
        "overall": 0,
        "scores": {
            "structure": 0,
            "selection": 0,
            "progression": 0,
            "spatial": 0,
        },
        "summary": "",
        "issues": [],
        "email_append": "",
        "model_used": "",
    }
    
    # Auto-fail checks
    if not workout_email:
        result["summary"] = "Missing email output"
        result["issues"].append("No email output generated")
        return result
    
    if not workout_json:
        result["summary"] = "Missing JSON output"
        result["issues"].append("No JSON output generated")
        return result
    
    if workout_json.get("date") != date:
        result["summary"] = f"Date mismatch: expected {date}, got {workout_json.get('date')}"
        result["issues"].append(result["summary"])
        return result
    
    if day_of_week.lower() == "friday":
        result["summary"] = "Friday is trainer day - no agent workouts"
        result["issues"].append(result["summary"])
        return result
    
    # Check for forbidden exercises (dips are discouraged but not auto-fail)
    forbidden = ["push-ups", "pushups", "front rack"]
    email_lower = workout_email.lower()
    for exercise in forbidden:
        if exercise in email_lower:
            result["summary"] = f"Forbidden exercise detected: {exercise}"
            result["issues"].append(f"Exercise '{exercise}' violates wrist injury constraint")
            return result
    
    # Note: Dips are discouraged but not auto-fail - the LLM eval will reduce selection score if dips are used
    
    # Load KB files
    try:
        kb_files = load_kb_files()
    except Exception as e:
        result["summary"] = f"KB loading error: {e}"
        return result
    
    # Load system prompt
    try:
        system_prompt = load_system_prompt()
    except Exception as e:
        result["summary"] = f"System prompt error: {e}"
        return result
    
    # Build user message
    user_message = build_user_message(
        workout_email=workout_email,
        workout_json=workout_json,
        date=date,
        day_of_week=day_of_week,
        day_type=day_type,
        kb_files=kb_files,
        past_workouts=past_workouts,
    )
    
    # Call model with fallback
    try:
        response, model_used, _ = call_model_with_fallback(system_prompt, user_message)
        result["model_used"] = model_used
    except RuntimeError as e:
        result["summary"] = str(e)
        return result
    
    # Parse response
    parsed = parse_eval_response(response)
    result.update(parsed)
    
    # Build email append
    result["email_append"] = format_eval_for_email(result)
    
    return result


def format_eval_for_email(eval_result: Dict[str, Any]) -> str:
    """Format eval results for email append."""
    parts = []
    parts.append("---")
    parts.append("")
    parts.append("## 📊 Workout Quality Check")
    parts.append("")
    parts.append(f"**Overall Score:** {eval_result.get('overall', 0):.1f}/5.0")
    parts.append("")
    parts.append("**Category Scores:**")
    scores = eval_result.get("scores", {})
    parts.append(f"- Structure: {scores.get('structure', 0)}/5")
    parts.append(f"- Selection: {scores.get('selection', 0)}/5")
    parts.append(f"- Progression: {scores.get('progression', 0)}/5")
    parts.append(f"- Spatial: {scores.get('spatial', 0)}/5")
    parts.append("")
    
    if eval_result.get("summary"):
        parts.append(f"**Summary:** {eval_result.get('summary')}")
        parts.append("")
    
    return "\n".join(parts)


def format_failed_attempts_for_email(attempts: List[Dict[str, Any]]) -> str:
    """Format multiple failed attempts for email."""
    parts = []
    parts.append("---")
    parts.append("")
    parts.append("## ⚠️ Eval Feedback (All Attempts)")
    parts.append("")
    parts.append("This workout did not pass quality check after 3 attempts.")
    parts.append("Review the feedback below and use your judgment.")
    parts.append("")
    
    for i, attempt in enumerate(attempts, 1):
        parts.append(f"### Attempt {i}")
        parts.append(f"- **Score:** {attempt.get('overall', 0)}/5")
        summary = attempt.get('summary', 'No summary')
        parts.append(f"- **Summary:** {summary}")
        issues = attempt.get('issues', [])
        if issues:
            parts.append("- **Issues:**")
            for issue in issues:
                parts.append(f"  - {issue}")
        parts.append("")
    
    return "\n".join(parts)
