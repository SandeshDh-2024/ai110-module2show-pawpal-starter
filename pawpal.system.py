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

    def update_info(self, **data):
        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def needs_medication_now(self, current_time: datetime) -> bool:
        raise NotImplementedError

    def needs_grooming_due(self) -> bool:
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

    def update_task(self, **updates):
        for k, v in updates.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def mark_done(self):
        raise NotImplementedError

    def is_due(self, target_date: date) -> bool:
        raise NotImplementedError

    def score_priority(self) -> float:
        raise NotImplementedError

    def estimate_end_time(self, start_time: datetime) -> datetime:
        return start_time + timedelta(minutes=self.duration_minutes)

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
        self.daily_available_minutes = daily_available_minutes
        self.preferences = preferences or {}

    def update_profile(self, **data):
        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def set_availability(self, minutes: int):
        self.daily_available_minutes = minutes

    def set_preferences(self, preferences: Dict[str, Any]):
        self.preferences = preferences

    def get_constraints(self) -> Dict[str, Any]:
        raise NotImplementedError

class Schedule:
    def __init__(self, schedule_date: date):
        self.date = schedule_date
        self.tasks: List[Task] = []
        self.unplaced_tasks: List[Task] = []
        self.total_scheduled_minutes: int = 0
        self.reasoning: List[str] = []

    def build_plan(self, tasks: List[Task], owner: Owner, pet: Pet):
        raise NotImplementedError

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_task(self, task_id: str):
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def find_conflicts(self) -> List[Task]:
        raise NotImplementedError

    def optimize(self):
        raise NotImplementedError

    def to_display_list(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def explain_decision(self) -> str:
        raise NotImplementedError
