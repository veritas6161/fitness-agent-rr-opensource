"""
Generator Agent - Generates personalized daily workouts

Model fallback: Claude Opus 4.5 → Gemini 3.0 Fast → GPT 5.2
Outputs: Email format (rich) + JSON format (sheets logging template)
"""

import json
import os
from typing import Dict, Any, Optional, List, Tuple

from config import (
    GENERATOR_MODEL_PRIORITY,
    ANTHROPIC_API_KEY,
    OPENAI_API_KEY,
    GEMINI_API_KEY,
)


def load_kb_files() -> Dict[str, str]:
    """
    Load all KB files from the kb/ directory.
    
    Returns:
        Dict mapping KB name to file contents
    """
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
    """
    Load the generator system prompt.
    
    Returns:
        System prompt string
    """
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "generator_prompt.md")
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise RuntimeError(f"Generator prompt not found: {prompt_path}")
    except Exception as e:
        raise RuntimeError(f"Error loading generator prompt: {e}")


def build_user_message(
    date: str,
    day_of_week: str,
    day_type: str,
    kb_files: Dict[str, str],
    past_workouts: Optional[List[Dict[str, Any]]] = None,
    feedback: Optional[str] = None,
) -> str:
    """
    Build the user message with all context for workout generation.
    
    Args:
        date: Date string (YYYY-MM-DD)
        day_of_week: Day name (e.g., "Friday")
        day_type: Type of workout (e.g., "Lower Body Strength")
        kb_files: Dict of KB file contents
        past_workouts: Optional list of past workout data from Sheets
        feedback: Optional eval feedback for retry
    
    Returns:
        Formatted user message string
    """
    message_parts = []
    
    # Date and day type (system-provided, no hallucination)
    message_parts.append(f"## Today's Workout Request")
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
        for workout in past_workouts[:7]:  # Limit to last 7 for context size
            message_parts.append(f"### {workout.get('tab_name', 'Unknown')}")
            message_parts.append(f"Date: {workout.get('date', 'Unknown')}")
            if workout.get('data'):
                # Format workout data as simple table
                for row in workout['data'][:20]:  # Limit rows
                    message_parts.append(" | ".join(str(cell) for cell in row))
            message_parts.append("")
    else:
        message_parts.append("---")
        message_parts.append("## Previous Workouts")
        message_parts.append("*No previous workout data available. Use conservative weights for first session.*")
        message_parts.append("")
    
    # Eval feedback (if retry)
    if feedback:
        message_parts.append("---")
        message_parts.append("## Eval Feedback (Previous Attempt Failed)")
        message_parts.append(feedback)
        message_parts.append("")
        message_parts.append("**Please regenerate the workout addressing the above feedback.**")
        message_parts.append("")
    
    # Final instruction
    message_parts.append("---")
    message_parts.append("## Output Required")
    message_parts.append("Generate both outputs:")
    message_parts.append("1. **Email Output** - Full workout plan with pro tips, structure, guardrails")
    message_parts.append("2. **JSON Output** - Sheets logging template (Exercise + Set pre-filled, rest empty)")
    message_parts.append("")
    message_parts.append("Format your response with clear sections:")
    message_parts.append("```")
    message_parts.append("=== EMAIL OUTPUT ===")
    message_parts.append("[Full email workout here]")
    message_parts.append("")
    message_parts.append("=== JSON OUTPUT ===")
    message_parts.append("[JSON object here]")
    message_parts.append("```")
    
    return "\n".join(message_parts)


def call_anthropic(system_prompt: str, user_message: str) -> Tuple[str, bool]:
    """
    Call Anthropic Claude API.
    
    Returns:
        Tuple of (response_text, success)
    """
    if not ANTHROPIC_API_KEY:
        return "Anthropic API key not configured", False
    
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        response = client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=8000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        return response.content[0].text, True
        
    except Exception as e:
        return f"Anthropic API error: {e}", False


def call_gemini(system_prompt: str, user_message: str) -> Tuple[str, bool]:
    """
    Call Google Gemini API.
    
    Returns:
        Tuple of (response_text, success)
    """
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


def call_openai(system_prompt: str, user_message: str) -> Tuple[str, bool]:
    """
    Call OpenAI API.
    
    Returns:
        Tuple of (response_text, success)
    """
    if not OPENAI_API_KEY:
        return "OpenAI API key not configured", False
    
    try:
        import openai
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-5.2",
            max_completion_tokens=8000,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        
        return response.choices[0].message.content, True
        
    except Exception as e:
        return f"OpenAI API error: {e}", False


def call_model_with_fallback(system_prompt: str, user_message: str) -> Tuple[str, str, List[str]]:
    """
    Call models with fallback logic.
    
    Returns:
        Tuple of (response_text, model_used, errors)
    """
    errors = []
    
    for model_config in GENERATOR_MODEL_PRIORITY:
        provider = model_config["provider"]
        model = model_config["model"]
        
        print(f"Trying {provider} ({model})...")
        
        if provider == "anthropic":
            response, success = call_anthropic(system_prompt, user_message)
        elif provider == "gemini":
            response, success = call_gemini(system_prompt, user_message)
        elif provider == "openai":
            response, success = call_openai(system_prompt, user_message)
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
    raise RuntimeError(f"All generator models failed. Errors: {errors}")


def parse_outputs(response: str) -> Dict[str, Any]:
    """
    Parse the model response to extract email and JSON outputs.
    
    Returns:
        Dict with 'email' and 'json' keys
    """
    result = {
        "email": "",
        "json": None,
        "raw_response": response,
        "parse_errors": []
    }
    
    # Try to find EMAIL OUTPUT section
    if "=== EMAIL OUTPUT ===" in response:
        parts = response.split("=== EMAIL OUTPUT ===")
        if len(parts) > 1:
            email_part = parts[1]
            if "=== JSON OUTPUT ===" in email_part:
                email_part = email_part.split("=== JSON OUTPUT ===")[0]
            result["email"] = email_part.strip()
    else:
        # Fallback: treat everything before JSON as email
        if "=== JSON OUTPUT ===" in response:
            result["email"] = response.split("=== JSON OUTPUT ===")[0].strip()
        else:
            result["email"] = response
            result["parse_errors"].append("Could not find EMAIL OUTPUT section")
    
    # Try to find JSON OUTPUT section
    if "=== JSON OUTPUT ===" in response:
        json_part = response.split("=== JSON OUTPUT ===")[1]
        
        # Extract JSON from the text (find first { to last })
        try:
            start_idx = json_part.find("{")
            end_idx = json_part.rfind("}") + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = json_part[start_idx:end_idx]
                result["json"] = json.loads(json_str)
            else:
                result["parse_errors"].append("Could not find JSON object in JSON OUTPUT section")
        except json.JSONDecodeError as e:
            result["parse_errors"].append(f"JSON parse error: {e}")
    else:
        result["parse_errors"].append("Could not find JSON OUTPUT section")
    
    return result


def generate_workout(
    date: str,
    day_of_week: str,
    day_type: str,
    past_workouts: Optional[List[Dict[str, Any]]] = None,
    feedback: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a workout for the given date and day type.
    
    Args:
        date: Date string (YYYY-MM-DD) - provided by orchestrator
        day_of_week: Day name (e.g., "Friday") - provided by orchestrator
        day_type: Type of workout (e.g., "Lower Body Strength")
        past_workouts: Optional list of past workout data from Sheets
        feedback: Optional eval feedback for retry
    
    Returns:
        Dict with:
        - email: Rich email workout content
        - json: Sheets logging template
        - model_used: Which model generated the response
        - errors: Any errors encountered
    """
    result = {
        "date": date,
        "day_of_week": day_of_week,
        "day_type": day_type,
        "email": "",
        "json": None,
        "model_used": "",
        "errors": [],
        "kb_loaded": True,
        "past_workouts_loaded": past_workouts is not None and len(past_workouts) > 0,
    }
    
    # Load KB files
    try:
        kb_files = load_kb_files()
        if not any(kb_files.values()):
            result["errors"].append("Warning: No KB files loaded")
            result["kb_loaded"] = False
    except Exception as e:
        result["errors"].append(f"KB loading error: {e}")
        result["kb_loaded"] = False
        kb_files = {}
    
    # Load system prompt
    try:
        system_prompt = load_system_prompt()
    except Exception as e:
        result["errors"].append(f"System prompt error: {e}")
        raise
    
    # Build user message
    user_message = build_user_message(
        date=date,
        day_of_week=day_of_week,
        day_type=day_type,
        kb_files=kb_files,
        past_workouts=past_workouts,
        feedback=feedback,
    )
    
    # Call model with fallback
    try:
        response, model_used, model_errors = call_model_with_fallback(system_prompt, user_message)
        result["model_used"] = model_used
        result["errors"].extend(model_errors)
    except RuntimeError as e:
        result["errors"].append(str(e))
        raise
    
    # Parse outputs
    parsed = parse_outputs(response)
    result["email"] = parsed["email"]
    result["json"] = parsed["json"]
    result["errors"].extend(parsed["parse_errors"])
    
    # Validate JSON has required fields
    if result["json"]:
        required_fields = ["date", "day_type", "rows"]
        missing = [f for f in required_fields if f not in result["json"]]
        if missing:
            result["errors"].append(f"JSON missing required fields: {missing}")
        
        # Verify date matches (catch hallucination)
        if result["json"].get("date") != date:
            result["errors"].append(f"Date mismatch: expected {date}, got {result['json'].get('date')}")
    
    return result
