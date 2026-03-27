from pawpal_system import Pet, Task, Owner, Schedule
from datetime import date, datetime, time, timedelta
from typing import List

# -- Helper: expand recurring tasks -------------------------------------------

def expand_recurring(template: Task, days: int = 7) -> List[Task]:
    """
    Generate one Task copy per day for a recurring task template.
    Uses a lambda-style timedelta offset so each copy gets the correct date.
    Only 'daily' recurrence is supported; non-recurring tasks return as-is.
    """
    if template.recurrence != "daily":
        return [template]
    return [
        Task(
            id=f"{template.id}-day{i}",
            name=template.name,
            duration_minutes=template.duration_minutes,
            priority=template.priority,
            task_type=template.task_type,
            pet_name=template.pet_name,
            earliest_start=template.earliest_start + timedelta(days=i) if template.earliest_start else None,
            latest_end=template.latest_end + timedelta(days=i)         if template.latest_end   else None,
            recurrence=template.recurrence,
        )
        for i in range(days)
    ]

# -- Owner & Pets -------------------------------------------------------------

owner = Owner("John Doe", daily_available_minutes=120)
pet1 = Pet("Fluffy", "Cat", age=3)
pet2 = Pet("Buddy", "Dog", age=5)
owner.pets = [pet1, pet2]          # multi-pet: owner tracks both animals

# -- Task Definitions (intentionally added OUT OF ORDER) ----------------------
#    Insertion order: evening -> morning -> afternoon -> night
#    sort_by_time() must reorder these correctly when printing.

task3 = Task(
    id="3",
    name="Play with Buddy",
    duration_minutes=20,
    priority=4,
    task_type="enrichment",
    pet_name="Buddy",
    earliest_start=datetime.combine(date.today(), time(18, 0)),
    latest_end=datetime.combine(date.today(), time(20, 0)),
)

task1 = Task(
    id="1",
    name="Morning Walk",
    duration_minutes=30,
    priority=3,
    task_type="exercise",
    pet_name="Buddy",
    earliest_start=datetime.combine(date.today(), time(8, 0)),
    latest_end=datetime.combine(date.today(), time(10, 0)),
)

task2 = Task(
    id="2",
    name="Feed Fluffy",
    duration_minutes=10,
    priority=5,
    task_type="feeding",
    pet_name="Fluffy",
    earliest_start=datetime.combine(date.today(), time(7, 0)),
    latest_end=datetime.combine(date.today(), time(8, 0)),
)

# Recurring task template — Fluffy's evening medication every day
task4_template = Task(
    id="4",
    name="Fluffy Evening Meds",
    duration_minutes=5,
    priority=5,
    task_type="medication",
    pet_name="Fluffy",
    earliest_start=datetime.combine(date.today(), time(19, 30)),
    latest_end=datetime.combine(date.today(), time(20, 0)),
    recurrence="daily",
)

# SAME-PET CONFLICT: Vet Call for Buddy overlaps Play with Buddy (18:00-20:00)
task5 = Task(
    id="5",
    name="Vet Call",
    duration_minutes=15,
    priority=4,
    task_type="health",
    pet_name="Buddy",
    earliest_start=datetime.combine(date.today(), time(19, 0)),
    latest_end=datetime.combine(date.today(), time(19, 30)),
)

# SAME-PET CONFLICT: Buddy's Bath at 08:30 overlaps Morning Walk (08:00-10:00)
task6 = Task(
    id="6",
    name="Buddy's Bath",
    duration_minutes=20,
    priority=2,
    task_type="grooming",
    pet_name="Buddy",
    earliest_start=datetime.combine(date.today(), time(8, 30)),
    latest_end=datetime.combine(date.today(), time(9, 0)),
)

# CROSS-PET CONFLICT: Fluffy's Grooming at 08:00 overlaps Morning Walk for Buddy
task7 = Task(
    id="7",
    name="Groom Fluffy",
    duration_minutes=15,
    priority=3,
    task_type="grooming",
    pet_name="Fluffy",
    earliest_start=datetime.combine(date.today(), time(8, 0)),
    latest_end=datetime.combine(date.today(), time(8, 45)),
)

# -- Build Schedule (tasks added OUT OF ORDER to prove sorting works) ---------

schedule = Schedule(date.today())

# Order added: deliberately scrambled to prove sorting works
schedule.add_task(task3)   # 18:00 Play with Buddy
schedule.add_task(task1)   # 08:00 Morning Walk
schedule.add_task(task2)   # 07:00 Feed Fluffy
schedule.add_task(task5)   # 19:00 Vet Call          (same-pet overlap with task3)
schedule.add_task(task6)   # 08:30 Buddy's Bath      (same-pet overlap with task1)
schedule.add_task(task7)   # 08:00 Groom Fluffy      (cross-pet overlap with task1)

# Expand recurring template and add only today's instance (19:30 -- added last)
for t in expand_recurring(task4_template, days=1):
    schedule.add_task(t)

# Mark morning feeding complete (non-recurring -- no next occurrence created)
schedule.mark_task_complete(task2.id)

# -- Display ------------------------------------------------------------------

print(f"Today's Schedule for {owner.name}")
print(f"Pets: {', '.join(p.name for p in owner.pets)}")
print(f"Total Scheduled Minutes: {schedule.total_scheduled_minutes}")

# Show raw insertion order first so the sorting improvement is visible
print("\n-- Raw Insertion Order (unsorted) ----------------------------------")
for t in schedule.tasks:
    start = t.earliest_start.strftime("%H:%M") if t.earliest_start else "?????"
    print(f"  {start}  {t.name}")

# 1. sort_by_time() -- Schedule method using lambda key on earliest_start
#    lambda t: t.earliest_start sorts datetime objects chronologically.
#    Tasks without a start time fall back to datetime.max and go last.
print("\n-- Sorted by Time (schedule.sort_by_time) --------------------------")
for t in schedule.sort_by_time():
    status = "DONE" if t.completed else "    "
    start  = t.earliest_start.strftime("%H:%M") if t.earliest_start else "?????"
    end    = t.latest_end.strftime("%H:%M")     if t.latest_end     else "?????"
    print(f"  [{status}] {start}-{end}  {t.name:<22} {t.duration_minutes:>3}min  P{t.priority}  [{t.pet_name}]")

# 2. filter_tasks(pet_name=...) -- filter by pet using the Schedule method
for pet in owner.pets:
    print(f"\n-- {pet.name}'s Tasks  [schedule.filter_tasks(pet_name='{pet.name}')] --")
    pet_tasks = sorted(
        schedule.filter_tasks(pet_name=pet.name),
        key=lambda t: t.earliest_start or datetime.max
    )
    for t in pet_tasks:
        start = t.earliest_start.strftime("%H:%M") if t.earliest_start else "?????"
        print(f"  {start}  {t.name} ({t.duration_minutes}min, {t.task_type})")

# 3. filter_tasks(completed=...) -- filter by completion status
print("\n-- Pending Tasks  [schedule.filter_tasks(completed=False)] ---------")
pending = sorted(
    schedule.filter_tasks(completed=False),
    key=lambda t: t.earliest_start or datetime.max
)
if pending:
    for t in pending:
        start = t.earliest_start.strftime("%H:%M") if t.earliest_start else "?????"
        print(f"  {start}  {t.name} [{t.pet_name}]")
else:
    print("  All tasks complete!")

print("\n-- Completed Tasks  [schedule.filter_tasks(completed=True)] --------")
done = sorted(
    schedule.filter_tasks(completed=True),
    key=lambda t: t.earliest_start or datetime.max
)
if done:
    for t in done:
        start = t.earliest_start.strftime("%H:%M") if t.earliest_start else "?????"
        print(f"  {start}  {t.name} [{t.pet_name}]")
else:
    print("  No completed tasks yet.")

# 4. filter_tasks(pet_name=..., completed=...) -- both filters together
print("\n-- Buddy's Pending Tasks  [schedule.filter_tasks(pet_name='Buddy', completed=False)]")
buddy_pending = sorted(
    schedule.filter_tasks(pet_name="Buddy", completed=False),
    key=lambda t: t.earliest_start or datetime.max
)
for t in buddy_pending:
    start = t.earliest_start.strftime("%H:%M") if t.earliest_start else "?????"
    print(f"  {start}  {t.name}")

# 5. Recurring task -- preview next 3 days
print("\n-- Recurring Task Preview: Fluffy Evening Meds (next 3 days) -------")
for t in expand_recurring(task4_template, days=3):
    start = t.earliest_start.strftime("%Y-%m-%d %H:%M") if t.earliest_start else "?????"
    print(f"  {start}  {t.name}")

# 6. Auto-recurrence demo -- completing a daily task creates the next day's copy
print("\n-- Auto-Recurrence Demo  [schedule.mark_task_complete()] -----------")
meds_task = next(t for t in schedule.tasks if t.name == "Fluffy Evening Meds" and not t.completed)
print(f"  Completing '{meds_task.name}' (id={meds_task.id}) for {meds_task.earliest_start.strftime('%Y-%m-%d %H:%M')}...")
next_task = schedule.mark_task_complete(meds_task.id)
if next_task:
    print(f"  -> Next occurrence auto-created: id={next_task.id}, "
          f"date={next_task.earliest_start.strftime('%Y-%m-%d %H:%M')}, "
          f"recurrence={next_task.recurrence}")
    print(f"  -> Schedule now has {len(schedule.tasks)} tasks ({schedule.total_scheduled_minutes} min)")
else:
    print(f"  -> No next occurrence (task is not recurring).")

# 7. Conflict detection -- returns warning strings, never crashes
print("\n-- Conflict Detection  [schedule.find_conflicts()] -----------------")
warnings = schedule.find_conflicts()
if warnings:
    for w in warnings:
        print(f"  {w}")
    print(f"\n  Total conflicts found: {len(warnings)}")
else:
    print("  No conflicts found.")
