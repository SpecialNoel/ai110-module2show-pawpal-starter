from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum
from datetime import date, timedelta

class Priority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class Frequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

@dataclass
class Pet:
    name: str
    id: str
    species: str
    age: int
    breed: str = ""
    health_notes: str = ""
    owner_name: str = ""
    tasks: List[Task] = field(default_factory=list)

    def edit_info(self, **kwargs) -> None:
        """Updates pet attributes using the provided keyword arguments."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def edit_owner_name(self, new_owner_name: str) -> None:
        """Sets the owner name for this pet."""
        self.owner_name = new_owner_name

    def add_task(self, task: Task) -> None:
        """Adds a task to this pet's task list if not already present."""
        if task not in self.tasks:
            self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Removes a task from this pet's task list if present."""
        if task in self.tasks:
            self.tasks.remove(task)


@dataclass
class Task:
    name: str = ""
    pets: List[Pet] = field(default_factory=list)
    description: str = ""
    priority: Priority = Priority.NORMAL
    duration: int = 0  # minutes
    frequency: Frequency = Frequency.ONCE
    due_date: date | None = None
    completed: bool = False

    def add_pet(self, pet: Pet) -> None:
        """Adds a pet to this task's pet list if not already present."""
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Removes a pet from this task's pet list if present."""
        if pet in self.pets:
            self.pets.remove(pet)

    def edit_description(self, description: str) -> None:
        """Updates the task description."""
        self.description = description

    def edit_priority(self, priority: Priority) -> None:
        """Sets the priority level of this task."""
        self.priority = priority

    def edit_duration(self, duration: int) -> None:
        """Updates the task duration in minutes."""
        self.duration = duration

    def edit_frequency(self, frequency: Frequency) -> None:
        """Sets the recurrence frequency for this task."""
        self.frequency = frequency

    def is_recurring(self) -> bool:
        """Returns True if the task is recurring, False if it occurs only once."""
        return self.frequency != Frequency.ONCE
        
    def create_next_instance(self) -> "Task":
        """Create a new task instance for the next recurrence period."""
        next_due_date = None
        if self.due_date is not None and self.is_recurring():
            if self.frequency == Frequency.DAILY:
                next_due_date = self.due_date + timedelta(days=1)
            elif self.frequency == Frequency.WEEKLY:
                next_due_date = self.due_date + timedelta(weeks=1)
            elif self.frequency == Frequency.MONTHLY:
                # approximate month as 30 days for now
                next_due_date = self.due_date + timedelta(days=30)

        return Task(
            name=self.name,
            pets=[],
            description=self.description,
            priority=self.priority,
            duration=self.duration,
            frequency=self.frequency,
            due_date=next_due_date,
            completed=False,
        )

    def mark_completed(self) -> Task | None:
        """Marks this task as completed and creates a next recurrence task if needed."""
        self.completed = True

        if not self.is_recurring():
            return None

        next_task = self.create_next_instance()
        for pet in self.pets:
            pet.add_task(next_task)
            next_task.add_pet(pet)

        return next_task


@dataclass
class Scheduler:
    name: str = ""
    owner: Owner = None
    schedule: List[Task] = field(default_factory=list)
    explanation: str = ""
    warning: str = ""
    
    def edit_name(self, name: str) -> None:
        """Updates the scheduler name."""
        self.name = name

    def generate_schedule(self) -> str:
        """Creates an optimized schedule sorted by priority (high first) and duration (shortest first)."""
        # Retrieve tasks from owner and sort by priority (HIGH first), then by duration (shortest first)
        if self.owner:
            tasks = self.owner.get_all_tasks()
            priority_order = {"low": 0, "normal": 1, "high": 2}
            self.schedule = sorted(tasks, key=lambda t: (-priority_order[t.priority.value], t.duration))
        else:
            self.schedule = []

        self.warning = self.get_conflict_warning()
        if self.warning and self.warning != "No schedule conflicts":
            print(f"Scheduler warning: {self.warning}")

        return self.warning

    def generate_explanation(self) -> str:
        """Generates a text explanation for the schedule."""
        self.explanation = "Generated by default scheduling."  # placeholder
        return self.explanation

    def edit_explanation(self, explanation: str) -> None:
        """Updates the explanation text for the schedule."""
        self.explanation = explanation

    def get_tasks_by_pet(self) -> Dict[str, List[Task]]:
        """Returns a dictionary mapping pet names to their associated tasks."""
        from collections import defaultdict
        tasks_by_pet = defaultdict(list)
        for task in self.schedule:
            for pet in task.pets:
                tasks_by_pet[pet.name].append(task)
        return dict(tasks_by_pet)

    def find_time_conflicts(self) -> Dict[str, List[tuple[Task, Task]]]:
        """
        Detect conflicts where two tasks are scheduled at the same due date/time.

        Groups tasks by due_date and checks for overlapping pet assignments.
        Conflicts are categorized as 'same_pet' (tasks sharing pets) or 'different_pets'
        (tasks for distinct pets).

        Returns:
            Dict[str, List[tuple[Task, Task]]]: A dictionary with keys 'same_pet' and 'different_pets',
            each containing lists of conflicting task pairs.
        """
        from collections import defaultdict

        # key: due_date
        by_schedule = defaultdict(list)
        for task in self.schedule:
            due = getattr(task, "due_date", None)
            if due is None:
                continue
            by_schedule[due].append(task)

        conflicts = {
            "same_pet": [],
            "different_pets": []
        }

        for scheduled_tasks in by_schedule.values():
            if len(scheduled_tasks) < 2:
                continue

            for i in range(len(scheduled_tasks)):
                for j in range(i + 1, len(scheduled_tasks)):
                    a = scheduled_tasks[i]
                    b = scheduled_tasks[j]
                    pets_a = {pet.id for pet in a.pets}
                    pets_b = {pet.id for pet in b.pets}
                    if pets_a & pets_b:
                        conflicts["same_pet"].append((a, b))
                    else:
                        conflicts["different_pets"].append((a, b))

        return conflicts

    def has_conflicts(self) -> bool:
        """
        Returns True when at least one time conflict exists.

        Checks the conflict map from find_time_conflicts for any entries.

        Returns:
            bool: True if there are conflicts, False otherwise.
        """
        conflict_map = self.find_time_conflicts()
        return bool(conflict_map["same_pet"] or conflict_map["different_pets"])

    def get_conflict_warning(self) -> str:
        """
        Returns a user-friendly warning string for tasks that conflict.

        Formats the conflicts from find_time_conflicts into readable messages,
        separating same-pet and different-pet conflicts.

        Returns:
            str: A warning message or "No schedule conflicts" if none.
        """
        conflicts = self.find_time_conflicts()
        warnings = []

        if conflicts["same_pet"]:
            same_pet_msgs = []
            for task_a, task_b in conflicts["same_pet"]:
                same_pet_msgs.append(f"'{task_a.description}' and '{task_b.description}'")
            warnings.append(f"Same-pet conflicts: {', '.join(same_pet_msgs)}")
        
        if conflicts["different_pets"]:
            diff_pet_msgs = []
            for task_a, task_b in conflicts["different_pets"]:
                diff_pet_msgs.append(f"'{task_a.description}' and '{task_b.description}'")
            warnings.append(f"Different-pets conflicts: {', '.join(diff_pet_msgs)}")

        return "; ".join(warnings) if warnings else "No schedule conflicts"

    def add_task(self, task: Task) -> bool:
        """
        Adds a task to the schedule if not already present and no conflicts.

        Checks for existing tasks on the same due_date and prevents addition
        if there are conflicts (same or different pets). Prints a message on failure.

        Args:
            task (Task): The task to add.

        Returns:
            bool: True if added successfully, False if conflicts or already present.
        """
        if task in self.schedule:
            return True  # Already present, no issue
        
        if task.due_date is None:
            # No due date, no conflict possible, add it
            self.schedule.append(task)
            return True
        
        # Check for conflicts on the same due_date
        existing_on_date = [t for t in self.schedule if getattr(t, "due_date", None) == task.due_date]
        
        for existing in existing_on_date:
            pets_existing = {pet.id for pet in existing.pets}
            pets_new = {pet.id for pet in task.pets}
            if pets_existing & pets_new:  # Same pet conflict
                print(f"Cannot add task '{task.description}': conflicts with existing task '{existing.description}' for the same pet on {task.due_date}")
                return False
            elif pets_existing and pets_new:  # Different pets conflict
                print(f"Cannot add task '{task.description}': conflicts with existing task '{existing.description}' for different pets on {task.due_date}")
                return False
        
        # No conflicts, add it
        self.schedule.append(task)
        return True

    def get_schedule(self) -> List[Task]:
        """Returns the current list of scheduled tasks."""
        return self.schedule
    
    def sort_by_time(self) -> None:
        """Sorts the schedule by time of day in HH:MM format."""
        self.schedule.sort(key=lambda t: t.time if hasattr(t, 'time') else "23:59")
        
    def filter_by_pet_name(self, pet_name: str) -> List[Task]:
        """Returns a list of tasks associated with a specific pet name."""
        return [task for task in self.schedule if any(pet.name == pet_name for pet in task.pets)]
    
    def filter_by_completion(self, completed: bool) -> List[Task]:
        """Returns a list of tasks filtered by their completion status."""
        return [task for task in self.schedule if task.completed == completed]


@dataclass
class Owner:
    pets: List[Pet] = field(default_factory=list)
    name: str = ""
    email: str = ""
    schedulers: List[Scheduler] = field(default_factory=list)
    available_time: List[str] = None

    def add_pet(self, pet: Pet) -> None:
        """Adds a pet to the owner's pet list if not already present."""
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Removes a pet from the owner's pet list if present."""
        if pet in self.pets:
            self.pets.remove(pet)

    def edit_pet(self, pet: Pet, **kwargs) -> None:
        """Updates attributes of one of the owner's pets."""
        if pet in self.pets:
            pet.edit_info(**kwargs)

    def edit_owner_name(self, new_name: str) -> None:
        """Updates the owner's name."""
        self.name = new_name
        
    def edit_onwer_email(self, new_email: str) -> None:
        """Updates the owner's email address."""
        self.email = new_email

    def add_task_to_pet(self, pet: Pet, task: Task) -> None:
        """Assigns a task to one of the owner's pets."""
        if pet in self.pets:
            pet.add_task(task)
            task.add_pet(pet)

    def remove_task_from_pet(self, pet: Pet, task: Task) -> None:
        """Unassigns a task from one of the owner's pets."""
        if pet in self.pets:
            pet.remove_task(task)
            task.remove_pet(pet)

    def get_all_tasks(self) -> List[Task]:
        """Retrieves all tasks across all of the owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def generate_scheduler(self, scheduler_name: str) -> Scheduler:
        """Creates and returns a new scheduler with optimized schedule."""
        p = Scheduler(owner=self, name=scheduler_name)
        p.generate_schedule()
        p.generate_explanation()
        self.schedulers.append(p)
        return p

    def remove_scheduler(self, scheduler: Scheduler) -> None:
        """Removes a scheduler from the owner's list."""
        if scheduler in self.schedulers:
            self.schedulers.remove(scheduler)

    def add_available_time(self, time_slot: str) -> None:
        """Adds a time slot to the owner's availability."""
        if self.available_time is None:
            self.available_time = []
        if time_slot not in self.available_time:
            self.available_time.append(time_slot)
    
    def remove_available_time(self, time_slot: str) -> None:
        """Removes a time slot from the owner's availability."""
        if self.available_time and time_slot in self.available_time:
            self.available_time.remove(time_slot)
