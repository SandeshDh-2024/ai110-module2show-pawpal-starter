from pawpal_system import Pet, Task, Owner, Schedule
from datetime import date, datetime, time

# Create Owner
owner = Owner("John Doe", daily_available_minutes=120)

# Create Pets
pet1 = Pet("Fluffy", "Cat", age=3)
pet2 = Pet("Buddy", "Dog", age=5)

# Assign pet to owner (assuming one primary pet, but we have two)
owner.pet = pet1

# Create Tasks with different times
task1 = Task(
    id="1",
    name="Morning Walk",
    duration_minutes=30,
    priority=3,
    task_type="exercise",
    earliest_start=datetime.combine(date.today(), time(8, 0)),
    latest_end=datetime.combine(date.today(), time(10, 0))
)

task2 = Task(
    id="2",
    name="Feed Fluffy",
    duration_minutes=10,
    priority=5,
    task_type="feeding",
    earliest_start=datetime.combine(date.today(), time(7, 0)),
    latest_end=datetime.combine(date.today(), time(8, 0))
)

task3 = Task(
    id="3",
    name="Play with Buddy",
    duration_minutes=20,
    priority=4,
    task_type="enrichment",
    earliest_start=datetime.combine(date.today(), time(18, 0)),
    latest_end=datetime.combine(date.today(), time(20, 0))
)

# Create Schedule
schedule = Schedule(date.today())

# Add tasks to schedule
schedule.add_task(task1)
schedule.add_task(task2)
schedule.add_task(task3)

# Print Today's Schedule
print("Today's Schedule for", owner.name)
print("Pet:", owner.pet.name if owner.pet else "None")
print("Total Scheduled Minutes:", schedule.total_scheduled_minutes)
print("\nTasks:")
for task in schedule.tasks:
    print(f"- {task.name} ({task.duration_minutes} min, Priority: {task.priority}, Time: {task.earliest_start} - {task.latest_end})")
