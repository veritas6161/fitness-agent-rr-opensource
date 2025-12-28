# Fitness Agent MVP - Todo List

## Implementation Steps

| Step | Task | Status |
|------|------|--------|
| 1 | Organize and categorize old/base files | ✅ Complete |
| 2 | Create fitness-agent/ project structure | ✅ Complete |
| 3 | Update config.py - model priorities, KB paths | ✅ Complete |
| 4 | Build sheets_client.py | ✅ Complete |
| 5 | Create KB files (goals, status, preferences, exercise_library, gym_layout) | ✅ Complete |
| 6 | Create generator system prompt | ✅ Complete |
| 7 | Create generator_agent.py | ✅ Complete |
| 8 | Create eval system prompt | ✅ Complete |
| 9 | Create eval_agent.py | ✅ Complete |
| 10 | Build email_client.py | ✅ Complete |
| 11 | Build main.py orchestrator | ✅ Complete |
| 12 | Create requirements.txt | ✅ Complete |
| 13 | Test locally | ⏳ Ready to test |
| 14 | Deploy to Cloud Run | ⏳ Pending |
| 15 | Set up Cloud Scheduler (9 PM) | ⏳ Pending |

## Current Progress

**Last Updated:** Steps 10-12 completed

### All Code Complete!

```
fitness-agent/
├── main.py                  # ✅ Full orchestrator
├── generator_agent.py       # ✅ With model fallback
├── eval_agent.py            # ✅ With model fallback
├── sheets_client.py         # ✅ Generic/reusable
├── email_client.py          # ✅ SendGrid integration
├── config.py                # ✅ Model priorities, paths
├── requirements.txt         # ✅ All dependencies
├── kb/                      # ✅ All KB files
└── prompts/                 # ✅ Generator + Eval prompts
```

### Ready to Test

To test locally:
```bash
cd fitness-agent
pip install -r requirements.txt
python main.py
```

Required environment variables:
- GOOGLE_CREDENTIALS (service account JSON)
- ANTHROPIC_API_KEY
- OPENAI_API_KEY  
- GEMINI_API_KEY
- SENDGRID_API_KEY
- EMAIL_RECIPIENT
- SPREADSHEET_ID

---

## Notes

- SESSION_NOTES.md created with full architecture documentation
- All code complete, ready for local testing
- Friday = trainer day (auto-skipped)
- 3 failed evals = send best attempt with warning
