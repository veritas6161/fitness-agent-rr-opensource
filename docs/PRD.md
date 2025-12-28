# Fitness Agent - Product Requirements Document

## Executive Summary

The Fitness Agent is an automated workout planning system that eliminates daily decision-making overhead by generating personalized, data-driven workouts with built-in quality evaluation. The system uses a two-agent architecture (Generator + Eval) to ensure workout quality before delivery, saving users time and cognitive load while maintaining consistency and progression.

## Problem Statement

### User Pain Points

1. **Decision Fatigue**: Choosing what workout to do each day creates mental overhead
2. **Time Cost**: Daily prompting, reviewing generated workouts, providing feedback, and iterating takes significant time
3. **Memory Limitations**: Manually tracking progress, patterns, and preferences is error-prone and incomplete
4. **Quality Uncertainty**: No objective way to evaluate if a workout meets goals and preferences

### Current State

- Users must manually prompt an AI daily for workout plans
- Requires reviewing and providing feedback on generated workouts
- No systematic tracking of workout history and performance patterns
- No automated quality assurance for workout plans

## Solution Overview

A two-agent system that:
1. **Generates** personalized workouts using long-term memory and data-driven planning
2. **Evaluates** workout quality automatically, eliminating manual review
3. **Delivers** actionable instructions and tracking sheets via email
4. **Tracks** everything automatically in Google Sheets

## Target Users

**Primary User**: Fitness enthusiast who:
- Works out 4-6 days per week
- Has specific fitness goals (body composition, performance, events)
- Values consistency and progression
- Wants to eliminate daily decision-making overhead
- Prefers data-driven approach to training

## Goals & Success Metrics

### User Goals
- **Time Saved**: Eliminate daily prompting, review, and feedback cycles
- **Quality Assurance**: Automated evaluation ensures consistent workout quality
- **Data-Driven Decisions**: Long-term memory enables better progression and variety
- **Reduced Cognitive Load**: No daily decision-making required

### Success Metrics

**System Performance:**
- Generates workout nightly at 9 PM without failure
- Eval agent passes workouts on first or second attempt (avg < 2 attempts)
- Email delivered within 5 minutes of trigger
- Sheet tab created with correct pre-filled data
- Eval scores logged for every workout

**User Outcomes:**
- Reduced time spent on workout planning (target: < 5 min/day → < 1 min/day)
- Improved workout consistency (target: 6/6 days adherence)
- Better progression tracking and data visibility

## Core Features

### 1. Long-Term Memory & Data-Driven Planning

**Description**: System maintains knowledge base and tracks workout history to inform decisions.

**Requirements**:
- Store knowledge base files: goals, gym layout, performance patterns, workout scripts
- Track last 7-14 days of workout history
- Maintain exercise library with historical weights
- Use past performance data to inform progression

**Acceptance Criteria**:
- System loads KB files from file system
- System reads past workouts from Google Sheets
- Generator agent uses historical data in workout generation

### 2. Automated Quality Evaluation

**Description**: Eval agent automatically scores workouts across multiple dimensions.

**Evaluation Categories**:
1. **Workout Structure & Preferences** (target: 5-6/6)
   - Follows defined workout formula/structure
   - Includes exercises user loves
   - Clear structure: Warm-up → Blocks → Finisher

2. **Exercise Selection Quality** (target: 5/5)
   - Uses exercises from Exercise Library only
   - Uses Last Weight data appropriately
   - Proper sequencing (large → small, compound → isolation)

3. **Progression & Safety** (target: 3-4/4)
   - Includes progression cues
   - Respects injury constraints (e.g., wrist limitations)
   - Appropriate volume for the day

4. **Spatial Efficiency** (target: 3-4/4)
   - One block = one location
   - Minimized floor changes

**Requirements**:
- Eval agent scores workout across all categories
- Automatic retry loop (max 3 attempts) if quality threshold not met
- Feedback provided to generator for retry attempts

**Acceptance Criteria**:
- Eval agent returns PASS/FAIL decision
- Scores provided for each category
- Overall score calculated
- Feedback string provided if FAIL
- Retry loop triggers automatically on FAIL

### 3. Streamlined Delivery

**Description**: System delivers workout via email with instructions and tracking sheet.

**Requirements**:
- **Instructions & Pro Tips**: Hyper-customized guidance for each workout
- **Tracking Sheet**: Pre-filled Google Sheet ready for quick logging
- **Voice Logging Support**: Update workouts via voice commands
- Daily email delivery at 9 PM PST

**Email Contents**:
- Workout summary
- Instructions and pro tips
- Google Sheet link
- Eval scores

**Acceptance Criteria**:
- Email sent within 5 minutes of trigger
- Email contains all required information
- Google Sheet tab created with pre-filled exercises
- Sheet is accessible and ready for logging

### 4. Automated Tracking

**Description**: All workouts logged automatically to Google Sheets with evaluation scores.

**Requirements**:
- Create workout tab in Google Sheets with pre-filled exercises
- Log eval scores to Eval History tab
- Monthly sheet rotation for organization
- Summary dashboard with visualizations

**Sheet Schema**:
- **Daily Workout Tab**: Exercise | Set | Weight | Reps | RIR | Feel | Notes
- **Eval History Tab**: Date | Day Type | Structure Score | Selection Score | Progression Score | Spatial Score | Overall Score | Attempts
- **Summary Tab**: Aggregated data, visualizations by day type and exercise category

**Acceptance Criteria**:
- Workout tab created with correct structure
- Eval scores logged for every workout
- Monthly sheet rotation works correctly
- Summary dashboard updates with workout data

## Technical Architecture

### System Components

1. **Generator Agent** (Claude Opus 4.5)
   - Generates personalized workouts
   - Uses KB files, exercise library, past workouts
   - Outputs structured JSON

2. **Eval Agent** (GPT or Gemini - configurable)
   - Evaluates workout quality
   - Provides scores and feedback
   - Triggers retry loop if needed

3. **Google Sheets Client**
   - Reads/writes workout data
   - Manages monthly sheet rotation
   - Updates summary dashboard

4. **Email Client**
   - Sends workout notifications
   - Includes instructions and sheet link

5. **Orchestrator** (main.py)
   - Coordinates workflow
   - Manages eval loop
   - Handles error cases

### Workflow

1. Cloud Scheduler triggers at 9 PM PST
2. Determine current day in weekly cycle
3. Load KB files, exercise library, past workouts
4. **Eval Loop** (max 3 attempts):
   - Call Generator Agent
   - Call Eval Agent
   - If FAIL: retry with feedback
   - If PASS: break
5. Log eval scores to Sheets
6. Create workout tab in Sheets
7. Update Summary dashboard
8. Send email notification
9. Return success response

## Knowledge Base Structure

### Core KB Files

1. **Fitness Goals**: Personal objectives and priorities
2. **Workout Script KB**: Workout structure and flow patterns
3. **Performance Patterns**: Historical performance data and trends
4. **Gym Layout & Rules**: Spatial constraints and equipment locations
5. **Exercise Library**: Exercise database with historical weights
6. **Day-Specific Plans**: Templates for each day type (Day 3: Conditioning, Day 4: Upper Body, Day 5: Lower Body, Day 6: Full Body)
7. **Evaluation Framework**: Criteria for workout evaluation

## Constraints & Considerations

### Technical Constraints
- Must run on Google Cloud Functions/Cloud Run
- Google Sheets API rate limits
- API costs for LLM calls (Claude Opus 4.5, GPT/Gemini)
- Email delivery reliability

### User Constraints
- Knowledge base must be maintainable
- Workout logging must be quick (< 1 min)
- Email must be readable on mobile
- Sheet must be accessible offline

### Business Constraints
- API costs per workout generation
- Storage costs for Google Sheets
- Email service costs

## Future Enhancements

### Phase 2: Food Automation
- Integration with meal planning and nutrition tracking
- Automated meal suggestions based on workout schedule and goals
- Macro tracking and adjustments

### Phase 3: Health Data Integration
- Whoop device integration for recovery metrics
- Workout adjustments based on sleep, recovery, and HRV data
- Data-driven rest day recommendations
- Recovery-based volume adjustments

### Phase 4: Enhanced Analytics
- Advanced performance trend analysis
- Predictive modeling for progression
- Personalized recovery recommendations
- Injury risk prediction

## Out of Scope (MVP)

- Mobile app (email + sheets sufficient)
- Social features
- Trainer collaboration
- Video exercise library
- Payment processing
- Multi-user support

## Dependencies

### External Services
- Anthropic Claude API (Generator Agent)
- OpenAI API or Google Gemini API (Eval Agent)
- Google Sheets API
- SendGrid or Gmail SMTP (Email)
- Google Cloud Functions/Cloud Run
- Google Cloud Scheduler

### Internal Dependencies
- Knowledge base files must be maintained
- Exercise library must be kept up to date
- Past workout data must be logged consistently

## Risks & Mitigations

### Risk: Eval agent fails frequently
**Mitigation**: Tune eval criteria, improve generator prompt, increase max attempts

### Risk: API costs too high
**Mitigation**: Optimize prompts, cache responses, use cheaper models for eval

### Risk: Google Sheets API rate limits
**Mitigation**: Batch operations, implement retry logic, optimize queries

### Risk: Email delivery failures
**Mitigation**: Use reliable email service, implement retry logic, fallback to Gmail SMTP

### Risk: Knowledge base becomes outdated
**Mitigation**: Document update process, version control KB files, regular reviews

## Timeline

### MVP (Current)
- ✅ Basic Cloud Function setup
- ✅ Google Sheets integration
- ⏳ Generator Agent implementation
- ⏳ Eval Agent implementation
- ⏳ Email notifications
- ⏳ Cloud Scheduler setup

### Future Phases
- Phase 2: Food Automation (Q2 2026)
- Phase 3: Health Data Integration (Q3 2026)
- Phase 4: Enhanced Analytics (Q4 2026)

