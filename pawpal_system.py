from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any

@dataclass
class Pet:
    name: str
    species: str
    breed: Optional[str] = None
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    health_notes: Optional[str] = None
    routine_preferences: Dict[str, Any] = field(default_factory=dict)
    tasks: List["Task"] = field(default_factory=list)

    def add_task(self, task: "Task"):
        self.tasks.append(task)

    def task_count(self) -> int:
        return len(self.tasks)

    def update_info(self, **data):
        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def needs_medication_now(self, current_time: datetime) -> bool:
        return False

    def needs_grooming_due(self) -> bool:
        return False

@dataclass
class Task:
    id: str
    name: str
    duration_minutes: int
    priority: int
    task_type: str
    completed: bool = False
    pet_name: Optional[str] = None
    earliest_start: Optional[datetime] = None
    latest_end: Optional[datetime] = None
    recurrence: Optional[str] = None  # "daily", "weekly", or None

    def mark_done(self) -> Optional["Task"]:
        """
        Mark this task complete.  If it recurs ("daily" or "weekly"), a new
        Task for the next occurrence is created and returned.
        Uses timedelta(days=1) for daily, timedelta(weeks=1) for weekly.
        Returns None for non-recurring tasks.
        """
        self.completed = True

        if self.recurrence not in ("daily", "weekly"):
            return None

        # Calculate the offset for the next occurrence
        if self.recurrence == "daily":
            delta = timedelta(days=1)       # today + 1 day
        else:                               # "weekly"
            delta = timedelta(weeks=1)      # today + 7 days

        next_task = Task(
            id=f"{self.id}-next",
            name=self.name,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            task_type=self.task_type,
            pet_name=self.pet_name,
            earliest_start=self.earliest_start + delta if self.earliest_start else None,
            latest_end=self.latest_end + delta         if self.latest_end     else None,
            recurrence=self.recurrence,                # keeps recurring
        )
        return next_task

    def is_complete(self) -> bool:
        """Return True if this task has been marked done."""
        return self.completed

class Owner:
    def __init__(
        self,
        name: str,
        contact_info: Optional[str] = None,
        daily_available_minutes: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.contact_info = contact_info
        self.daily_available_minutes = daily_available_minutes or 0
        self.preferences = preferences or {}
        self.pet: Optional[Pet] = None

    def update_profile(self, **data):
        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def set_availability(self, minutes: int):
        self.daily_available_minutes = minutes

    def set_preferences(self, preferences: Dict[str, Any]):
        self.preferences = preferences

    def get_constraints(self) -> Dict[str, Any]:
        return {
            "daily_available_minutes": self.daily_available_minutes,
            "preferences": self.preferences,
        }

class Schedule:
    def __init__(self, schedule_date: date):
        self.date = schedule_date
        self.tasks: List[Task] = []
        self.owner: Optional[Owner] = None
        self.pet: Optional[Pet] = None
        self.total_scheduled_minutes = 0
        self.unplaced_tasks: List[Task] = []
        self.reasoning: List[str] = []

    def build_plan(self, tasks: List[Task], owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)
        self.total_scheduled_minutes = sum(t.duration_minutes for t in self.tasks)
        self.reasoning = [
            f"Built plan with {len(self.tasks)} tasks. Total {self.total_scheduled_minutes} minutes."
        ]
        return self

    def add_task(self, task: Task):
        """Append a task to the schedule and update total scheduled minutes."""
        self.tasks.append(task)
        self.total_scheduled_minutes += task.duration_minutes
        self.reasoning.append(f"Added task {task.name} ({task.duration_minutes}m).")

    def mark_task_complete(self, task_id: str) -> Optional[Task]:
        """
        Find a task by ID, mark it done, and — if it recurs — automatically
        add the next occurrence to the schedule.
        Returns the newly created next-occurrence Task, or None.
        """
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task is None:
            return None

        next_task = task.mark_done()        # mark_done handles timedelta logic

        if next_task:
            self.add_task(next_task)
            self.reasoning.append(
                f"Recurring task '{task.name}' completed; "
                f"next occurrence created for "
                f"{next_task.earliest_start.strftime('%Y-%m-%d %H:%M') if next_task.earliest_start else 'TBD'}."
            )
        else:
            self.reasoning.append(f"Task '{task.name}' marked complete.")

        return next_task

    def remove_task(self, task_id: str):
        """Remove a task by ID and recalculate total scheduled minutes."""
        removed = [t for t in self.tasks if t.id == task_id]
        self.tasks = [t for t in self.tasks if t.id != task_id]
        if removed:
            self.total_scheduled_minutes = sum(t.duration_minutes for t in self.tasks)
            self.reasoning.append(f"Removed task id={task_id}.")

    def find_conflicts(self) -> List[str]:
        """
        Lightweight conflict detection: compare every pair of incomplete,
        timed tasks.  Two tasks conflict when their time windows overlap
        (a starts before b ends AND b starts before a ends).

        Returns a list of human-readable warning strings rather than
        raising exceptions, so the program never crashes.

        Each warning is labelled:
          - SAME-PET CONFLICT  -- one pet double-booked
          - CROSS-PET CONFLICT -- different pets at the same time
                                  (owner can only be in one place)
        """
        timed = [t for t in self.tasks
                 if t.earliest_start and t.latest_end and not t.completed]
        timed.sort(key=lambda t: t.earliest_start)

        warnings: List[str] = []
        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                a, b = timed[i], timed[j]

                # If b starts at or after a ends, no overlap (and none
                # with any later task either, since the list is sorted).
                if b.earliest_start >= a.latest_end:
                    break

                # Overlapping -- classify the conflict
                # Both pets must be set and equal for a same-pet conflict;
                # otherwise it's cross-pet (owner double-booked across pets).
                same_pet = (a.pet_name is not None
                            and a.pet_name == b.pet_name)
                label = "SAME-PET CONFLICT" if same_pet else "CROSS-PET CONFLICT"

                a_window = (f"{a.earliest_start.strftime('%H:%M')}-"
                            f"{a.latest_end.strftime('%H:%M')}")
                b_window = (f"{b.earliest_start.strftime('%H:%M')}-"
                            f"{b.latest_end.strftime('%H:%M')}")

                warnings.append(
                    f"WARNING {label}: '{a.name}' [{a.pet_name}] ({a_window}) "
                    f"overlaps '{b.name}' [{b.pet_name}] ({b_window})"
                )

        return warnings

    def sort_by_time(self) -> List["Task"]:
        """
        Return tasks sorted by earliest_start using a lambda as the sort key.
        Tasks stored in "HH:MM" style are compared as datetime objects so
        "08:00" correctly comes before "19:00".
        Tasks without a start time are pushed to the end of the list.
        """
        return sorted(self.tasks, key=lambda t: t.earliest_start or datetime.max)

    def filter_tasks(self, pet_name: Optional[str] = None, completed: Optional[bool] = None) -> List["Task"]:
        """
        Filter tasks by pet name, completion status, or both.
        - pet_name="Buddy"    -> only Buddy's tasks
        - completed=False     -> only pending tasks
        - both together       -> tasks matching both conditions
        """
        result = self.tasks
        if pet_name is not None:
            result = [t for t in result if t.pet_name == pet_name]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        return result

    def optimize(self):
        """Sort tasks in-place by descending priority (highest priority first)."""
        self.tasks.sort(key=lambda t: t.priority, reverse=True)
        self.reasoning.append("Optimized tasks by priority.")

    def to_display_list(self) -> List[Dict[str, Any]]:
        """Return a list of dicts summarizing each task for table display."""
        return [
            {
                "id": t.id,
                "pet": t.pet_name or "—",
                "name": t.name,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority,
            }
            for t in self.tasks
        ]

    def explain_decision(self) -> str:
        """Return a human-readable summary of all scheduling decisions made."""
        if not self.reasoning:
            return "No schedule decisions recorded."
        return " ".join(self.reasoning)
