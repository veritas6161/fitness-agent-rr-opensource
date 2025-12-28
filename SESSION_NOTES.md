# Fitness Agent - Session Notes

This document captures all architecture decisions, rules, and context from the initial build session. Use this as reference for continuing development.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    NIGHTLY CRON (9 PM PST)                      │
│                           ↓                                     │
│                  main.py (Orchestrator)                         │
│                           ↓                                     │
│              ┌─────────────────────────┐                        │
│              │   Generator Agent       │ ←─────────────────┐    │
│              │   (Opus 4.5→Gemini→GPT) │                   │    │
│              └─────────────────────────┘                   │    │
│                           ↓                                │    │
│                  Workout (email + JSON)                    │    │
│                           ↓                                │    │
│              ┌─────────────────────────┐                   │    │
│              │   Eval Agent            │                   │    │
│              │   (GPT→Gemini→Opus)     │ ── FAIL ──────────┘    │
│              └─────────────────────────┘   + feedback           │
│                           ↓ PASS                                │
│              ┌─────────────────────────┐                        │
│              │   Output                │                        │
│              │   • Email (workout+eval)│                        │
│              │   • Sheets (JSON log)   │                        │
│              └─────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Model Fallback Order

| Agent | Priority 1 | Priority 2 | Priority 3 |
|-------|------------|------------|------------|
| **Generator** | claude-opus-4-5-20251101 | gemini-1.5-flash | gpt-5.2 |
| **Eval** | gpt-5.2 | gemini-1.5-flash | claude-opus-4-5-20251101 |

Different order ensures different model evaluates than generates.

---

## Output Formats

### Email Output (Instructions for user)
- Full workout plan with pro tips
- Warm-up → Blocks → Cooldown structure
- Location flow, exercise notes
- Eval scores appended at bottom

### JSON Output (Sheets logging template)
- Pre-filled: Exercise name, Set number
- Empty (user fills): Weight, Reps, RIR, Feel, Notes
- Tab name: `Workout_YYYY-MM-DD`

**Key:** Eval scores go in EMAIL only, NOT in Sheets.

---

## Key Rules

### Friday = Trainer Day
- Agent does NOT generate Friday workouts
- Trainer handles full body + form work
- Agent generates for Sat-Thu only

### Smart-Adapt Policy (Missed Workouts)
| Situation | Action |
|-----------|--------|
| 1 missed workout | Shift to next available day |
| 2+ misses in week | Prioritize under-hit muscle groups, enforce 48h rule |

**What counts as "missed":** No tab exists OR <50% sets logged

### Hard Rules
- **48h recovery:** No same primary muscle within 48 hours
- **Max consecutive hard days:** 2 (14+ strain) before recovery day
- **Missing weight data:** Use conservative "first session" weight (RPE 6-7)

### Injury Constraints
| Issue | Avoid | Use Instead |
|-------|-------|-------------|
| Right wrist (tendon) | Dips, push-ups, front rack | Neutral grips, DBs, machines |
| Right knee (patella) | High-impact plyos if flaring | Monitor, reduce if pain |
| Lower back | Poor burpee form, excessive hinge | Proper form, reasonable volume |

---

## Weekly Targets

| Metric | Target |
|--------|--------|
| Zone 2 time | 3 hours/week |
| Zone 4-5 (VO2 max) | 1 hour/week |
| Sets per major muscle | 12+/10 days (rolling window) |
| Muscle group frequency | 2x/week |
| Training days | 6-7 days |

## Muscle Balance Feature

The Generator analyzes the last 10-14 days of workouts to check set counts per muscle group. If any group is under-hit (<12 sets), the workout:
1. Includes exercises for that muscle group (unless 48h rule prevents)
2. Adds a "📊 Muscle Balance Analysis" callout at the top of the email

The Eval awards +0.5 bonus for addressing gaps, or -0.5 penalty for ignoring them.

---

## Eval Scoring

| Category | What It Checks |
|----------|----------------|
| Structure (0-5) | Warm-up → Blocks → Cooldown, day type match |
| Selection (0-5) | From library, no forbidden exercises, proper sequence |
| Progression (0-5) | References previous weights, respects constraints |
| Spatial (0-5) | One block = one location, minimal transitions |
| Muscle Balance | +0.5 bonus for addressing gaps, -0.5 for ignoring |

**Pass Threshold:** Overall ≥ 4.0 = PASS, 3.0-3.9 = PASS with note, <3.0 = FAIL

**Bonuses:**
- +0.5 for triathlon/Ironman-relevant progression notes
- +0.5 for addressing under-hit muscle group with callout

**Auto-Fail:** Forbidden exercise, date mismatch, Friday workout, missing output

### 3 Failed Evals
- Send best attempt with WARNING banner
- Include all 3 attempts' feedback
- User uses judgment

---

## File Structure

```
fitness-agent/
├── main.py                  # ✅ Full orchestrator with eval loop
├── generator_agent.py       # ✅ Model fallback (Opus → Gemini → GPT)
├── eval_agent.py            # ✅ Model fallback (GPT → Gemini → Opus)
├── sheets_client.py         # ✅ Generic/reusable
├── email_client.py          # ✅ SendGrid with markdown→HTML
├── config.py                # ✅ Model priorities, paths, settings (loads from .env)
├── requirements.txt         # ✅ All dependencies
├── test_keys.py             # ✅ Utility to verify API keys work
├── .env                     # 🔒 API keys (gitignored, create manually)
├── .gitignore               # ✅ Excludes .env and sensitive files
├── kb/
│   ├── goals.md             # ✅ Ironman 70.3, weekly targets
│   ├── status.md            # ✅ Body comp, training setup, Friday trainer
│   ├── preferences.md       # ✅ Loves/dislikes, injury constraints
│   ├── exercise_library.md  # ✅ Exercises by movement (no hardcoded weights)
│   └── gym_layout.md        # ✅ Floor layout, design rules
└── prompts/
    ├── generator_prompt.md  # ✅ Programming rules, output formats, muscle balance
    └── eval_prompt.md       # ✅ Scoring rubric, auto-fail, balance bonus
```

### Graceful Degradation
- **No Sheets credentials?** Skips sheets read/write, continues with Generator + Eval
- **No email credentials?** Logs error but still writes to Sheets
- **All models fail?** Returns best attempt after 3 tries with warning

---

## Primary Goal

**Ironman 70.3 Oceanside — March 2027**

The agent should proactively:
- Suggest swim/bike/run work
- Identify training gaps
- Build aerobic base alongside strength
- Flag if weekly Zone 2/VO2 max targets aren't being met

---

## Remaining TODO

| Step | Task | Status |
|------|------|--------|
| 10 | Build email_client.py | ✅ Done |
| 11 | Build main.py orchestrator | ✅ Done |
| 12 | Create requirements.txt | ✅ Done |
| 13 | Test locally | ✅ Complete (working with Claude Opus 4.5 + GPT 5.2) |
| 14 | Deploy to Cloud Run | ⏳ Pending |
| 15 | Set up Cloud Scheduler (9 PM) | ⏳ Pending |

### Testing Commands
```bash
cd "/Users/rezaridwan/Downloads/Fitness Agent/fitness-agent"

# Test API keys individually
python3 test_keys.py

# Run full workflow
python3 main.py
```

---

## Environment Variables Needed

| Variable | Description |
|----------|-------------|
| GOOGLE_CREDENTIALS | Service account JSON for Sheets |
| ANTHROPIC_API_KEY | Claude API |
| OPENAI_API_KEY | GPT API |
| GEMINI_API_KEY | Gemini API |
| SENDGRID_API_KEY | Email sending |
| EMAIL_RECIPIENT | Where to send workouts |
| SPREADSHEET_ID | Google Sheets ID |

---

## Key Design Decisions

1. **Weights not in KB** — Come from previous workouts (Sheets), not hardcoded
2. **Two outputs** — Email (instructions) + JSON (logging template)
3. **Eval in email** — Scores appended to email, not stored in Sheets
4. **Reusable architecture** — sheets_client accepts spreadsheet_id parameter
5. **Zone 2 fillers** — Farmer carries, skater hops between heavy sets
6. **Model diversity** — Generator and Eval use opposite model priority

---

*Last Updated: December 2025*
*Status: ✅ Fully functional — tested locally, Generator + Eval working*

