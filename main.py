from pawpal_system import Priority, Frequency, Pet, Task, Scheduler, Owner

owner = Owner(name="John Doe", email="john.doe@example.com")
pet1 = Pet(name="dog", id="1", species="Dog", age=5, breed="Labrador", health_notes="Healthy", owner_name=owner.name)
pet2 = Pet(name="cat",id="2", species="Cat", age=3, breed="Siamese", health_notes="Allergic to certain foods", owner_name=owner.name)
task1 = Task(description="Feed the dog", priority=Priority.HIGH, duration=15, frequency=Frequency.DAILY)
task2 = Task(description="Take the dog for a walk", priority=Priority.NORMAL, duration=30, frequency=Frequency.DAILY)
task3 = Task(description="Give the cat medication", priority=Priority.HIGH, duration=10, frequency=Frequency.WEEKLY)

owner.add_pet(pet1)
owner.add_pet(pet2)
owner.add_task_to_pet(pet1, task1)
owner.add_task_to_pet(pet1, task2)
owner.add_task_to_pet(pet2, task3)

scheduler = owner.generate_scheduler("John's Pet Care Schedule")
print("Generated Schedule:")
for task in scheduler.get_schedule():
    print(f"- {task.description} (Priority: {task.priority.value}, Duration: {task.duration} mins, Frequency: {task.frequency.value})")
    