import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler, Priority, Frequency


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

    def test_mark_completed_on_recurring_task_creates_next_instance(self, sample_task, sample_pet):
        """Recurring tasks should create a next instance when completed."""
        sample_task.frequency = Frequency.DAILY
        sample_task.due_date = date.today()
        sample_task.pets.append(sample_pet)

        next_task = sample_task.mark_completed()

        assert sample_task.completed is True
        assert next_task is not None
        assert next_task.completed is False
        assert next_task.frequency == sample_task.frequency
        assert next_task.due_date == sample_task.due_date + timedelta(days=1)
        assert sample_task is not next_task
        assert sample_pet in next_task.pets
        assert next_task in sample_pet.tasks

    def test_mark_completed_on_non_recurring_task_does_not_create_next_instance(self, sample_task):
        """Non-recurring tasks should not create a next instance when completed."""
        sample_task.frequency = Frequency.ONCE

        next_task = sample_task.mark_completed()

        assert sample_task.completed is True
        assert next_task is None


class TestTaskAddition:
    """Tests for task addition to pets"""

    def test_add_task_to_pet_increases_task_count(self, sample_pet, sample_task):
        """Verify that adding a task to a pet increases the pet's task count"""
        assert len(sample_pet.tasks) == 0
        
        sample_pet.add_task(sample_task)
        
        assert len(sample_pet.tasks) == 1
        assert sample_task in sample_pet.tasks

    def test_scheduler_detects_same_pet_conflict_by_due_date(self, sample_pet):
        from datetime import date

        task_a = Task(name='A', description='Brush dog', pets=[], frequency=Frequency.DAILY, due_date=date.today())
        task_b = Task(name='B', description='Walk dog', pets=[sample_pet], frequency=Frequency.DAILY, due_date=date.today())
        task_a.add_pet(sample_pet)

        owner = Owner(name='Owner')
        owner.add_pet(sample_pet)
        owner.add_task_to_pet(sample_pet, task_a)
        owner.add_task_to_pet(sample_pet, task_b)

        scheduler = owner.generate_scheduler('Conflict')
        conflicts = scheduler.find_time_conflicts()

        assert scheduler.has_conflicts() is True
        assert len(conflicts['same_pet']) == 1
        assert len(conflicts['different_pets']) == 0
        assert "Same-pet conflicts" in scheduler.warning

    def test_scheduler_detects_different_pet_conflict_by_due_date(self, sample_pet):
        from datetime import date

        other_pet = Pet('Other', '2', 'Cat', 2)
        task_a = Task(name='A', description='Feed dog', pets=[sample_pet], frequency=Frequency.DAILY, due_date=date.today())
        task_b = Task(name='B', description='Feed cat', pets=[other_pet], frequency=Frequency.DAILY, due_date=date.today())

        owner = Owner(name='Owner')
        owner.add_pet(sample_pet)
        owner.add_pet(other_pet)
        owner.add_task_to_pet(sample_pet, task_a)
        owner.add_task_to_pet(other_pet, task_b)

        scheduler = owner.generate_scheduler('Conflict')
        conflicts = scheduler.find_time_conflicts()

        assert scheduler.has_conflicts() is True
        assert len(conflicts['same_pet']) == 0
        assert len(conflicts['different_pets']) == 1
        assert "Different-pets conflicts" in scheduler.warning

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

    def test_scheduler_prevents_adding_conflicting_task_same_pet(self, sample_pet):
        from datetime import date

        scheduler = Scheduler(name="Test")
        task1 = Task(name='A', description='Brush dog', pets=[sample_pet], frequency=Frequency.DAILY, due_date=date.today())
        task2 = Task(name='B', description='Walk dog', pets=[sample_pet], frequency=Frequency.DAILY, due_date=date.today())
        
        # Add first task
        assert scheduler.add_task(task1) is True
        assert task1 in scheduler.schedule
        
        # Try to add conflicting task
        assert scheduler.add_task(task2) is False
        assert task2 not in scheduler.schedule

    def test_scheduler_prevents_adding_conflicting_task_different_pets(self, sample_pet):
        from datetime import date

        other_pet = Pet('Other', '2', 'Cat', 2)
        scheduler = Scheduler(name="Test")
        task1 = Task(name='A', description='Feed dog', pets=[sample_pet], frequency=Frequency.DAILY, due_date=date.today())
        task2 = Task(name='B', description='Feed cat', pets=[other_pet], frequency=Frequency.DAILY, due_date=date.today())
        
        # Add first task
        assert scheduler.add_task(task1) is True
        assert task1 in scheduler.schedule
        
        # Try to add conflicting task
        assert scheduler.add_task(task2) is False
        assert task2 not in scheduler.schedule

