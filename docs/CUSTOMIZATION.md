# Customization Guide

This guide will help you customize the Fitness Agent for your own goals, preferences, and gym setup.

---

## Overview

The Fitness Agent uses **Knowledge Base (KB) files** to understand your goals, preferences, injury constraints, and gym layout. These files are located in the `kb/` directory and must be customized before deployment.

---

## KB Files to Customize

### 1. `kb/goals.md` - Your Fitness Goals

**What to customize:**
- Primary fitness goal (e.g., triathlon, marathon, body composition, strength)
- Body composition targets
- Weekly training targets (Zone 2, VO2 max, sets per muscle group)
- Milestone timeline
- Success metrics

**Example structure:**
```markdown
## Primary Target
**Ironman 70.3 Oceanside** — March 2027

## Body Composition
- Current: 20% body fat, 160 lbs
- Target: 17% by January 2026

## Weekly Targets
| Metric | Target |
|--------|--------|
| Training days | 6-7 days/week |
| Zone 2 time | 3 hrs/week |
| Sets per major muscle | 12+ sets/week |
```

**Tips:**
- Be specific about your primary goal - this drives workout programming
- Set realistic weekly targets based on your schedule
- Include any upcoming events or milestones

---

### 2. `kb/status.md` - Current Status

**What to customize:**
- Current body composition measurements
- Training frequency and session length
- Current vs. target metrics
- Weekly schedule (rest days, trainer days, etc.)
- Facility/gym name
- Current strengths and limiters

**Example structure:**
```markdown
## Body Composition (December 2025)
- Body fat: 20%
- Total weight: 160 lbs

## Training Setup
| Metric | Current | Target |
|--------|---------|--------|
| Frequency | 5 days/week | 6-7 days/week |
| Session length | 50 min | 50-55 min |

## Weekly Schedule
| Day | Type | Notes |
|-----|------|-------|
| Friday | **Trainer Day** | Agent does NOT generate workouts |
| Sat-Thu | Agent-generated | 5-6 workouts |
```

**Tips:**
- Be honest about current status - this helps the agent program appropriately
- Specify any days that should be skipped (trainer days, rest days)
- List your gym/facility name

---

### 3. `kb/preferences.md` - Exercise Preferences & Constraints

**What to customize:**
- Exercises you love
- Exercises you dislike
- Injury history and constraints
- Training style preferences
- Session preferences

**Example structure:**
```markdown
## Exercises I Love
- Heavy compounds (squats, deadlifts)
- Face pulls, curls
- Leg press, lunges

## Exercises I Dislike
- Dips (wrist issue)
- Push-ups (wrist issue)

## Injury History & Constraints

### Right Wrist — ACTIVE ISSUE
- **Issue:** Tendon problems
- **Triggers:** Backward movements, heavy loading
- **Management:** Avoid dips, push-ups, front rack. Use neutral grips.
```

**Tips:**
- **CRITICAL:** List ALL injury constraints - the agent will avoid these exercises
- Be specific about what to avoid and what alternatives to use
- Include exercises you love - the agent will prioritize these

---

### 4. `kb/gym_layout.md` - Your Gym Layout

**What to customize:**
- Floor/area names and descriptions
- Equipment available on each floor
- Best use cases for each area
- Workout design rules based on layout

**Example structure:**
```markdown
## Floor Overview
| Floor | Name | Equipment | Best For |
|-------|------|-----------|----------|
| Floor 1 | Open Side | Squat racks, open floor | Core, mobility |
| Floor 2 | Heavy/Olympic | Barbells, squat racks | Heavy compounds |
| Floor 3 | Conditioning | Treadmills, rowers | Cardio, HIIT |

## Workout Design Rules
**Core Rule:** One block = one location. Complete all exercises in a block before moving floors.
```

**Tips:**
- Map out your gym's actual layout - this enables efficient workout flow
- List equipment available in each area
- Define rules for minimizing floor transitions

---

### 5. `kb/exercise_library.md` - Exercise Library

**What to customize:**
- Add/remove exercises based on what's available at your gym
- Add exercises you want to include
- Remove exercises you don't have equipment for

**Example structure:**
```markdown
## Push
| Exercise | Equipment | Notes |
|----------|-----------|-------|
| Bench press | Barbell | Flat bench |
| Chest press | Machine | Flat or incline |

## Pull
| Exercise | Equipment | Notes |
|----------|-----------|-------|
| Lat pulldown | Machine | Wide or close grip |
| Barbell row | Barbell | Bent over |
```

**Tips:**
- Only include exercises you can actually do at your gym
- Organize by movement pattern (Push, Pull, Legs, etc.)
- Add notes about equipment variations or modifications

---

## Customization Workflow

### Step 1: Review Template Files

1. Open each KB file in `kb/`
2. Read through the template structure
3. Note the `<!-- CUSTOMIZE: -->` comments

### Step 2: Fill in Your Information

1. **Start with `goals.md`** - Define your primary fitness goal
2. **Then `status.md`** - Set your current status and schedule
3. **Then `preferences.md`** - List injuries, preferences, and constraints
4. **Then `gym_layout.md`** - Map your gym's layout
5. **Finally `exercise_library.md`** - Customize available exercises

### Step 3: Test Locally

After customizing, test the system:

```bash
cd src
python3 main.py
```

Check that:
- Workouts reference your goals
- Injury constraints are respected
- Gym layout is used correctly
- Exercises are from your library

### Step 4: Iterate

- If workouts don't match your goals, refine `goals.md`
- If injury constraints aren't respected, check `preferences.md`
- If gym layout isn't efficient, update `gym_layout.md`

---

## Common Customization Scenarios

### Scenario 1: Body Composition Focus

**Goals:**
- Primary: Lose 20 lbs by June
- Focus: Fat loss + muscle retention

**Customize:**
- `goals.md`: Set body composition targets, weekly training days
- `preferences.md`: Emphasize compound movements, cardio
- `status.md`: Track current weight, body fat %

### Scenario 2: Endurance Sport (Triathlon/Marathon)

**Goals:**
- Primary: Complete Ironman 70.3
- Focus: Aerobic base + strength maintenance

**Customize:**
- `goals.md`: Set Zone 2 targets, weekly swim/bike/run goals
- `preferences.md`: Include triathlon-specific exercises
- `status.md`: Track training volume across disciplines

### Scenario 3: Strength Focus

**Goals:**
- Primary: Build muscle mass
- Focus: Progressive overload, volume

**Customize:**
- `goals.md`: Set sets per muscle group targets
- `preferences.md`: Emphasize heavy compounds
- `status.md`: Track strength metrics (1RM, volume)

---

## Tips for Best Results

1. **Be Specific:** Vague goals lead to generic workouts
2. **Be Honest:** Accurate current status helps the agent program appropriately
3. **Be Complete:** Fill out all sections - missing info leads to assumptions
4. **Be Realistic:** Set targets you can actually achieve
5. **Test & Iterate:** Customize → Test → Refine → Repeat

---

## Troubleshooting

### Workouts Don't Match My Goals

- Check `goals.md` - is your primary goal clear?
- Review `preferences.md` - are preferences aligned with goals?
- Check if weekly targets are realistic

### Injury Constraints Not Respected

- Verify `preferences.md` lists all injuries
- Check that forbidden exercises are explicitly listed
- Ensure management strategies are clear

### Gym Layout Not Used Efficiently

- Review `gym_layout.md` - is layout accurate?
- Check workout design rules
- Verify equipment lists match actual gym

### Exercises Not From Library

- Review `exercise_library.md` - are exercises listed?
- Check if exercise names match exactly
- Add missing exercises to library

---

## Next Steps

After customizing your KB files:

1. **Test locally** - Run `python3 src/main.py`
2. **Deploy** - Follow [DEPLOYMENT.md](DEPLOYMENT.md)
3. **Monitor** - Check email delivery and workout quality
4. **Iterate** - Refine KB files based on results

---

## Questions?

If you need help customizing, open an issue on GitHub with:
- Your fitness goal
- What you've tried
- What's not working

We're here to help!

