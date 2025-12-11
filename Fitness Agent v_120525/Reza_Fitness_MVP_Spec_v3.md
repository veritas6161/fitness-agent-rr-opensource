# Reza Fitness Ecosystem
MVP Technical Specification
Version 3.0 — December 2025
# Executive Summary
This document defines the MVP for an automated fitness programming system. The system generates personalized daily workouts using a two-agent architecture (Generator + Eval), enables quick logging at the gym, and creates a closed feedback loop where logged data informs future workout generation.
Core Value Proposition:
Remove daily decision fatigue from workout planning
Ensure workout quality through automated evaluation loop
Enable frictionless logging during workouts
Create intelligent progression based on actual performance data
## Target Goals
Short-Term (End of January 2026):
Reduce body fat from 20% → 17%
Preserve lean mass (127+ lbs)
Establish consistent 6-day workout adherence
Long-Term (2026):
Maintain body fat in 13-17% range year-round
Achieve visible abs
Complete 1-2 competitive events (Hyrox/Spartan/Tactical Fitness, Half Iron Man)
Fully automated fitness programming system running smoothly
# Current Implementation Status
✅ Completed:
Google Cloud project created: [project-name]
Service account configured with JSON credentials
Google Sheet created and shared with service account
Cloud Function deployed and tested
Verified: Function can read/write to Google Sheet
🔧 Working Resources:
Function URL: [cloud-function-url]
Sheet ID: [spreadsheet-id]
Sheet Name: Workout_December 2025
Region: us-west1 (Oregon)
⏳ Next Steps:
Build Generator Agent with system prompt
Build Eval Agent with system prompt
Create orchestrator with eval loop
Add email notification
Set up Cloud Scheduler (9 PM cron)

# System Architecture
## High-Level Flow
The system operates as a nightly automated loop with a Generator-Eval agent pattern that ensures workout quality before delivery.
┌─────────────────────────────────────────────────────────────────┐
│                    NIGHTLY CRON (9 PM)                          │
│                           ↓                                     │
│                  Cloud Function (Orchestrator)                  │
│                           ↓                                     │
│              ┌─────────────────────────┐                        │
│              │   Generator Agent       │ ←─────────────────┐    │
│              │   (Claude API call)     │                   │    │
│              └─────────────────────────┘                   │    │
│                           ↓                                │    │
│              ┌─────────────────────────┐                   │    │
│              │   Eval Agent            │                   │    │
│              │   (Claude API call)     │ ── FAIL ──────────┘    │
│              └─────────────────────────┘   + feedback           │
│                           ↓ PASS                                │
│              ┌─────────────────────────┐                        │
│              │   Log Eval Scores       │ → Sheet (eval tab)     │
│              └─────────────────────────┘                        │
│                           ↓                                     │
│              ┌─────────────────────────┐                        │
│              │   Output                │                        │
│              │   • Email notification  │                        │
│              │   • Google Sheet tab    │                        │
│              └─────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
## Infrastructure Stack


# Code Structure
All code is developed in Cursor, then deployed to Cloud Run Functions via ZIP upload or GitHub connection.
## Project Folder Structure
fitness-agent/
├── main.py                  # Entry point + orchestrator
├── generator_agent.py       # Generator agent logic
├── eval_agent.py            # Eval agent logic
├── sheets_client.py         # Google Sheets read/write
├── email_client.py          # Email notification
├── config.py                # Configuration constants
├── requirements.txt         # Python dependencies
└── prompts/                 # System prompts
├── generator_prompt.md  # Workout generation prompt
└── eval_prompt.md       # Evaluation prompt
## File Descriptions
### main.py — Orchestrator
The entry point for the Cloud Function. Handles the complete workflow:
Receive trigger from Cloud Scheduler
Load KB files and past workout data from Google Sheets
Call Generator Agent to create workout
Call Eval Agent to validate workout
If FAIL: Loop back to Generator with feedback (max 3 attempts)
If PASS: Log eval scores to Sheet
Create workout tab in Google Sheet
Send email notification with workout + sheet link
### generator_agent.py — Workout Generator
Calls Claude API with the generator system prompt. Inputs:
Knowledge base files (goals, preferences, weekly structure)
Exercise library with last weights
Gym layout constraints
Past workout logs (last 7-14 days)
Current day in weekly cycle
(Optional) Feedback from previous eval attempt
### eval_agent.py — Workout Evaluator
Calls Claude API with the eval system prompt. Evaluates the generated workout against:
Workout structure & preferences
Exercise selection quality
Progression & safety
Spatial efficiency
Returns: PASS/FAIL decision, scores per category, feedback for regeneration if failed.
### sheets_client.py — Google Sheets Helper
Handles all Google Sheets operations:
Read past workout logs
Read exercise library
Create new workout tab with pre-filled exercises
Log eval scores to evaluation history tab
### email_client.py — Email Notifications
Sends workout notification email with: workout summary, Google Sheet link, eval scores.
### config.py — Configuration
Central configuration file containing:
SPREADSHEET_ID
Email recipient
Max eval loop attempts
Claude model version

# Agent Specifications
## Generator Agent
Purpose: Generate a personalized daily workout based on knowledge base files, past performance data, and weekly structure.
Inputs:
Knowledge Base files (goals, preferences, performance patterns, weekly structure)
Exercise Library (available exercises with last weights)
Gym layout and spatial constraints
Day-specific workout templates
Past workout logs from Google Sheet (last 7-14 days)
Current day in weekly cycle
(If retry) Feedback from Eval Agent
Outputs:
Structured workout plan (JSON format)
Includes: exercises, sets, reps, weights, rest periods, notes
Example Key Rules:
Note: These are examples. Final key rules are defined in the system prompt and KB files.
Avoid exercises that irritate wrist (dips, pushups, front rack positions)
Prefer neutral grip variations where possible
Include exercises user loves (specified in KB)
Use Last Weight data for progression cues
Group exercises by gym floor/location for spatial efficiency
## Eval Agent
Purpose: Validate generated workout against goals, preferences, and evaluation criteria. Gate quality before delivery.
Inputs:
Generated workout from Generator Agent
Knowledge Base files (same as generator)
Evaluation framework criteria
Evaluation Categories:
Workout Structure & Preferences
Follows defined workout formula/structure
Includes exercises user loves
Clear structure: Warm-up → Blocks → Finisher
Exercise Selection Quality
Uses exercises from Exercise Library only
Uses Last Weight data appropriately
Proper sequencing (large → small, compound → isolation)
Progression & Safety
Includes progression cues
Respects injury constraints (e.g., wrist limitations)
Appropriate volume for the day
Spatial Efficiency
One block = one location
Minimized floor changes
Outputs:
PASS or FAIL decision
Score per evaluation category
Overall score
If FAIL: Specific feedback for regeneration
Action: If PASS → proceed to output. If FAIL → return feedback to Generator Agent for retry (max 3 attempts).

# Google Sheet Schema
## Sheet Structure
Daily Workout Tabs — One tab per workout day (e.g., "2025-12-07 Day 4 Upper")
Exercise Library Tab — Reference for available exercises with last weights
Eval History Tab — Logs eval scores for each generated workout
Summary Tab — Aggregated history, PRs, trends
## Daily Workout Tab Schema (One Row Per Set)

## Eval History Tab Schema


# Environment Variables
These must be set in Cloud Run → Edit & Deploy → Variables & Secrets

# Deployment Process
## Option A: ZIP Upload
Build and test code locally in Cursor
Zip the fitness-agent folder
Go to Cloud Run → generate-daily-workout → Edit & Deploy
Upload ZIP in Source section
Deploy
## Option B: GitHub Connection
Push code to GitHub repository
Go to Cloud Run → generate-daily-workout → Connect to Repo
Select repository and branch
Auto-deploys on push
# Cloud Scheduler Setup
After code is deployed and tested, set up the nightly trigger:
Go to Cloud Scheduler in Google Cloud Console
Create Job
Name: nightly-workout-generator
Frequency: 0 21 * * * (9 PM daily)
Timezone: America/Los_Angeles
Target: HTTP
URL: [cloud-function-url]
Method: GET
# Success Metrics
## System Success
Generates workout nightly at 9 PM without failure
Eval agent passes workouts on first or second attempt (avg < 2 attempts)
Email delivered within 5 minutes of trigger
Sheet tab created with correct pre-filled data
Eval scores logged for every workout
## Goal Alignment
Short-Term (End of January 2026):
Body fat: 20% → 17%
Lean mass: Preserve 127+ lbs
Workout adherence: 6/6 days
Long-Term (2026):
Body fat maintained 13-17%
Visible abs achieved
1-2 competitive events completed
— End of Specification —

| Component | Technology |
| --- | --- |
| Compute | Google Cloud Run Functions (Python 3.12) |
| Scheduler | Google Cloud Scheduler (cron: 0 21 * * *) |
| Database | Google Sheets (via Sheets API) |
| AI Engine | Anthropic Claude API (claude-sonnet-4-20250514) |
| Secrets | Environment variables in Cloud Run |
| Notifications | SendGrid or Gmail SMTP |


| Column | Type | Description |
| --- | --- | --- |
| Exercise | Text (pre-filled) | Exercise name + target |
| Set | Number (pre-filled) | Set number (1, 2, 3...) |
| Weight | Number (user input) | Weight lifted in lbs |
| Reps | Number (user input) | Reps completed |
| RIR | Number (optional) | Reps in Reserve (0-5) |
| Feel | Dropdown (optional) | 😎 Easy / 👍 Good / 😤 Hard / ❌ Failed |
| Notes | Text (optional) | Free text notes |


| Column | Description |
| --- | --- |
| Date | Workout date |
| Day Type | Day 3, Day 4, etc. |
| Structure Score | Score for workout structure & preferences |
| Selection Score | Score for exercise selection quality |
| Progression Score | Score for progression & safety |
| Spatial Score | Score for spatial efficiency |
| Overall Score | Combined overall score |
| Attempts | Number of generation attempts before pass |


| Variable | Description |
| --- | --- |
| GOOGLE_CREDENTIALS | Full JSON contents of service account key (already set) |
| ANTHROPIC_API_KEY | Anthropic API key for Claude calls |
| SENDGRID_API_KEY | SendGrid API key for email (optional) |
| EMAIL_RECIPIENT | Email address to receive workout notifications |
