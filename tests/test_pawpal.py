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


class TestRecurringTaskEdgeCases:
    """Tests for edge cases in recurring task behavior"""

    def test_recurring_task_with_no_due_date_does_not_crash(self, sample_pet):
        """Recurring task with due_date=None should not crash on mark_completed."""
        task = Task(description="Daily feeding", frequency=Frequency.DAILY, due_date=None, pets=[sample_pet])
        
        next_task = task.mark_completed()
        
        assert task.completed is True
        assert next_task is not None
        assert next_task.due_date is None  # No due date remains None

    def test_recurring_chain_multiple_completions(self, sample_pet):
        """Test creating a chain of recurring task instances over multiple completions."""
        original_date = date.today()
        task1 = Task(
            description="Daily walk",
            frequency=Frequency.DAILY,
            due_date=original_date,
            pets=[sample_pet]
        )
        
        # Complete first instance
        task2 = task1.mark_completed()
        assert task2.due_date == original_date + timedelta(days=1)
        
        # Complete second instance
        task3 = task2.mark_completed()
        assert task3.due_date == original_date + timedelta(days=2)
        
        # Verify original task unchanged
        assert task1.completed is True
        assert task2.completed is True
        assert task3.completed is False

    def test_weekly_recurrence_creates_correct_next_date(self, sample_pet):
        """Weekly recurring tasks should add 7 days to the next due_date."""
        original_date = date(2026, 3, 20)
        task = Task(
            description="Weekly grooming",
            frequency=Frequency.WEEKLY,
            due_date=original_date,
            pets=[sample_pet]
        )
        
        next_task = task.mark_completed()
        
        assert next_task.due_date == original_date + timedelta(weeks=1)
        assert next_task.due_date == date(2026, 3, 27)

    def test_monthly_recurrence_creates_correct_next_date(self, sample_pet):
        """Monthly recurring tasks should add ~30 days to the next due_date."""
        original_date = date(2026, 3, 20)
        task = Task(
            description="Monthly vet checkup",
            frequency=Frequency.MONTHLY,
            due_date=original_date,
            pets=[sample_pet]
        )
        
        next_task = task.mark_completed()
        
        # Current implementation uses 30-day approximation
        assert next_task.due_date == original_date + timedelta(days=30)

    def test_next_instance_has_independent_pet_list(self, sample_pet):
        """Newly created recurring task should have its own pet list, not shared reference."""
        task = Task(
            description="Daily play",
            frequency=Frequency.DAILY,
            due_date=date.today(),
            pets=[sample_pet]
        )
        
        next_task = task.mark_completed()
        
        # Next task starts with empty pet list, then same pet is added
        assert len(next_task.pets) == 1
        assert sample_pet in next_task.pets
        
        # Modify next task's pets and verify original unaffected
        next_task.pets.clear()
        assert len(task.pets) == 1
        assert sample_pet in task.pets


class TestSchedulerSorting:
    """Tests for scheduler sorting and task ordering"""

    def test_generate_schedule_sorts_by_priority_then_duration(self, sample_pet):
        """Schedule should sort HIGH priority first, then NORMAL, then LOW, and within same priority by shortest duration."""
        owner = Owner(name="Owner")
        owner.add_pet(sample_pet)
        
        # Create tasks with varying priorities and durations
        task_low = Task(description="Low priority long", priority=Priority.LOW, duration=30, frequency=Frequency.ONCE)
        task_normal_short = Task(description="Normal short", priority=Priority.NORMAL, duration=5, frequency=Frequency.ONCE)
        task_high_long = Task(description="High priority long", priority=Priority.HIGH, duration=20, frequency=Frequency.ONCE)
        task_high_short = Task(description="High priority short", priority=Priority.HIGH, duration=10, frequency=Frequency.ONCE)
        task_normal_long = Task(description="Normal long", priority=Priority.NORMAL, duration=15, frequency=Frequency.ONCE)
        
        owner.add_task_to_pet(sample_pet, task_low)
        owner.add_task_to_pet(sample_pet, task_normal_short)
        owner.add_task_to_pet(sample_pet, task_high_long)
        owner.add_task_to_pet(sample_pet, task_high_short)
        owner.add_task_to_pet(sample_pet, task_normal_long)
        
        scheduler = owner.generate_scheduler("Test")
        schedule = scheduler.get_schedule()
        
        # Verify order: HIGH (short first), then NORMAL (short first), then LOW
        assert schedule[0] == task_high_short  # HIGH, 10m
        assert schedule[1] == task_high_long   # HIGH, 20m
        assert schedule[2] == task_normal_short  # NORMAL, 5m
        assert schedule[3] == task_normal_long   # NORMAL, 15m
        assert schedule[4] == task_low  # LOW, 30m

    def test_generate_schedule_with_empty_task_list(self):
        """Scheduler with no tasks should produce empty schedule."""
        owner = Owner(name="Empty Owner")
        scheduler = owner.generate_scheduler("Empty Schedule")
        
        assert len(scheduler.get_schedule()) == 0
        assert scheduler.warning == "No schedule conflicts"

    def test_generate_schedule_same_priority_same_duration_preserves_insertion(self, sample_pet):
        """Tasks with identical priority and duration should maintain relative insertion order."""
        owner = Owner(name="Owner")
        owner.add_pet(sample_pet)
        
        task_a = Task(description="Task A", priority=Priority.NORMAL, duration=10, frequency=Frequency.ONCE)
        task_b = Task(description="Task B", priority=Priority.NORMAL, duration=10, frequency=Frequency.ONCE)
        task_c = Task(description="Task C", priority=Priority.NORMAL, duration=10, frequency=Frequency.ONCE)
        
        owner.add_task_to_pet(sample_pet, task_a)
        owner.add_task_to_pet(sample_pet, task_b)
        owner.add_task_to_pet(sample_pet, task_c)
        
        scheduler = owner.generate_scheduler("Stable Sort")
        schedule = scheduler.get_schedule()
        
        # With stable sort, original insertion order preserved
        assert schedule[0].description == "Task A"
        assert schedule[1].description == "Task B"
        assert schedule[2].description == "Task C"

    def test_sort_by_time_with_missing_time_attribute(self, sample_pet):
        """sort_by_time should handle tasks without 'time' attribute using fallback '23:59'."""
        scheduler = Scheduler(name="Test")
        
        # Create tasks without 'time' attribute
        task1 = Task(description="No time attr 1", pets=[sample_pet])
        task2 = Task(description="No time attr 2", pets=[sample_pet])
        
        scheduler.schedule = [task2, task1]
        scheduler.sort_by_time()
        
        # All should fallback to "23:59" so order preserved (stable sort)
        assert scheduler.schedule[0] == task2
        assert scheduler.schedule[1] == task1

    def test_sort_by_time_mixed_with_and_without_time_attribute(self, sample_pet):
        """sort_by_time should sort tasks with 'time' before those without (if times differ)."""
        scheduler = Scheduler(name="Test")
        
        # Dynamically add 'time' attribute to one task
        task_morning = Task(description="Morning task", pets=[sample_pet])
        task_morning.time = "08:00"
        
        task_no_time = Task(description="No specific time", pets=[sample_pet])
        
        scheduler.schedule = [task_no_time, task_morning]
        scheduler.sort_by_time()
        
        # Morning (08:00) should come before fallback (23:59)
        assert scheduler.schedule[0].description == "Morning task"
        assert scheduler.schedule[1].description == "No specific time"


class TestConflictDetectionEdgeCases:
    """Tests for edge cases in conflict detection and scheduling"""

    def test_add_task_with_no_due_date_does_not_conflict(self, sample_pet):
        """Tasks with due_date=None should be added without conflict checking."""
        scheduler = Scheduler(name="Test")
        
        task1 = Task(description="Task with date", pets=[sample_pet], due_date=date.today())
        task2 = Task(description="Task without date", pets=[sample_pet], due_date=None)
        
        assert scheduler.add_task(task1) is True
        assert scheduler.add_task(task2) is True
        assert len(scheduler.schedule) == 2

    def test_add_duplicate_task_returns_true_without_modification(self, sample_pet):
        """Adding the same task object twice should return True and not duplicate."""
        scheduler = Scheduler(name="Test")
        task = Task(description="Unique task", pets=[sample_pet], due_date=date.today())
        
        result1 = scheduler.add_task(task)
        result2 = scheduler.add_task(task)
        
        assert result1 is True
        assert result2 is True
        assert len(scheduler.schedule) == 1
        assert scheduler.schedule[0] is task

    def test_find_time_conflicts_with_multiple_pets_per_task(self, sample_pet):
        """Task with multiple pets should conflict with any task sharing those pets."""
        other_pet = Pet('Other', '2', 'Cat', 2)
        third_pet = Pet('Third', '3', 'Bird', 1)
        
        scheduler = Scheduler(name="Test")
        
        # Task A: two pets
        task_a = Task(description="Multi-pet A", pets=[sample_pet, other_pet], due_date=date.today())
        # Task B: overlaps with one pet from A
        task_b = Task(description="Single B", pets=[third_pet], due_date=date.today())
        # Task C: overlaps with pets from both A and B
        task_c = Task(description="Multi-pet C", pets=[sample_pet, third_pet], due_date=date.today())
        
        scheduler.schedule = [task_a, task_b, task_c]
        conflicts = scheduler.find_time_conflicts()
        
        # Same-pet conflicts: (A,C) share sample_pet, (B,C) share third_pet
        assert len(conflicts['same_pet']) == 2
        # Different-pet conflicts: (A,B) share no pets
        assert len(conflicts['different_pets']) == 1

    def test_find_time_conflicts_with_empty_pet_lists(self):
        """Tasks with empty pet lists on same date are classified as different_pets conflicts."""
        scheduler = Scheduler(name="Test")
        
        task_a = Task(description="Empty pets A", pets=[], due_date=date.today())
        task_b = Task(description="Empty pets B", pets=[], due_date=date.today())
        
        scheduler.schedule = [task_a, task_b]
        conflicts = scheduler.find_time_conflicts()
        
        # Empty pet sets don't intersect, so goes to different_pets category
        assert len(conflicts['same_pet']) == 0
        assert len(conflicts['different_pets']) == 1

    def test_conflict_warning_no_conflicts_message(self):
        """Conflict warning should return 'No schedule conflicts' when none exist."""
        scheduler = Scheduler(name="Test")
        scheduler.schedule = []
        
        warning = scheduler.get_conflict_warning()
        assert warning == "No schedule conflicts"

    def test_conflict_warning_both_same_and_different_pets(self, sample_pet):
        """Warning should list both same-pet and different-pet conflicts separated."""
        other_pet = Pet('Other', '2', 'Cat', 2)
        
        scheduler = Scheduler(name="Test")
        
        # Same-pet conflict
        task_a = Task(description="Task A", pets=[sample_pet], due_date=date.today())
        task_b = Task(description="Task B", pets=[sample_pet], due_date=date.today())
        
        # Different-pet conflict
        task_c = Task(description="Task C", pets=[other_pet], due_date=date.today())
        
        scheduler.schedule = [task_a, task_b, task_c]
        warning = scheduler.get_conflict_warning()
        
        assert "Same-pet conflicts" in warning
        assert "Different-pets conflicts" in warning
        assert ";" in warning  # Separator between the two types


class TestFilteringOperations:
    """Tests for filter operations on schedules"""

    def test_filter_by_pet_name_returns_matching_tasks(self, sample_pet):
        """filter_by_pet_name should return only tasks for specified pet."""
        other_pet = Pet('Other', '2', 'Cat', 2)
        
        scheduler = Scheduler(name="Test")
        task_a = Task(description="Task for Buddy", pets=[sample_pet])
        task_b = Task(description="Task for Other", pets=[other_pet])
        task_c = Task(description="Another Buddy task", pets=[sample_pet])
        
        scheduler.schedule = [task_a, task_b, task_c]
        
        buddy_tasks = scheduler.filter_by_pet_name("Buddy")
        assert len(buddy_tasks) == 2
        assert task_a in buddy_tasks
        assert task_c in buddy_tasks
        assert task_b not in buddy_tasks

    def test_filter_by_pet_name_no_matches_returns_empty(self):
        """filter_by_pet_name should return empty list when no tasks match."""
        scheduler = Scheduler(name="Test")
        scheduler.schedule = [
            Task(description="Task A", pets=[Pet('Dog', '1', 'Dog', 3)])
        ]
        
        result = scheduler.filter_by_pet_name("NonexistentPet")
        assert result == []

    def test_filter_by_completion_true(self, sample_pet):
        """filter_by_completion(True) should return only completed tasks."""
        scheduler = Scheduler(name="Test")
        
        task_a = Task(description="Done", pets=[sample_pet], completed=True)
        task_b = Task(description="Pending", pets=[sample_pet], completed=False)
        task_c = Task(description="Also done", pets=[sample_pet], completed=True)
        
        scheduler.schedule = [task_a, task_b, task_c]
        
        completed = scheduler.filter_by_completion(True)
        assert len(completed) == 2
        assert task_a in completed
        assert task_c in completed

    def test_filter_by_completion_false(self, sample_pet):
        """filter_by_completion(False) should return only incomplete tasks."""
        scheduler = Scheduler(name="Test")
        
        task_a = Task(description="Done", pets=[sample_pet], completed=True)
        task_b = Task(description="Pending", pets=[sample_pet], completed=False)
        task_c = Task(description="Also pending", pets=[sample_pet], completed=False)
        
        scheduler.schedule = [task_a, task_b, task_c]
        
        pending = scheduler.filter_by_completion(False)
        assert len(pending) == 2
        assert task_b in pending
        assert task_c in pending

    def test_filter_by_completion_empty_schedule(self):
        """filter_by_completion on empty schedule should return empty list."""
        scheduler = Scheduler(name="Test")
        
        assert scheduler.filter_by_completion(True) == []
        assert scheduler.filter_by_completion(False) == []


class TestIntegrationScenarios:
    """Integration tests combining multiple features"""

    def test_full_workflow_pets_tasks_schedule_conflicts_and_sort(self):
        """Test complete workflow: create pets, assign tasks, generate schedule, detect conflicts."""
        # Setup
        owner = Owner(name="John")
        pet_a = Pet("Buddy", "1", "Dog", 3)
        pet_b = Pet("Whiskers", "2", "Cat", 5)
        owner.add_pet(pet_a)
        owner.add_pet(pet_b)
        
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        # Task 1: HIGH priority, short duration, for pet_a on today
        task1 = Task(
            description="Vet appointment",
            priority=Priority.HIGH,
            duration=10,
            frequency=Frequency.ONCE,
            due_date=today,
            pets=[pet_a]
        )
        
        # Task 2: NORMAL priority, medium duration, for pet_a on today (CONFLICT with task1)
        task2 = Task(
            description="Dog grooming",
            priority=Priority.NORMAL,
            duration=20,
            frequency=Frequency.ONCE,
            due_date=today,
            pets=[pet_a]
        )
        
        # Task 3: LOW priority, long duration, for pet_b on tomorrow (no conflict, different date)
        task3 = Task(
            description="Cat food",
            priority=Priority.LOW,
            duration=5,
            frequency=Frequency.ONCE,
            due_date=tomorrow,
            pets=[pet_b]
        )
        
        owner.add_task_to_pet(pet_a, task1)
        owner.add_task_to_pet(pet_a, task2)
        owner.add_task_to_pet(pet_b, task3)
        
        # Generate schedule
        scheduler = owner.generate_scheduler("Full Schedule")
        
        # Verify schedule order: sorted by priority (HIGH first) then duration (shortest first)
        schedule = scheduler.get_schedule()
        assert schedule[0] == task1  # HIGH priority, 10m
        assert schedule[1] == task2  # NORMAL priority, 20m
        assert schedule[2] == task3  # LOW priority, 5m
        
        # Verify conflict detection: only task1 and task2 conflict (same pet, same date)
        assert scheduler.has_conflicts() is True
        conflicts = scheduler.find_time_conflicts()
        assert len(conflicts['same_pet']) == 1  # task1 and task2 on same date for pet_a

    def test_recurring_task_marked_complete_then_scheduled(self, sample_pet):
        """Test recurring task completion creating next instance that gets scheduled."""
        owner = Owner(name="Owner")
        owner.add_pet(sample_pet)
        
        today = date.today()
        task1 = Task(
            description="Daily feeding",
            priority=Priority.NORMAL,
            duration=5,
            frequency=Frequency.DAILY,
            due_date=today,
            pets=[sample_pet]
        )
        
        owner.add_task_to_pet(sample_pet, task1)
        
        # Generate initial schedule
        scheduler1 = owner.generate_scheduler("Day 1")
        assert task1 in scheduler1.get_schedule()
        
        # Mark task1 complete
        task2 = task1.mark_completed()
        assert task2 is not None
        assert task2.due_date == today + timedelta(days=1)
        
        # Manually add task2 to owner's pet
        owner.add_task_to_pet(sample_pet, task2)
        
        # New schedule should contain task2
        scheduler2 = owner.generate_scheduler("Day 2")
        assert task2 in scheduler2.get_schedule()
        assert task1 not in [t for t in scheduler2.get_schedule() if not t.completed]

