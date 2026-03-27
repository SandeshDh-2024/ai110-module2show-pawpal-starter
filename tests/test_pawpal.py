import pytest
from datetime import date, datetime, timedelta
from pawpal_system import Pet, Task, Owner, Schedule


def test_task_completion():
    task = Task(
        id="t1",
        name="Feed",
        duration_minutes=10,
        priority=5,
        task_type="feeding",
    )
    assert not task.completed
    task.mark_done()
    assert task.completed
    assert task.is_complete()


def test_pet_task_addition():
    pet = Pet(name="Buddy", species="Dog")
    assert pet.task_count() == 0

    task_a = Task(
        id="t2",
        name="Walk",
        duration_minutes=30,
        priority=4,
        task_type="exercise",
    )
    task_b = Task(
        id="t3",
        name="Play",
        duration_minutes=20,
        priority=3,
        task_type="enrichment",
    )

    pet.add_task(task_a)
    pet.add_task(task_b)

    assert pet.task_count() == 2


# ── Happy Path 1: Build a plan with 3 tasks at different priorities ──
def test_build_plan_sorts_by_priority_and_sums_minutes():
    owner = Owner(name="Alice", daily_available_minutes=120)
    pet = Pet(name="Buddy", species="Dog")

    low = Task(id="t10", name="Brush teeth", duration_minutes=5, priority=1, task_type="grooming", pet_name="Buddy")
    mid = Task(id="t11", name="Walk", duration_minutes=30, priority=5, task_type="exercise", pet_name="Buddy")
    high = Task(id="t12", name="Medication", duration_minutes=10, priority=9, task_type="medical", pet_name="Buddy")

    schedule = Schedule(schedule_date=date.today())
    schedule.build_plan([low, mid, high], owner, pet)

    # Highest priority should be first after build_plan sorts
    assert schedule.tasks[0].priority == 9
    assert schedule.tasks[1].priority == 5
    assert schedule.tasks[2].priority == 1

    # Total minutes = 5 + 30 + 10
    assert schedule.total_scheduled_minutes == 45


# ── Happy Path 2: Complete a daily recurring task ──
def test_daily_recurring_task_creates_next_occurrence():
    start = datetime(2026, 3, 27, 8, 0)
    end = datetime(2026, 3, 27, 8, 30)

    task = Task(
        id="t20",
        name="Morning walk",
        duration_minutes=30,
        priority=5,
        task_type="exercise",
        pet_name="Buddy",
        earliest_start=start,
        latest_end=end,
        recurrence="daily",
    )

    next_task = task.mark_done()

    # Original is marked done
    assert task.completed is True

    # A new task was returned
    assert next_task is not None

    # New task's times are shifted forward by exactly 1 day
    assert next_task.earliest_start == start + timedelta(days=1)
    assert next_task.latest_end == end + timedelta(days=1)

    # Recurrence carries forward so the chain continues
    assert next_task.recurrence == "daily"


# ── Edge Case 1: Pet with zero tasks ──
def test_pet_with_zero_tasks():
    pet = Pet(name="Ghost", species="Cat")

    # task_count is 0 on a fresh pet
    assert pet.task_count() == 0

    # build_plan with an empty list should not crash
    owner = Owner(name="Bob")
    schedule = Schedule(schedule_date=date.today())
    schedule.build_plan([], owner, pet)

    assert schedule.tasks == []
    assert schedule.total_scheduled_minutes == 0


# ── Edge Case 2: Two tasks at the exact same time, same pet ──
def test_same_time_same_pet_conflict():
    t1 = Task(
        id="t30",
        name="Vet visit",
        duration_minutes=60,
        priority=8,
        task_type="medical",
        pet_name="Buddy",
        earliest_start=datetime(2026, 3, 27, 10, 0),
        latest_end=datetime(2026, 3, 27, 11, 0),
    )
    t2 = Task(
        id="t31",
        name="Grooming",
        duration_minutes=60,
        priority=4,
        task_type="grooming",
        pet_name="Buddy",
        earliest_start=datetime(2026, 3, 27, 10, 0),
        latest_end=datetime(2026, 3, 27, 11, 0),
    )

    schedule = Schedule(schedule_date=date.today())
    schedule.add_task(t1)
    schedule.add_task(t2)

    warnings = schedule.find_conflicts()

    # There should be exactly one conflict warning
    assert len(warnings) == 1
    assert "SAME-PET CONFLICT" in warnings[0]


# ── Sorting Correctness: tasks returned in chronological order ──
def test_sort_by_time_returns_chronological_order():
    morning = Task(
        id="t40", name="Morning walk", duration_minutes=30,
        priority=3, task_type="exercise", pet_name="Buddy",
        earliest_start=datetime(2026, 3, 27, 7, 0),
        latest_end=datetime(2026, 3, 27, 7, 30),
    )
    evening = Task(
        id="t41", name="Evening feed", duration_minutes=15,
        priority=5, task_type="feeding", pet_name="Buddy",
        earliest_start=datetime(2026, 3, 27, 18, 0),
        latest_end=datetime(2026, 3, 27, 18, 15),
    )
    noon = Task(
        id="t42", name="Midday play", duration_minutes=20,
        priority=1, task_type="enrichment", pet_name="Buddy",
        earliest_start=datetime(2026, 3, 27, 12, 0),
        latest_end=datetime(2026, 3, 27, 12, 20),
    )
    no_time = Task(
        id="t43", name="Unscheduled bath", duration_minutes=45,
        priority=2, task_type="grooming", pet_name="Buddy",
    )

    # Add in non-chronological order on purpose
    schedule = Schedule(schedule_date=date.today())
    schedule.add_task(evening)
    schedule.add_task(no_time)
    schedule.add_task(morning)
    schedule.add_task(noon)

    sorted_tasks = schedule.sort_by_time()

    # Tasks with times come out earliest-first; no-time task goes last
    assert sorted_tasks[0].id == "t40"  # 07:00 morning
    assert sorted_tasks[1].id == "t42"  # 12:00 noon
    assert sorted_tasks[2].id == "t41"  # 18:00 evening
    assert sorted_tasks[3].id == "t43"  # no start time → last

