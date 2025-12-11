"""Configuration constants for Fitness Agent MVP"""
import os

# Google Sheets Configuration
# Simple spreadsheet ID - swap out as needed for different months
# Minimal change approach: just update this constant when switching months
# Set via environment variable or update this constant
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "YOUR_SPREADSHEET_ID_HERE")

# Agent Configuration
MAX_EVAL_ATTEMPTS = 3
GENERATOR_MODEL = "claude-opus-4.5"  # Claude Opus 4.5
EVAL_MODEL_PROVIDER = os.environ.get("EVAL_MODEL_PROVIDER", "gpt")  # "gpt" or "gemini"

# API Keys (from environment variables)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Email Configuration
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

# Google Credentials (from environment variable)
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS")

# KB File Paths (pointing to old-base-files directory)
# Note: These are old/base files - will update later
KB_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "old-base-files")
KB_FILES = {
    "fitness_goals": os.path.join(KB_BASE_DIR, "Reza_Fitness_Goals.md"),
    "workout_script": os.path.join(KB_BASE_DIR, "Reza_Workout_Script_KB.md"),
    "performance_patterns": os.path.join(KB_BASE_DIR, "Reza_Performance_Patterns_KB.md"),
    "gym_layout": os.path.join(KB_BASE_DIR, "Reza_Gym_Layout_and_Rules.md"),
    "eval_framework": os.path.join(KB_BASE_DIR, "Reza_Evaluation_Framework.md"),
}

# Day-specific plan files
DAY_PLANS = {
    "Day 3": os.path.join(KB_BASE_DIR, "Day_3_Conditioning_Plans.md"),
    "Day 4": os.path.join(KB_BASE_DIR, "Day_4_Upper_Body_Plans.md"),
    "Day 5": os.path.join(KB_BASE_DIR, "Day_5_Lower_Body_Plans.md"),
    "Day 6": os.path.join(KB_BASE_DIR, "Day_6_Full_Body_Plans.md"),
}

# Exercise Library
EXERCISE_LIBRARY_CSV = os.path.join(KB_BASE_DIR, "Exercise_Library.csv")



