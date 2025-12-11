# Fitness Agent MVP Build Plan (Updated)

## Overview
Build a two-agent system (Generator + Eval) that generates personalized daily workouts, validates quality, and logs to Google Sheets with email notifications. Build on existing Cloud Function foundation.

**Key Changes:**
- Generator Agent: Claude Opus 4 (not Sonnet 4)
- Eval Agent: GPT or Gemini (flexible, not Claude vs Claude)
- KB files: Current versions are old/base - will update later, don't use yet
- Monthly sheet rotation: Support December, January, etc. (dynamic file selection)
- Eval storage: Separate tab or separate file (TBD)
- Summary/Dashboard: Visualizations by day and exercise type in Summary tab

## Current Status
✅ Google Cloud Function deployed and tested
✅ Google Sheets authentication working
✅ Basic connection verified
✅ Existing requirements.txt: functions-framework==3.*, google-auth==2.23.0, google-api-python-client==2.108.0
⏳ Need to categorize old files
⏳ Need to build: Generator Agent, Eval Agent, orchestrator logic, email, prompts

## File Organization

### Step 1: Categorize Old/Base Files
**Old/Base Files (Previous Iteration):**
- `Fitness_Agent_System_Prompt.md` - Base for generator prompt (will update)
- `Reza_Evaluation_Framework.md` - Base for eval prompt (will update)
- `Reza_Fitness_Goals.md` - Old KB file (will update)
- `Reza_Workout_Script_KB.md` - Old KB file (will update)
- `Reza_Performance_Patterns_KB.md` - Old KB file (will update)
- `Reza_Gym_Layout_and_Rules.md` - Old KB file (will update)
- `Day_3_Conditioning_Plans.md` - Old workout plans (will update)
- `Day_4_Upper_Body_Plans.md` - Old workout plans (will update)
- `Day_5_Lower_Body_Plans.md` - Old workout plans (will update)
- `Day_6_Full_Body_Plans.md` - Old workout plans (will update)
- `Exercise_Library.csv` - Old exercise library (will update)

**Action:** Label these as reference/base materials. Don't use in code yet - will update step by step.

## Project Structure
```
fitness-agent/
├── main.py                  # Cloud Function entry (update existing)
├── generator_agent.py       # Generator agent (Claude Opus 4)
├── eval_agent.py            # Eval agent (GPT or Gemini - flexible)
├── sheets_client.py         # Google Sheets operations
├── email_client.py          # Email notifications
├── config.py                # Configuration constants
├── requirements.txt         # Python dependencies
└── prompts/
    ├── generator_prompt.md  # Generator system prompt (will update)
    └── eval_prompt.md       # Eval system prompt (will update)
```

## Implementation Steps

### 1. Project Setup + File Organization
- Create `fitness-agent/` directory structure
- Copy existing main.py to fitness-agent/
- Create prompts directory
- **Categorize and label old files** as "old/base" for reference
- Note: KB files will be updated later - don't use current versions yet

### 2. Configuration (config.py)
- **Monthly Sheet Support:** Simple SPREADSHEET_ID swap (minimal change approach)
  - Set via environment variable `SPREADSHEET_ID` or update constant in config.py
  - Will swap out file as needed (no complex dynamic logic)
  - Single SPREADSHEET_ID constant that can be easily changed
- MAX_EVAL_ATTEMPTS: 3
- GENERATOR_MODEL: `claude-opus-4.5` (Claude Opus 4.5, not Sonnet)
- EVAL_MODEL: Configurable (GPT or Gemini - set via env var)
- EVAL_MODEL_PROVIDER: "gpt" or "gemini" (env var)
- Load environment variables: 
  - ANTHROPIC_API_KEY (for Generator)
  - OPENAI_API_KEY or GEMINI_API_KEY (for Eval - flexible)
  - EMAIL_RECIPIENT, SENDGRID_API_KEY
- KB file paths (reference old files, but note: will be updated later - don't use yet)

### 3. Google Sheets Client (sheets_client.py)
**Functions:**
- `get_spreadsheet_id_for_month(year, month)` → Return spreadsheet ID for given month
- `read_exercise_library(service, spreadsheet_id)` → Read Exercise Library tab, return dict/list
- `read_past_workouts(service, spreadsheet_id, days=14)` → Read last 7-14 days of workout tabs (can span multiple monthly sheets)
- `create_workout_tab(service, spreadsheet_id, date, day_type, exercises)` → Create new tab with pre-filled exercise rows
- `log_eval_scores(service, spreadsheet_id, date, day_type, scores, attempts)` → Write to Eval History tab
  - **Question:** Same sheet or separate eval file? (TBD - need user decision)
- `update_summary_dashboard(service, spreadsheet_id)` → Update Summary tab with visualizations/aggregated data
  - Visualizations by day type (Day 3, Day 4, Day 5, Day 6)
  - Visualizations by exercise type/category
  - Performance trends
  - PR tracking
- **Note:** Use existing `googleapiclient.discovery.build` pattern from main.py (not gspread)
- Accept `service` object from main.py to reuse existing auth

**Sheet Schema (Per Monthly Sheet):**
- Daily Workout Tab: Exercise | Set | Weight | Reps | RIR | Feel | Notes
- Eval History Tab: Date | Day Type | Structure Score | Selection Score | Progression Score | Spatial Score | Overall Score | Attempts
- **Summary Tab:** Aggregated data, visualizations by:
  - Day type (Day 3, Day 4, Day 5, Day 6)
  - Exercise type/category
  - Performance trends
  - PR tracking
  - (Dashboard visualizations - may require Google Sheets charts or separate reporting)

### 4. Generator Agent (generator_agent.py)
**Function:** `generate_workout(day_type, kb_files, exercise_library, past_workouts, feedback=None)`

**Inputs:**
- Load KB files: Reza_Fitness_Goals.md, Reza_Workout_Script_KB.md, Reza_Performance_Patterns_KB.md, Reza_Gym_Layout_and_Rules.md
  - **Note:** These are old/base files - will update later
- Load day-specific plan (Day_3_Conditioning_Plans.md, etc.) - old/base
- Exercise library with last weights
- Past workout logs (last 7-14 days)
- Optional: Eval feedback for retries

**Process:**
- Call Claude Opus 4.5 API with generator_prompt.md as system prompt
- Load KB files as text from file system (they are separate source files)
- Pass KB file contents to Claude API as context/messages (not as separate file uploads)
- Request structured JSON output

**KB File Access:**
- KB files are separate markdown/text files stored in the project directory
- They are loaded as text content using Python file I/O
- The text content is then passed to Claude API as part of the message context
- This allows the agent to reference the KB content when generating workouts

**Output:** JSON workout with exercises, sets, reps, weights, rest periods, location flow, notes

### 5. Eval Agent (eval_agent.py)
**Function:** `evaluate_workout(workout_json, kb_files, eval_framework, model_provider="gpt")`

**Inputs:**
- Generated workout JSON
- KB files (same as generator)
- Reza_Evaluation_Framework.md (updated version - not current)

**Model Flexibility:**
- Support multiple providers: GPT (OpenAI) or Gemini (Google)
- Set via EVAL_MODEL_PROVIDER env var: "gpt" or "gemini"
- Use appropriate API client based on provider

**Process:**
- Call selected API (GPT or Gemini) with eval_prompt.md as system prompt
- Evaluate against 4 categories (criteria TBD - will define with user):
  1. Workout Structure & Preferences (target: 5-6/6)
  2. Exercise Selection Quality (target: 5/5)
  3. Progression & Safety (target: 3-4/4)
  4. Spatial Efficiency (target: 3-4/4)
- **Note:** Eval criteria will be defined as we iterate - not using current Reza_Evaluation_Framework.md yet

**Output:** 
- PASS/FAIL decision
- Scores per category (0-5 or 0-6 scale - TBD)
- Overall score
- Feedback string (if FAIL)

**Note:** The above eval criteria are EXAMPLES only. Final eval criteria will be defined when we build the eval agent.

### 6. Email Client (email_client.py)
**Function:** `send_workout_email(workout_summary, sheet_link, eval_scores)`

**Options:**
- SendGrid API (preferred)
- Gmail SMTP fallback
- Include: workout summary, Google Sheet link, eval scores

### 7. Main Orchestrator (main.py)
**Existing Code:** Basic Cloud Function with Google Sheets auth already working

**Update to:** Keep `@functions_framework.http` decorator, keep function name `generate_workout`

**Workflow:**
1. Keep existing Google Sheets auth setup (already working)
2. Determine current day in weekly cycle (Day 1-7, flexible scheduling)
3. Load KB files from file system (reference from parent directory or absolute paths)
   - **Note:** Old/base files - will update later
5. Load exercise library from Sheets (Exercise Library tab)
6. Load past workout logs (last 7-14 days from workout tabs, may span multiple monthly sheets)
7. **Eval Loop (max 3 attempts):**
   - Call Generator Agent (Claude Opus 4.5)
   - Call Eval Agent (GPT or Gemini)
   - If FAIL: retry with feedback
   - If PASS: break
8. Log eval scores to Sheets (Eval History tab - location TBD)
9. Create workout tab in Sheets with pre-filled exercises
10. Update Summary dashboard (if exists)
11. Send email notification
12. Return success response

**Error Handling:**
- Keep existing error handling pattern
- Retry logic for API failures
- Logging for debugging
- Graceful degradation

### 8. System Prompts
**prompts/generator_prompt.md:**
- Use existing `Fitness_Agent_System_Prompt.md` as base
- Format for Claude Opus 4 API system message
- Include all KB file references
- **Note:** Will update as we iterate

**prompts/eval_prompt.md:**
- Base on `Reza_Evaluation_Framework.md` (old/base)
- Define 4 evaluation categories with scoring criteria
- Output format: JSON with PASS/FAIL, scores, feedback
- **Note:** Will update as we iterate

### 9. Dependencies (requirements.txt)
```
functions-framework==3.*
google-auth==2.23.0
google-api-python-client==2.108.0
anthropic>=0.34.0
openai>=1.0.0  # For GPT eval agent
google-generativeai>=0.3.0  # For Gemini eval agent (optional)
sendgrid>=6.10.0
python-dotenv>=1.0.0
```
**Note:** Keep existing versions exactly as specified. Add OpenAI and optional Gemini support for eval agent.

### 10. Testing & Deployment
- Test locally with mock data
- Verify Google Sheets integration (already working)
- Test Claude Opus 4 API calls (Generator)
- Test GPT/Gemini API calls (Eval)
- Deploy to Cloud Run via ZIP upload
- Set environment variables in Cloud Run:
  - ANTHROPIC_API_KEY (Generator)
  - OPENAI_API_KEY or GEMINI_API_KEY (Eval)
  - EVAL_MODEL_PROVIDER ("gpt" or "gemini")
  - EMAIL_RECIPIENT, SENDGRID_API_KEY
- Configure Cloud Scheduler (9 PM PST daily)

## Key Implementation Details

**Day Type Determination:**
- Track last workout day in Sheets or config
- Cycle through Day 1-7 (flexible, not consecutive calendar days)
- Day 1 (Trainer) usually Friday, but adaptable

**KB File Loading:**
- Current KB files are old/base versions
- Don't use in code yet - will update prompts and KB files step by step
- Reference from parent directory: `../Reza_Fitness_Goals.md`

**Monthly Sheet Rotation:**
- Determine month from current date
- Map to spreadsheet ID in config
- Support multiple monthly sheets (December, January, etc.)
- Past workout queries may need to span multiple sheets

**Workout JSON Schema:**
```json
{
  "date": "2025-12-07",
  "day_type": "Day 4",
  "overview": {...},
  "warmup": [...],
  "blocks": [
    {
      "name": "Block A",
      "location": "Floor 2",
      "exercises": [...]
    }
  ],
  "finisher": [...]
}
```

**Eval Output Schema:**
```json
{
  "pass": true/false,
  "scores": {
    "structure": 5,
    "selection": 5,
    "progression": 4,
    "spatial": 4
  },
  "overall": 4.5,
  "feedback": "..." // if fail
}
```

## Open Questions / Decisions Needed

1. **Eval Storage Location:**
   - **Selected: Option A** - Eval History tab in same monthly sheet (e.g., December sheet has eval history)
   - Option B: Separate "Eval History" sheet that spans all months
   - Option C: Eval tab in each monthly sheet + master eval sheet

2. **Summary/Dashboard Implementation:**
   - **Selected: Option B** - Master Summary sheet that pulls from all monthly sheets
   - Master database table for future reference
   - Option A: Summary tab in each monthly sheet with charts/visualizations
   - Option C: Both - monthly summary + master summary
   - **Technical:** Google Sheets native charts vs. external dashboard (TBD)

3. **Eval Criteria:**
   - Need to define final eval categories and scoring (0-5? 0-6?)
   - Current Reza_Evaluation_Framework.md is base/reference only
   - Will update as we iterate

4. **KB Files:**
   - Current KB files are old/base versions
   - Don't use in code yet - will update prompts and KB files step by step

## Success Criteria
- Generates workout nightly at 9 PM
- Eval passes on first or second attempt (avg < 2)
- Email delivered within 5 minutes
- Sheet tab created with correct data
- Eval scores logged for every workout
- Monthly sheet rotation works correctly
- Summary dashboard updates with workout data

