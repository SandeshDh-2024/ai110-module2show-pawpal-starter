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

## Features

PawPal+ is built around four classes (`Owner`, `Pet`, `Task`, `Schedule`) and exposes the following capabilities through the Streamlit UI:

### Pet and Owner Management
- Register multiple pets with species, breed, age, and health notes
- Configure owner availability (daily minutes) and preferences
- Each pet maintains its own task list independently of the schedule

### Task Scheduling
- Create tasks with a title, duration, priority (low / medium / high), type, and time window
- Assign every task to a specific pet
- **Priority sorting** — `Schedule.optimize()` orders tasks from highest to lowest priority so the most important care happens first
- **Chronological sorting** — `Schedule.sort_by_time()` arranges tasks by `earliest_start` using a lambda sort key, pushing unscheduled tasks to the end so the daily view reads like a real agenda

### Daily Recurrence
- Mark any task as `"daily"` or `"weekly"` recurring
- When a recurring task is completed, `Task.mark_done()` automatically generates the next occurrence by shifting the time window forward with `timedelta(days=1)` or `timedelta(weeks=1)`
- The new task is added to the schedule instantly — no manual re-entry needed

### Conflict Detection
- `Schedule.find_conflicts()` compares every pair of incomplete, timed tasks for overlapping windows
- Conflicts are classified as **SAME-PET** (one pet double-booked) or **CROSS-PET** (owner double-booked across pets)
- The UI displays each conflict as an `st.warning` with an actionable tip explaining what to fix

### Filtering and Display
- Filter the schedule by pet name, completion status, or both using `Schedule.filter_tasks()`
- View tasks in a clean `st.table` sorted chronologically
- Mark tasks complete directly from the UI with automatic recurrence handling
- Expand "Schedule log" to see a plain-English explanation of every scheduling decision

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

## Testing PawPal+

### Running the tests

```bash
python -m pytest
```

For verbose output showing each test name and result:

```bash
python -m pytest -v
```

### What the tests cover

The test suite (`tests/test_pawpal.py`) includes 7 tests across happy paths and edge cases:

| Test | Category | What it verifies |
|------|----------|-----------------|
| `test_task_completion` | Happy path | A task can be marked done and `is_complete()` reflects that |
| `test_pet_task_addition` | Happy path | Tasks are added to a pet and `task_count()` updates correctly |
| `test_build_plan_sorts_by_priority_and_sums_minutes` | Happy path | `build_plan()` sorts tasks highest-priority-first and sums total minutes |
| `test_daily_recurring_task_creates_next_occurrence` | Recurrence | Completing a daily task creates a new task shifted +1 day with `recurrence="daily"` preserved |
| `test_pet_with_zero_tasks` | Edge case | A pet with no tasks returns count 0; building an empty schedule does not crash |
| `test_same_time_same_pet_conflict` | Conflict | Two identical-window tasks for the same pet produce a `SAME-PET CONFLICT` warning |
| `test_sort_by_time_returns_chronological_order` | Sorting | Tasks added out of order are returned 07:00 -> 12:00 -> 18:00; tasks with no start time go last |

### Confidence Level

**Confidence: 4 / 5 stars**

The core scheduling behaviors -- priority sorting, chronological sorting, daily recurrence, and conflict detection -- are all tested and passing. One star is held back because the suite does not yet cover weekly recurrence, cross-pet conflicts, or the `filter_tasks()` method. Adding those tests would bring confidence to 5/5.

### Demo

<a href="/ai110-module2show-pawpal-starter/image.png" target="_blank"><img src='/ai110-module2show-pawpal-starter/image.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>