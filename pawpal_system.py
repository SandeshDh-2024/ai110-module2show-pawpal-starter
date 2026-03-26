from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
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
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        "Add a task to this pet's task list."
        self.tasks.append(task)

    def task_count(self) -> int:
        "Return the number of tasks assigned to this pet."
        return len(self.tasks)

    def update_info(self, **data):
        "Update pet attributes from keyword arguments."
        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def needs_medication_now(self, current_time: datetime) -> bool:
        "Check if the pet requires medication now (not implemented)."
        raise NotImplementedError

    def needs_grooming_due(self) -> bool:
        "Check if the pet is due for grooming (not implemented)."
        raise NotImplementedError

@dataclass
class Task:
    id: str
    name: str
    duration_minutes: int
    priority: int
    task_type: str
    notes: Optional[str] = None
    earliest_start: Optional[datetime] = None
    latest_end: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    completed: bool = False

    def update_task(self, **updates):
        "Update task fields from keyword arguments."
        for k, v in updates.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def mark_done(self):
        "Mark task as completed."
        self.completed = True

    def mark_incomplete(self):
        "Mark task as not completed."
        self.completed = False

    def is_complete(self) -> bool:
        "Return true if task is marked completed."
        return self.completed

    def is_due(self, target_date: date) -> bool:
        "Determine if task is due on the given date."
        if not self.earliest_start or not self.latest_end:
            return False
        return self.earliest_start.date() <= target_date <= self.latest_end.date()

    def score_priority(self) -> float:
        "Return a numeric score for priority comparison."
        return float(self.priority)

    def estimate_end_time(self, start_time: datetime) -> datetime:
        "Estimate end time based on duration from a start time."
        return start_time + timedelta(minutes=self.duration_minutes)

class Owner:
    def __init__(
        self,
        name: str,
        contact_info: Optional[str] = None,
        daily_available_minutes: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ):
        "Initialize owner profile with optional availability and preferences."
        self.name = name
        self.contact_info = contact_info
        self.daily_available_minutes = daily_available_minutes
        self.preferences = preferences or {}
        self.pet: Optional[Pet] = None

    def update_profile(self, **data):
        "Update owner profile fields."
        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def set_availability(self, minutes: int):
        "Set daily available minutes for scheduling."
        self.daily_available_minutes = minutes

    def set_preferences(self, preferences: Dict[str, Any]):
        "Set owner preference dictionary."
        self.preferences = preferences

    def get_constraints(self) -> Dict[str, Any]:
        "Return a dict representing owner constraints."
        raise NotImplementedError

class Schedule:
    def __init__(self, schedule_date: date):
        "Initialize schedule for a specific date."
        self.date = schedule_date
        self.tasks: List[Task] = []
        self.unplaced_tasks: List[Task] = []
        self.total_scheduled_minutes: int = 0
        self.reasoning: List[str] = []
        self.owner: Optional[Owner] = None
        self.pet: Optional[Pet] = None

    def build_plan(self, tasks: List[Task], owner: Owner, pet: Pet):
        "Build the task plan for the schedule."
        self.owner = owner
        self.pet = pet
        raise NotImplementedError

    def add_task(self, task: Task):
        "Add a task to the schedule and update totals."
        self.tasks.append(task)
        self.total_scheduled_minutes += task.duration_minutes

    def remove_task(self, task_id: str):
        "Remove a task by ID and update totals."
        task_to_remove = next((t for t in self.tasks if t.id == task_id), None)
        if task_to_remove:
            self.tasks = [t for t in self.tasks if t.id != task_id]
            self.total_scheduled_minutes -= task_to_remove.duration_minutes

    def find_conflicts(self) -> List[Task]:
        "Identify conflicting tasks in the schedule."
        raise NotImplementedError

    def optimize(self):
        "Optimize schedule ordering and selection."
        raise NotImplementedError

    def to_display_list(self) -> List[Dict[str, Any]]:
        "Return schedule tasks in a display-friendly format."
        raise NotImplementedError

    def explain_decision(self) -> str:
        "Return human-readable explanation of scheduling decisions."
        raise NotImplementedError
