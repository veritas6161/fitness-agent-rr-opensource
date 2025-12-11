🏋️ Olympic Athletic Club — Gym Layout & Workout Design Rules

This document defines the physical layout of Olympic Athletic Club (Ballard, Washington), spatial constraints for workout design, and action script ground rules for exercise selection and sequencing.

⸻

📍 Gym Location

**Facility:** Olympic Athletic Club  
**Location:** Ballard, Washington  
**Training Schedule:** 6 days/week  
**Reference:** See `Reza_Workout_Script_KB.md` for weekly structure

⸻

🏢 Three-Floor Layout

## Floor 1 (Ground Floor)

### Side 1: Conditioning & Lower Body Zone
**Equipment & Features:**
• Squat barbell racks
• Conditioning tools (kettlebells, jump ropes)
• Open spaces for stretching, foam rolling
• Space for core exercises

**Best For:**
• Core exercises
• Squats
• Conditioning work
• Stretching and mobility

### Side 2: Upper Body Machine Zone
**Equipment & Features:**
• Chest press machines
• Incline chest press machines
• Back machines
• Lat pulldown machines
• Hamstring curl machines
• Leg press machines

**Best For:**
• Upper body machine work (chest, back)
• Lower body machine isolation (hamstrings, quads via leg press)
• All machine-based exercises in one area

⸻

## Floor 2

### Side 1: Mixed Upper/Lower Zone
**Equipment & Features:**
• Chest press machines
• Lat pulldown machines
• Tricep pushdown machines
• Barbells
• Dumbbells
• Squat racks
• Deadlift area
• Small upper body machines (cable flies, single-arm lat pulldowns)
• Dumbbell stations
• Benches
• Additional barbell squat racks

**Best For:**
• Upper body work (chest, back, arms)
• Squats and deadlifts
• Barbell and dumbbell exercises
• Cable work

⸻

## Floor 3: Cardio & Conditioning Zone

**Equipment & Features:**
• Cardio machines (treadmills, rowers, ski ergs)
• Assault bikes
• Wall balls
• Hyrox-style conditioning area
• Dumbbells and free weights

**Best For:**
• Zone 2 cardio (Day 2)
• Heavy conditioning (Day 3)
• HIIT and metabolic work
• Hyrox-style training
• Cardio-focused blocks

⸻

🎯 Spatial Design Principles

**Core Rule: One Block = One Location**

When designing workouts:
1. **Each block should be completed in one location** before moving to the next
2. **Move to another location/floor for the next block** with related exercises
3. **Group related exercises together** within the same floor/area
4. **Minimize floor changes** during a single block to maintain heart rate

**Design Strategy:**
• Block A → Floor/Area 1 (complete all exercises)
• Block B → Floor/Area 2 (move and complete all exercises)
• Block C → Floor/Area 3 (if needed)

**Heart Rate Maintenance:**
• Keep HR >135 during transitions
• Short rest periods (45–60 sec) to maintain intensity
• Minimize downtime between blocks by efficient location grouping

⸻

📋 Action Script Ground Rules

### Muscle Group Frequency
1. **Hit every big muscle group twice per week**
   • Chest, Back, Shoulders, Legs (quads, hamstrings, glutes)

2. **Focus on arms twice per week**
   • Already defined in KB (Day 4 and Day 6)

3. **Large muscles first, smaller muscles later**
   • Sequence: Compound movements → Isolation movements
   • Example: Chest press → Tricep pushdown
   • Example: Deadlift → Hamstring curl
   • Example: Squat → Leg extension

### Exercise Selection Priority
1. **Compound movements first** (multi-joint, large muscle groups)
2. **Isolation movements second** (single-joint, smaller muscles)
3. **Accessory movements last** (targeted, finishing work)

### Within-Block Sequencing
• Always program largest movement pattern first
• Progress to smaller, more targeted movements
• Maintain training flow and intensity

⸻

🔗 Integration with KB Templates

**Day 3 — Heavy Conditioning / HIIT + Jumps:**
• Block A (Explosive HIIT) → Floor 1 Side 1 or Floor 3
• Block B (Heavy Conditioning) → Floor 3 (rower, bike, sled, battle ropes)
• Block C (Core) → Floor 1 Side 1

**Day 4 — Upper Body Strength:**
• Block A (Push) → Floor 2 or Floor 1 Side 2 (machines)
• Block B (Pull) → Floor 2 or Floor 1 Side 2 (machines)
• Block C (Arms) → Floor 2 (cable work)

**Day 5 — Lower Body Strength:**
• Block A (Heavy Lifts) → Floor 2 (squats, deadlifts)
• Block B (Glute/Ham) → Floor 1 Side 2 (machines) or Floor 2 (DB work)
• Block C (Ski Add-ons) → Floor 1 Side 1 (balance, hops)

**Day 6 — Full Body:**
• Script A (Power + Strength) → Floor 1 Side 1 (power) → Floor 2 (strength)
• Script B (Strength-Focused) → Floor 2 (alternating upper/lower)

**Day 2 — Zone 2 Cardio:**
• Entire session → Floor 3 (treadmill, rower, ski erg)

⸻

⚙️ Equipment Availability Considerations

**Constraints:**
• Equipment may be unavailable during peak hours
• Not all equipment is in one place (must plan location transitions)
• Some exercises have multiple equipment options (barbell, dumbbell, machine)

**Design Approach:**
• Provide alternative equipment options for each exercise
• Reference `Exercise_Library.csv` for equipment alternatives
• Agent should consider equipment availability when generating workouts
• Prioritize exercises that can be done with available equipment

⸻

📊 Body Composition Reference

**Body Spec Results:**
• See `bodyspec-results.pdf` for current body composition metrics
• Use baseline metrics for progression tracking
• Reference starting point: 20% body fat (target: 17% by end of January)

⸻

✅ Checklist for Workout Generation

When generating specific workouts, ensure:
- [ ] Each block uses exercises from the same floor/area
- [ ] Location transitions occur between blocks, not within blocks
- [ ] Large muscle groups come before small muscle groups
- [ ] All big muscle groups hit twice per week
- [ ] Arms appear twice per week (Day 4 and Day 6)
- [ ] Compound movements precede isolation movements
- [ ] Heart rate can be maintained >135 with efficient transitions
- [ ] Equipment alternatives available for each exercise
- [ ] Exercises match weekly structure in KB

⸻

🔗 Related Documents

• `Reza_Workout_Script_KB.md` — Weekly structure and exercise templates
• `Reza_Fitness_Goals.md` — Goals and objectives
• `Exercise_Library.csv` — Available exercises with equipment options
• `bodyspec-results.pdf` — Body composition baseline

