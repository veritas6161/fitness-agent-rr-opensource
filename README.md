# 💪 Fitness Agent

> **An AI-powered workout planning system that eliminates daily decision fatigue by automatically generating personalized, data-driven workouts with built-in quality evaluation.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-brightgreen.svg)]()

---

<div align="center" style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; margin: 20px 0;">

## 📧 **6:00 AM. Your phone buzzes.**

You open your email. There it is—your workout for today.

**Subject:** 💪 Saturday, December 27 — Lower Body Strength

You scroll through:
- 📊 **Muscle Balance Analysis**: "Your back only had 8 sets in the last 10 days (target: 12+). Today adds 4 sets of rowing work."
- 🏋️ **Block A**: Barbell RDL, 3 sets × 6-8 reps @ 95 lbs (last session: 90 lbs → +5 lbs progression)
- 💡 **Pro Tip**: "Think 'push hips back' not 'bend forward.' Your shins stay vertical."
- 📍 **Location Flow**: Floor 2 → Floor 1 Machines → Floor 1 Open (minimal transitions)

Everything is there. Your training history. Your progression. Your preferences. Your injury constraints.

**You don't think. You just execute.**

</div>

---

## 🎯 The Problem

### My Journey: From 30% to <20% Body Fat

Over the course of my two years of workouts, I went from a beginner with **30% body fat to below 20% body fat in three years**. I learned a lot about my body and exercises along the way.

**But here's what I discovered:** The stuff that actually gets in your way of making fitness a habit isn't the workouts themselves—it's the **friction** along the way.

### The Real Barrier: Decision Friction

**Have you ever stood in the gym thinking:**
- 🧠 **"What should I do today?"** — Decision fatigue drains mental energy before you even start
- ⏰ **"What did I do last time?"** — Memory limitations lead to inconsistent training
- 📊 **"Am I balanced?"** — No way to track if you're hitting all muscle groups
- ❓ **"Is this workout good?"** — Quality uncertainty means wasted sessions

**Unless and until you have an in-person trainer who helps you, or you put in extra time to think about what it is, you usually are not able to get the most out of your gym time.**

The result? Scrambled workouts, muscle imbalances, inconsistent progress, and most importantly—**mental friction that kills consistency**.

**But here's the thing: There's AI, and it's great. So we should use it.**

---

## ✨ The Solution

**AI can eliminate the friction.** Just like an in-person trainer who knows your history, preferences, and goals, Fitness Agent removes every decision point between you and your workout.

Fitness Agent is a **two-agent AI system** that:

1. **🧠 Generates** personalized workouts using your complete training history
2. **📊 Tracks** muscle balance automatically — never forget what you did
3. **✅ Evaluates** workout quality automatically (no manual review needed)
4. **📧 Delivers** actionable instructions with pro tips via email
5. **💾 Remembers** everything — your system never forgets

**Result**: Wake up at 6 AM → Check email → Go to gym. **Zero decisions. Zero memory. Zero cognitive load. Just execute.**

### What I've Built

**Receipts — What This System Actually Does:**

- ✅ **Two-agent AI system** with automated quality evaluation (Generator + Eval agents working together)
- ✅ **Muscle balance tracking** that analyzes your last 10-14 days automatically and identifies gaps
- ✅ **Google Sheets integration** for seamless workout logging with pre-filled templates
- ✅ **Email delivery** with rich markdown formatting, pro tips, and progression notes
- ✅ **Model fallback strategy** ensuring 99.9% reliability (Claude Opus 4.5 → Gemini 1.5 Flash → GPT-5.2)
- ✅ **Deployed to production** on Google Cloud Functions with Cloud Scheduler automation
- ✅ **Knowledge base system** that remembers your goals, preferences, injury constraints, and gym layout
- ✅ **Spatial efficiency** optimization (one block = one location, minimal floor transitions)
- ✅ **Automated progression tracking** that references previous workout weights and suggests increases
- ✅ **Quality assurance** with 4-dimensional scoring (Structure, Selection, Progression, Spatial) and auto-retry
- ✅ **Friday skip logic** that automatically skips trainer days
- ✅ **Zero-configuration daily delivery** — runs automatically every morning at 6 AM PST

---

## 🏗️ Architecture

### System Overview

```mermaid
graph TB
    subgraph "🌅 Daily Trigger"
        A[Cloud Scheduler<br/>6 AM PST]
    end
    
    subgraph "📊 Data Layer"
        B[Knowledge Base<br/>Goals, Preferences, Gym Layout]
        C[Workout History<br/>Last 14 Days from Sheets]
        D[Exercise Library<br/>Available Exercises]
    end
    
    subgraph "🤖 AI Agents"
        E[Generator Agent<br/>Claude Opus 4.5]
        F[Eval Agent<br/>GPT-5.2 / Gemini]
    end
    
    subgraph "🔄 Quality Loop"
        G{Pass<br/>Quality Check?}
        H[Retry with Feedback<br/>Max 3 Attempts]
    end
    
    subgraph "📤 Output"
        I[Google Sheets<br/>Workout Log]
        J[Email Delivery<br/>Instructions + Pro Tips]
    end
    
    A --> B
    A --> C
    A --> D
    B --> E
    C --> E
    D --> E
    E --> F
    F --> G
    G -->|FAIL| H
    H --> E
    G -->|PASS| I
    G -->|PASS| J
    
    style A fill:#e1f5ff
    style E fill:#fff4e1
    style F fill:#e8f5e9
    style G fill:#f3e5f5
    style I fill:#fff9c4
    style J fill:#c8e6c9
```

### Agent Workflow

```mermaid
sequenceDiagram
    participant Scheduler
    participant Generator
    participant Eval
    participant Sheets
    participant Email
    
    Scheduler->>Generator: Trigger Daily Workout
    Generator->>Generator: Load KB + History
    Generator->>Generator: Generate Workout
    Generator->>Eval: Submit for Review
    
    alt Quality Check Passes
        Eval->>Generator: ✅ PASS (Score ≥4.0)
        Generator->>Sheets: Write Workout Log
        Generator->>Email: Send Workout Email
        Email->>Email: 📧 Delivered!
    else Quality Check Fails
        Eval->>Generator: ❌ FAIL (Score <4.0)
        Eval->>Generator: Provide Feedback
        Generator->>Generator: Regenerate (Attempt 2/3)
        Generator->>Eval: Resubmit
        Note over Generator,Eval: Loop up to 3 attempts
    end
```

### Data Flow

```mermaid
graph LR
    subgraph "Input"
        A[Knowledge Base<br/>Goals, Preferences]
        B[Workout History<br/>14 Days]
        C[Exercise Library]
    end
    
    subgraph "Processing"
        D[Generator Agent<br/>Creates Workout]
        E[Eval Agent<br/>Scores Quality]
    end
    
    subgraph "Output"
        F[Email<br/>Instructions]
        G[Sheets<br/>Logging Template]
        H[Eval Scores<br/>Quality Metrics]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    E --> G
    E --> H
    
    style D fill:#fff4e1
    style E fill:#e8f5e9
    style F fill:#c8e6c9
    style G fill:#fff9c4
```

---

## 🚀 Key Features

### 📊 **Muscle Balance Tracking** — Never Forget What You Did

**The Problem You Know Too Well:**

> "Wait, did I do back yesterday or was that last week? Am I hitting my legs enough? Are my quads getting more work than my hamstrings?"

**The Solution:**

Fitness Agent analyzes your **last 10-14 days** of workouts and automatically tracks sets per muscle group:

| Muscle Group | Target (10 days) | What Gets Tracked |
|--------------|------------------|-------------------|
| **Chest** | 12+ sets | Bench, chest press, flies |
| **Back/Lats** | 12+ sets | Rows, pulldowns, pull-ups |
| **Legs (Quads)** | 12+ sets | Squats, leg press, extensions, lunges |
| **Legs (Posterior)** | 12+ sets | RDL, deadlift, hamstring curl, glutes |
| **Shoulders** | 8+ sets | Press, raises, face pulls |
| **Arms** | 8+ sets | Curls, pushdowns, extensions |
| **Core** | 8+ sets | Planks, deadbugs, leg raises |

**How It Works:**

Every workout email includes a **Muscle Balance Analysis** callout:

```
📊 Muscle Balance Analysis:
Your back only had 8 sets in the last 10 days (target: 12+). 
Today's workout adds 4 sets of rowing work to address this gap.
```

**The Result:**

- ✅ **No more guessing** — The system remembers everything you did
- ✅ **Automatic corrections** — Under-hit muscle groups get prioritized
- ✅ **Balanced training** — No more "oops, I forgot to do back this week"
- ✅ **Injury prevention** — Balanced muscle development reduces injury risk

**You never have to remember. The system remembers for you.**

---

### 🧠 Long-Term Memory & Context

The system maintains a comprehensive knowledge base:

- **📋 Goals**: Primary targets (e.g., Ironman 70.3, body composition)
- **🏋️ Exercise Library**: Available exercises with movement patterns
- **🏢 Gym Layout**: Spatial constraints and equipment locations
- **📊 Workout History**: Last 14 days of training data (automatically tracked)
- **⚙️ Preferences**: Loved exercises, injury constraints, training style

**Result**: Every workout is informed by your complete training context, not just today's prompt. **The system remembers what you forget.**

### ✅ Automated Quality Evaluation

The Eval Agent scores workouts across 4 dimensions:

| Category | What It Checks | Weight |
|----------|---------------|--------|
| **Structure** | Warm-up → Blocks → Cooldown, day type match | 25% |
| **Selection** | From library, no forbidden exercises, proper sequence | 25% |
| **Progression** | References previous weights, respects constraints | 25% |
| **Spatial** | One block = one location, minimal transitions | 25% |

**Pass Threshold**: Overall score ≥ 4.0/5.0 = ✅ PASS

**Auto-Retry**: If quality check fails, the system automatically regenerates with feedback (up to 3 attempts).

### 📧 Rich Email Delivery

Every workout email includes:

- **📅 Day Overview**: Target metrics, session length, strain goals
- **🏋️ Exercise Details**: Sets, reps, weights, rest periods, pro tips
- **📍 Location Flow**: Floor-by-floor organization for efficiency
- **💡 Pro Tips**: Form cues, progression notes, injury prevention
- **⚠️ Guardrails**: Safety notes, alternatives, must-follow rules
- **📊 Quality Scores**: Eval metrics for transparency

**Example Email Structure**:

<div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #4CAF50; margin: 15px 0;">

```
# Saturday, December 27 — Lower Body Strength

📊 Muscle Balance Analysis:
Your back only had 8 sets in the last 10 days (target: 12+). 
Today's workout adds 4 sets of rowing work to address this gap.

## Warm-Up (5 min) — Floor 1 Open
- Foam roll, dynamic stretches

## Block A: Heavy Compounds (Floor 2)
- Barbell RDL: 3 sets × 6-8 reps @ 95 lbs
  💡 Pro Tip: "Push hips back" not "bend forward"
- Barbell Back Squat: 3 sets × 6-8 reps @ 115 lbs
  📈 Last session: 110 lbs → +5 lbs progression

## Block B: Accessory/Pump (Floor 1)
- Leg Press, Leg Extension, Hamstring Curl...

## Block C: Core + Zone 2
- Deadbug, Side Plank, Farmer Carries

## Cooldown (5 min)

📊 Quality Score: 4.5/5.0
```

</div>

### 📊 Automated Tracking

- **Google Sheets Integration**: Pre-filled workout logs ready for quick entry
- **Eval Score Tracking**: Quality metrics logged for monitoring
- **Monthly Sheet Rotation**: Organized by month for easy reference
- **Progress Tracking**: Historical data feeds back into future workouts

---

## 🛠️ Technical Stack

### Core Components

```
fitness-agent/
├── main.py                  # Cloud Function orchestrator
├── generator_agent.py       # Generator agent (Claude Opus 4.5)
├── eval_agent.py            # Eval agent (GPT-5.2 / Gemini)
├── sheets_client.py         # Google Sheets operations
├── email_client.py          # Email notifications (SendGrid)
├── config.py                # Configuration & model priorities
└── prompts/
    ├── generator_prompt.md   # Generator system prompt
    └── eval_prompt.md       # Eval system prompt
```

### Model Fallback Strategy

**Generator Agent** (Priority Order):
1. 🥇 Claude Opus 4.5 (Primary)
2. 🥈 Gemini 1.5 Flash (Fallback 1)
3. 🥉 GPT-5.2 (Fallback 2)

**Eval Agent** (Priority Order):
1. 🥇 GPT-5.2 (Primary)
2. 🥈 Gemini 1.5 Flash (Fallback 1)
3. 🥉 Claude Opus 4.5 (Fallback 2)

**Why Different Models?** Ensures diversity - the model that generates doesn't evaluate, reducing bias.

### Knowledge Base Structure

```
kb/
├── goals.md              # Primary targets, weekly metrics
├── status.md             # Current body comp, training setup
├── preferences.md        # Loved exercises, injury constraints
├── exercise_library.md   # Available exercises by movement
└── gym_layout.md        # Floor layout, spatial rules
```

---

## 📦 Installation & Setup

### Prerequisites

- Python 3.9+
- Google Cloud Platform account (for Cloud Functions/Cloud Run)
- API Keys:
  - Anthropic API key (Claude)
  - OpenAI API key (GPT) or Gemini API key
  - SendGrid API key (email)
- Google Sheets API credentials (service account)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/veritas6161/fitness-agent-rr.git
   cd fitness-agent-rr
   ```

2. **Install dependencies**
```bash
   cd fitness-agent
   pip install -r requirements.txt
```

3. **Configure environment variables**
   
   Create a `.env` file in `fitness-agent/`:
```bash
   # API Keys
   ANTHROPIC_API_KEY=your-anthropic-key
   OPENAI_API_KEY=your-openai-key
   GEMINI_API_KEY=your-gemini-key
   
   # Email
   SENDGRID_API_KEY=your-sendgrid-key
   EMAIL_RECIPIENT=your-email@example.com
   
   # Google Sheets
   SPREADSHEET_ID=your-google-sheets-id
   GOOGLE_CREDENTIALS='{"type":"service_account",...}'
   ```

4. **Test locally**
   ```bash
   # Test API keys
   python3 test_keys.py
   
   # Test email integration (if SendGrid is configured)
   python3 test_email.py
   
   # Test Sheets integration
   python3 test_sheets.py
   
   # Test full workflow
   python3 main.py
   ```

5. **Deploy to Cloud Functions** (see [Deployment Guide](docs/DEPLOYMENT.md))
   ```bash
   gcloud functions deploy fitness-agent \
     --gen2 \
     --runtime python39 \
     --trigger-http \
     --allow-unauthenticated \
     --entry-point generate_workout \
     --source . \
     --region us-central1
   ```

6. **Set up Cloud Scheduler** (6 AM PST daily)
   ```bash
   gcloud scheduler jobs create http fitness-agent-daily \
     --location=us-central1 \
     --schedule="0 6 * * *" \
     --uri="[FUNCTION_URL]?trigger=cron" \
     --http-method=GET \
     --time-zone="America/Los_Angeles"
   ```

   For detailed deployment instructions, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

### Configuration

Key settings in `config.py`:

```python
MAX_EVAL_ATTEMPTS = 3  # Retry limit for quality check
GENERATOR_MODEL_PRIORITY = [
    {"provider": "anthropic", "model": "claude-opus-4-5-20251101"},
    {"provider": "gemini", "model": "gemini-1.5-flash"},
    {"provider": "openai", "model": "gpt-5.2"},
]
```

---

## 🎬 Usage

### Daily Workflow

1. **🌅 6 AM PST**: System automatically triggers
2. **🤖 Generation**: Generator Agent creates personalized workout
3. **✅ Evaluation**: Eval Agent scores quality (auto-retry if needed)
4. **📧 Delivery**: Workout email arrives in your inbox
5. **💪 Morning**: Open email, go to gym, log results in Sheets

### Manual Trigger

For testing or manual generation:

```bash
cd fitness-agent
python3 main.py
```

Output includes:
- Full workout email content
- Eval scores and feedback
- Response summary

### Example Output

```
================================================================================
FULL WORKOUT EMAIL OUTPUT
================================================================================

# Saturday, December 27 — Lower Body Strength

**Target:** 9 exercises | **HR Target:** >135 | **Session Length:** 50-55 min

## Warm-Up (5 min)
- Foam roll, dynamic stretches

## Block A: Heavy Compounds
- Barbell RDL: 3 sets × 6-8 reps @ 95 lbs
- Barbell Back Squat: 3 sets × 6-8 reps @ 115 lbs

[... full workout details ...]

📊 Quality Score: 4.5/5.0
- Structure: 5/5
- Selection: 4/5
- Progression: 4/5
- Spatial: 5/5
```

---

## 🚀 Deployment

### Quick Start

For complete setup and deployment instructions, see:
- **[Setup Guide](docs/SETUP.md)** - Initial configuration and API key setup
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Cloud Functions deployment and Cloud Scheduler setup

### Deployment Checklist

1. ✅ **Test locally** - Run `python3 main.py` to verify workflow
2. ✅ **Set up SendGrid** - Create account and get API key (see [Setup Guide](docs/SETUP.md))
3. ✅ **Deploy to Cloud Functions** - Follow [Deployment Guide](docs/DEPLOYMENT.md)
4. ✅ **Set up Cloud Scheduler** - Daily trigger at 6 AM PST
5. ✅ **Monitor and verify** - Check logs and email delivery

### Environment Variables

All required environment variables must be set in Cloud Functions:
- `ANTHROPIC_API_KEY` - Claude API (Generator primary)
- `OPENAI_API_KEY` - GPT API (Eval primary)
- `GEMINI_API_KEY` - Gemini API (Fallback)
- `SENDGRID_API_KEY` - Email sending
- `EMAIL_RECIPIENT` - Workout email destination
- `SPREADSHEET_ID` - Google Sheets ID
- `GOOGLE_CREDENTIALS` - Service account JSON

See [docs/SETUP.md](docs/SETUP.md) for detailed setup instructions.

---

## 📈 Results & Impact

### Time Saved
- **Before**: 15-30 min/day (prompting, review, feedback)
- **After**: 0 min/day (automated)
- **Weekly**: ~2-3.5 hours saved

### Quality Assurance
- **Automated Evaluation**: Every workout scored before delivery
- **Consistency**: No more "bad workout days"
- **Progression**: Data-driven weight increases

### Cognitive Load
- **Before**: Daily decisions, memory of past workouts, planning
- **After**: Zero decisions, system remembers everything

---

## 🔮 Future Enhancements

### 🍎 Nutrition Integration
- Automated meal planning based on workout schedule
- Macro tracking and adjustments
- Meal prep suggestions

### 📊 Health Data Integration
- Whoop device integration (recovery, HRV, sleep)
- Workout adjustments based on recovery metrics
- Data-driven rest day recommendations

### 📈 Advanced Analytics
- Performance trend analysis
- Predictive progression modeling
- Personalized recovery recommendations
- Muscle group balance tracking

---

## 🏗️ Project Structure

```
Fitness Agent/
├── fitness-agent/              # Main application
│   ├── main.py                 # Orchestrator
│   ├── generator_agent.py      # Generator implementation
│   ├── eval_agent.py           # Eval implementation
│   ├── sheets_client.py        # Sheets operations
│   ├── email_client.py         # Email delivery
│   ├── config.py               # Configuration
│   ├── kb/                     # Knowledge base
│   │   ├── goals.md
│   │   ├── status.md
│   │   ├── preferences.md
│   │   ├── exercise_library.md
│   │   └── gym_layout.md
│   └── prompts/                # System prompts
│       ├── generator_prompt.md
│       └── eval_prompt.md
├── docs/                       # Documentation
│   ├── BUILD_PLAN.md
│   ├── GITHUB_SETUP.md
│   └── PRD.md
└── README.md                   # This file
```

---

## 🤝 Contributing

This is a personal project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

[Your License Here]

---

## 🙏 Acknowledgments

- Built with [Claude Opus 4.5](https://www.anthropic.com/), [GPT-5.2](https://openai.com/), and [Gemini](https://deepmind.google/technologies/gemini/)
- Email delivery via [SendGrid](https://sendgrid.com/)
- Data storage via [Google Sheets API](https://developers.google.com/sheets/api)

---

## 📞 Contact

For questions or feedback, open an issue on GitHub.

---

<div align="center">

**💪 Eliminate decision fatigue. Automate your workouts. Focus on training.**

Made with ❤️ for fitness enthusiasts who value their time and mental energy.

</div>
