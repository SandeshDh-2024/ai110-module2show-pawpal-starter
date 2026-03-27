# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

The scheduler includes four algorithmic features beyond basic task storage:

### Sort by Time (`Schedule.sort_by_time`)
Tasks are sorted chronologically by their `earliest_start` using a lambda key: `key=lambda t: t.earliest_start`. Tasks without a start time are pushed to the end via a `datetime.max` fallback. This ensures the daily view reads like an actual agenda regardless of the order tasks were added.

### Filter by Pet and Status (`Schedule.filter_tasks`)
A single method accepts optional `pet_name` and `completed` arguments. Each filter is applied as a list comprehension only when provided, so callers can filter by pet, by status, or by both in one call.

### Recurring Tasks (`Task.mark_done` + `Schedule.mark_task_complete`)
Tasks can carry a `recurrence` field ("daily" or "weekly"). When a recurring task is marked complete, `mark_done()` uses `timedelta(days=1)` or `timedelta(weeks=1)` to calculate the next occurrence and returns a new Task with the shifted time window. `Schedule.mark_task_complete()` automatically adds that new task to the schedule so the owner never has to re-enter it.

### Conflict Detection (`Schedule.find_conflicts`)
Compares every pair of incomplete, timed tasks. Two tasks conflict when their time windows overlap (task A's end is after task B's start). Each conflict is classified as:
- **SAME-PET CONFLICT** -- one pet is double-booked
- **CROSS-PET CONFLICT** -- different pets overlap, meaning the owner cannot attend to both

The method returns human-readable warning strings instead of raising exceptions, so the program never crashes on a scheduling error.
