import pytest
from pawpal_system import Pet, Task


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

