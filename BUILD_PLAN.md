# Fitness Agent MVP Build Plan (Updated)

## Overview
Build a two-agent system (Generator + Eval) that generates personalized daily workouts, validates quality, and logs to Google Sheets with email notifications. Build on existing Cloud Function foundation.

**Architecture Approach: Reusable Plumbing Pattern**
- **Generic/Reusable Components:** `main.py` (orchestrator), `sheets_client.py` (Google Sheets operations) - designed to work across multiple agents
- **Agent-Specific Components:** `config.py` (agent settings), agent modules (generator_agent.py, eval_agent.py), prompts
- **Input Flexibility:** HTTP endpoint handles multiple input sources (GET/POST, cron/manual/webhook)
- **Easy Replication:** Copy agent folder, update config.py with new spreadsheet_id, minimal changes needed

**Key Changes:**
- Generator Agent: Opus 4.5 → Gemini 3 → GPT 5.2 (with fallback)
- Eval Agent: GPT 5.2 → Gemini 3 → Claude Opus 4.5 (with fallback)
- KB files: Goals and Exercise Library (primary KB files)
- Simple spreadsheet ID: Single constant in config.py (easy swap for different months/agents)
- Eval storage: Eval scores stored below workout table in same daily workout tab
- Summary/Dashboard: Future enhancement (not in MVP)
- Error handling: Graceful degradation with error flags for partial failures

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
├── main.py                  # Generic orchestrator (reusable pattern) - handles GET/POST, cron/manual/webhook
├── generator_agent.py       # Agent-specific: Generator agent (Claude Opus 4.5)
├── eval_agent.py            # Agent-specific: Eval agent (GPT or Gemini - flexible)
├── sheets_client.py         # Generic/Reusable: Google Sheets operations (accepts spreadsheet_id parameter)
├── email_client.py          # Generic/Reusable: Email notifications
├── config.py                # Agent-specific: Configuration constants (spreadsheet_id, KB paths, etc.)
├── requirements.txt         # Python dependencies
└── prompts/
    ├── generator_prompt.md  # Agent-specific: Generator system prompt (will update)
    └── eval_prompt.md       # Agent-specific: Eval system prompt (will update)
```

**Architecture Notes:**
- **Reusable Components** (`main.py`, `sheets_client.py`, `email_client.py`): Designed to work across multiple agents with parameterization
- **Agent-Specific Components** (`config.py`, agent modules, prompts): Each agent has its own configuration and logic
- **Replication Pattern:** Copy entire `fitness-agent/` folder for new agent, update `config.py` with new spreadsheet_id and agent-specific settings

## Implementation Steps

> **Note:** Todo list moved to separate `TODO.md` file for easier tracking.

### 1. Project Setup + File Organization
- Create `fitness-agent/` directory structure
- Copy existing main.py to fitness-agent/
- Create prompts directory
- **Categorize and label old files** as "old/base" for reference
- Note: KB files will be updated later - don't use current versions yet

### 2. Configuration (config.py) - Agent-Specific
**Purpose:** Agent-specific settings. Each agent has its own config.py with its own spreadsheet_id and settings.

**Contents:**
- **SPREADSHEET_ID:** Simple constant (easy swap for different months/agents)
  - Set via environment variable `SPREADSHEET_ID` or update constant directly
  - Minimal change approach: just update this constant when switching months/agents
- MAX_EVAL_ATTEMPTS: 3
- **Generator Model Priority (with fallback):**
  - Primary: `claude-opus-4.5` (Claude Opus 4.5)
  - Fallback 1: `gemini-2.0-flash-exp` (Gemini 3)
  - Fallback 2: `gpt-5.2` (GPT 5.2)
- **Eval Model Priority (with fallback):**
  - Primary: `gpt-5.2` (GPT 5.2) - default
  - Fallback 1: `gemini-2.0-flash-exp` (Gemini 3)
  - Fallback 2: `claude-opus-4.5` (Claude Opus 4.5)
- Load environment variables: 
  - ANTHROPIC_API_KEY (for Generator/Eval fallback)
  - OPENAI_API_KEY (for Eval primary)
  - GEMINI_API_KEY (for Generator/Eval fallback)
  - EMAIL_RECIPIENT, SENDGRID_API_KEY
  - GOOGLE_CREDENTIALS (for Sheets API)
- KB file paths (agent-specific file locations)
- Agent-specific settings (model configs, eval criteria, etc.)

**Replication:** When creating new agent, copy config.py template and update spreadsheet_id and agent-specific paths.

### 3. Google Sheets Client (sheets_client.py) - Generic/Reusable
**Purpose:** Generic Google Sheets operations that work across all agents. All functions accept `spreadsheet_id` as parameter.

**Functions (All Generic/Reusable):**
- `read_data(service, spreadsheet_id, tab_name, range=None)` → Generic read function
- `write_data(service, spreadsheet_id, tab_name, data, range=None)` → Generic write function
- `create_tab(service, spreadsheet_id, tab_name, headers=None)` → Create new tab
- `read_exercise_library(service, spreadsheet_id, tab_name="Exercise Library")` → Read exercise library tab, return dict/list
- `read_past_workouts(service, spreadsheet_id, days=14, tab_prefix="Workout")` → Read last N days of workout tabs
- `create_workout_tab(service, spreadsheet_id, date, day_type, exercises, tab_headers)` → Create new workout tab with pre-filled rows
- `create_workout_tab_with_eval(service, spreadsheet_id, date, day_type, exercises, tab_headers, eval_scores, attempts)` → Create workout tab with eval scores below workout table in same tab

**Key Design Principles:**
- **Generic:** All functions accept `spreadsheet_id` as parameter (not hardcoded)
- **Reusable:** Works with any spreadsheet_id (fitness, nutrition, other agents)
- **Pattern:** Use existing `googleapiclient.discovery.build` pattern (not gspread)
- **Service Object:** Accept `service` object from main.py to reuse existing auth
- **Tab Names:** Accept tab names as parameters for flexibility

**Replication:** No changes needed when copying to new agent - works with any spreadsheet_id.

**Sheet Schema (Per Monthly Sheet):**
- Daily Workout Tab Structure:
  - **Workout Table (top):** Exercise | Set | Weight | Reps | RIR | Feel | Notes
  - **Eval Scores (below workout table):** Date | Day Type | Structure Score | Selection Score | Progression Score | Spatial Score | Overall Score | Attempts | Errors/Warnings
  - Each workout tab contains both workout data and eval scores in the same tab
- **Summary Dashboard:** Future enhancement (not in MVP)

### 4. Generator Agent (generator_agent.py)
**Function:** `generate_workout(day_type, kb_files, exercise_library, past_workouts, feedback=None)`

**Inputs:**
- **Primary KB Files:** Goals and Exercise Library (essential KB files)
- Load KB files (Goals and Exercise Library) as text from file system
  - **Note:** Current files are old/base versions - will update during build process
- Exercise library with last weights (from Exercise Library CSV/Sheet)
- Past workout logs (last 7-14 days) - loaded from Sheets
- Optional: Eval feedback for retries

**Process:**
- **Model Priority (with fallback):** Opus 4.5 → Gemini 3 → GPT 5.2
- Call API with generator_prompt.md as system prompt
- Load KB files (Goals and Exercise Library) as text from file system
- Load previous workouts from Sheets (if available)
- Pass KB file contents + previous workouts to API as context/messages
- Request structured JSON output

**Input Handling & Error Resilience:**
- **System Prompt:** Must be available (failure not expected)
- **KB Files (Goals + Exercise Library):** Must be available (failure not expected, but handle gracefully if it occurs)
- **Previous Workouts:** May fail (most likely failure point)
  - If previous workouts fail to load, agent can still generate output
  - Mark output as generated with error: "Could not access previous workouts"
  - Include error flag in eval scores/output

**KB File Access:**
- KB files are separate markdown/text files stored in the project directory
- Primary KB files: Goals and Exercise Library
- They are loaded as text content using Python file I/O
- The text content is then passed to API as part of the message context
- This allows the agent to reference the KB content when generating workouts

**Output:** JSON workout with exercises, sets, reps, weights, rest periods, location flow, notes + error flags if any inputs failed

### 5. Eval Agent (eval_agent.py)
**Function:** `evaluate_workout(workout_json, kb_files, eval_framework, model_provider="gpt")`

**Inputs:**
- Generated workout JSON
- KB files (same as generator)
- Reza_Evaluation_Framework.md (updated version - not current)

**Model Priority (with fallback):**
- Primary: GPT 5.2 (default)
- Fallback 1: Gemini 3
- Fallback 2: Claude Opus 4.5
- Handle errors gracefully - if primary fails, try fallbacks in order

**Process:**
- Call API with eval_prompt.md as system prompt
- Evaluate against categories (criteria TBD - will define during build):
  1. Workout Structure & Preferences
  2. Exercise Selection Quality
  3. Progression & Safety
  4. Spatial Efficiency
- **Note:** Eval criteria will be defined step by step during build - not using current Reza_Evaluation_Framework.md yet
- **Note:** It's okay to use same model for both generator and eval if fallbacks align (handle errors appropriately)

**Output:** 
- PASS/FAIL decision
- Scores per category (0-5 or 0-6 scale - TBD)
- Overall score
- Feedback string (if FAIL)

**Note:** The above eval criteria are EXAMPLES only. Final eval criteria will be defined when we build the eval agent.

### 6. Email Client (email_client.py) - Generic/Reusable
**Purpose:** Generic email notification system usable across agents.

**Functions:**
- `send_email(recipient, subject, body, sheet_link=None)` → Generic email function
- `send_workout_email(workout_summary, sheet_link, eval_scores, recipient)` → Agent-specific wrapper (fitness agent)

**Options:**
- SendGrid API (preferred)
- Gmail SMTP fallback
- Include: summary, Google Sheet link, scores/metadata

**Replication:** Generic function works for any agent, agent-specific wrappers can be added per agent.

### 7. Main Orchestrator (main.py) - Generic/Reusable Pattern
**Purpose:** Generic orchestrator that handles multiple input sources and coordinates agent workflow. Reusable across agents.

**Existing Code:** Basic Cloud Function with Google Sheets auth already working

**Update to:** Generic orchestrator pattern with input flexibility

**Input Handling (Multiple Sources):**
- **GET Request (Cron/Manual):**
  - Cron trigger: No parameters (uses config defaults)
  - Manual trigger: Query parameters (e.g., `?day_type=Day4`, `?trigger=manual`)
- **POST Request (Webhooks):**
  - Chat/Text/Email webhooks: JSON body with `source`, `message`, `metadata`
  - Example: `{"source": "chat", "message": "generate workout", "day_type": "Day 4"}`

**Workflow (Generic Pattern):**
1. **Parse Request:** Determine input source and extract parameters
   - GET: Read query parameters
   - POST: Parse JSON body
2. **Initialize Sheets Service:** Google Sheets auth (reuse existing pattern)
   - Load credentials from environment
   - Build service object
3. **Load Configuration:** Import agent-specific config (spreadsheet_id, KB paths, etc.)
4. **Agent-Specific Orchestration:** (This part is agent-specific, called from generic orchestrator)
   - Determine workflow parameters (day_type, date, etc.)
   - Load KB files from file system (Goals + Exercise Library from config)
   - Load previous workouts from Sheets using sheets_client.py (with spreadsheet_id from config)
     - **Error Handling:** If previous workouts fail to load, continue with error flag
   - **Eval Loop (max 3 attempts):**
     - Call Generator Agent (agent-specific) with model fallback logic
       - Try Opus 4.5 → Gemini 3 → GPT 5.2
     - Call Eval Agent (agent-specific) with model fallback logic
       - Try GPT 5.2 → Gemini 3 → Claude Opus 4.5
     - If FAIL: retry with feedback
     - If PASS: break
   - Create workout tab with eval scores (workout table + eval scores below in same tab)
   - Send email notification
5. **Return Response:** Success/error response

**Error Handling:**
- **Model API Failures:** Implement fallback logic for both Generator and Eval agents
- **Input Failures:** 
  - System prompt: Should not fail (but handle if it does)
  - KB files: Should not fail (but handle gracefully if it does)
  - Previous workouts: Most likely to fail - continue generation with error flag
- **Eval Loop Failures:** If all 3 attempts fail, log error, notify user
- **Sheets API Failures:** Retry logic with exponential backoff
- **Email Failures:** Retry logic, fallback to Gmail SMTP
- Comprehensive logging for debugging
- Graceful degradation - partial outputs with error flags rather than complete failures

**Replication Pattern:**
- Generic structure stays the same
- Agent-specific logic isolated in agent modules
- Config loaded from agent-specific config.py
- All Sheets operations use sheets_client.py with spreadsheet_id from config

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
- Test multiple input methods (GET with query params, POST with JSON body)
- Verify Google Sheets integration (already working)
- Test model fallback logic:
  - Generator: Opus 4.5 → Gemini 3 → GPT 5.2
  - Eval: GPT 5.2 → Gemini 3 → Claude Opus 4.5
- Test error handling scenarios:
  - Previous workouts fail to load (should still generate with error flag)
  - KB files fail (should handle gracefully)
  - Model API failures (should use fallbacks)
- Test workout tab creation with eval scores below workout table
- Deploy to Cloud Run via ZIP upload
- Set environment variables in Cloud Run:
  - ANTHROPIC_API_KEY (Generator primary, Eval fallback)
  - OPENAI_API_KEY (Eval primary)
  - GEMINI_API_KEY (Generator/Eval fallback)
  - EMAIL_RECIPIENT, SENDGRID_API_KEY
  - SPREADSHEET_ID (optional - can be in config.py instead)
  - GOOGLE_CREDENTIALS (service account JSON)
- Configure Cloud Scheduler (9 PM PST daily) - calls endpoint via GET request
- Test manual trigger: `GET [function-url]?trigger=manual&day_type=Day4`
- Test webhook trigger: `POST [function-url]` with JSON body

## Reusable Architecture Pattern

**Design Philosophy:**
This architecture is designed to be reusable across multiple agents. The pattern separates generic/reusable plumbing from agent-specific logic.

**Generic/Reusable Components:**
- `main.py` - Generic orchestrator pattern (handles GET/POST, input parsing, workflow coordination)
- `sheets_client.py` - Generic Google Sheets operations (all functions accept spreadsheet_id parameter)
- `email_client.py` - Generic email notification functions

**Agent-Specific Components:**
- `config.py` - Agent-specific settings (spreadsheet_id, KB paths, model configs)
- `generator_agent.py` - Agent-specific generation logic
- `eval_agent.py` - Agent-specific evaluation logic
- `prompts/` - Agent-specific system prompts

**Replication Pattern for New Agents:**
1. Copy entire `fitness-agent/` folder to `[new-agent]-agent/`
2. Update `config.py` with new agent's spreadsheet_id and settings
3. Replace agent-specific modules (generator_agent.py, eval_agent.py, prompts) with new agent logic
4. Generic components (main.py, sheets_client.py, email_client.py) work as-is

**Benefits:**
- Minimal code changes when creating new agents
- Consistent patterns across all agents
- Easy to maintain and update shared functionality
- Simple copy-paste workflow

## Key Implementation Details

**Day Type Determination:**
- Track last workout day in Sheets or config
- Cycle through Day 1-7 (flexible, not consecutive calendar days)
- Day 1 (Trainer) usually Friday, but adaptable

**KB File Loading:**
- Current KB files are old/base versions
- Don't use in code yet - will update prompts and KB files step by step
- Reference from parent directory: `../Reza_Fitness_Goals.md`

**Spreadsheet ID Management:**
- Simple constant in config.py (easy swap approach)
- Each agent has its own spreadsheet_id in its config.py
- When switching months: update SPREADSHEET_ID constant in config.py
- When creating new agent: copy config.py, update SPREADSHEET_ID

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
   - **Selected:** Eval scores stored below workout table in same daily workout tab
   - Each workout tab contains: Workout table (top) + Eval scores (below)
   - Structure: Workout data first, then eval scores in same tab

2. **Summary/Dashboard Implementation:**
   - **Status:** Future enhancement (not in MVP)
   - Will implement later after MVP is working

3. **Eval Criteria:**
   - Will define step by step during build process
   - Current Reza_Evaluation_Framework.md is base/reference only
   - Categories and scoring will be determined during implementation

4. **KB Files:**
   - **Primary KB files:** Goals and Exercise Library (essential for generation)
   - Current KB files are old/base versions (will update during build)
   - Will update prompts and KB files step by step during build

5. **Model Fallback Logic:**
   - Generator: Opus 4.5 → Gemini 3 → GPT 5.2
   - Eval: GPT 5.2 → Gemini 3 → Claude Opus 4.5
   - Error handling for each fallback step required

## Success Criteria
- Generates workout nightly at 9 PM
- Eval passes on first or second attempt (avg < 2)
- Email delivered within 5 minutes
- Sheet tab created with correct data (workout table + eval scores below)
- Eval scores included in workout tab for every workout
- Error flags included when inputs fail (e.g., previous workouts)
- Model fallback logic works correctly for both Generator and Eval agents

