import pytest
from pawpal_system import Task, Pet, Priority


@pytest.fixture
def sample_pet():
    """Fixture providing a sample pet for testing"""
    return Pet("Buddy", "1", "Dog", 3)


@pytest.fixture
def sample_task():
    """Fixture providing a sample task for testing"""
    return Task(description="Walk dog")


@pytest.fixture
def high_priority_task():
    """Fixture providing a high priority task"""
    return Task(description="Vet appointment", priority=Priority.HIGH)


class TestTaskCompletion:
    """Tests for task completion functionality"""

    def test_mark_completed_changes_status_from_false_to_true(self, sample_task):
        """Verify that calling mark_completed() changes task.completed from False to True"""
        assert sample_task.completed is False
        sample_task.mark_completed()
        assert sample_task.completed is True

    def test_mark_completed_on_different_priority_task(self, high_priority_task):
        """Verify mark_completed() works on high priority tasks"""
        assert high_priority_task.completed is False
        high_priority_task.mark_completed()
        assert high_priority_task.completed is True


class TestTaskAddition:
    """Tests for task addition to pets"""

    def test_add_task_to_pet_increases_task_count(self, sample_pet, sample_task):
        """Verify that adding a task to a pet increases the pet's task count"""
        assert len(sample_pet.tasks) == 0
        
        sample_pet.add_task(sample_task)
        
        assert len(sample_pet.tasks) == 1
        assert sample_task in sample_pet.tasks

    @pytest.mark.parametrize("task_count", [1, 2, 3])
    def test_add_multiple_tasks_to_pet_increases_count(self, sample_pet, task_count):
        """Verify that adding multiple tasks increases the pet's task count correctly"""
        assert len(sample_pet.tasks) == 0
        
        tasks = [Task(description=f"Task {i}") for i in range(task_count)]
        
        for i, task in enumerate(tasks):
            sample_pet.add_task(task)
            assert len(sample_pet.tasks) == i + 1
        
        for task in tasks:
            assert task in sample_pet.tasks

