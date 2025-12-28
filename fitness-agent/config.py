"""Configuration constants for Fitness Agent MVP"""
import os
from dotenv import load_dotenv

# Load .env file if it exists (override=True ensures .env values override shell env vars)
load_dotenv(override=True)

# Google Sheets Configuration
# Simple spreadsheet ID - swap out as needed for different months
# Minimal change approach: just update this constant when switching months
# Set via environment variable or update this constant
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "YOUR_SPREADSHEET_ID_HERE")

# Agent Configuration
MAX_EVAL_ATTEMPTS = 3

# Generator Model Priority (with fallback)
# Primary: Claude Opus 4.5 → Fallback 1: Gemini 1.5 Flash → Fallback 2: GPT 5.2
GENERATOR_MODEL_PRIORITY = [
    {"provider": "anthropic", "model": "claude-opus-4-5-20251101"},
    {"provider": "gemini", "model": "gemini-1.5-flash"},
    {"provider": "openai", "model": "gpt-5.2"},
]

# Eval Model Priority (with fallback)
# Primary: GPT 5.2 → Fallback 1: Gemini 1.5 Flash → Fallback 2: Claude Opus 4.5
EVAL_MODEL_PRIORITY = [
    {"provider": "openai", "model": "gpt-5.2"},
    {"provider": "gemini", "model": "gemini-1.5-flash"},
    {"provider": "anthropic", "model": "claude-opus-4-5-20251101"},
]

# API Keys (from environment variables)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Email Configuration
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

# Google Credentials (from environment variable)
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS")

# KB File Paths (pointing to kb/ directory)
KB_DIR = os.path.join(os.path.dirname(__file__), "kb")
KB_FILES = {
    "goals": os.path.join(KB_DIR, "goals.md"),
    "status": os.path.join(KB_DIR, "status.md"),
    "preferences": os.path.join(KB_DIR, "preferences.md"),
    "exercise_library": os.path.join(KB_DIR, "exercise_library.md"),
    "gym_layout": os.path.join(KB_DIR, "gym_layout.md"),
}

# Prompts directory
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")
GENERATOR_PROMPT = os.path.join(PROMPTS_DIR, "generator_prompt.md")
EVAL_PROMPT = os.path.join(PROMPTS_DIR, "eval_prompt.md")



