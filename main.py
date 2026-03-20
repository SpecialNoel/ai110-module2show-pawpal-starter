from pawpal_system import Priority, Frequency, Pet, Task, Scheduler, Owner
from datetime import date, timedelta

owner = Owner(name="John Doe", email="john.doe@example.com")

pet1 = Pet(name="dog", id="1", species="Dog", age=5, breed="Labrador", health_notes="Healthy", owner_name=owner.name)
pet2 = Pet(name="cat",id="2", species="Cat", age=3, breed="Siamese", health_notes="Allergic to certain foods", owner_name=owner.name)

task1 = Task(name="task1", description="Feed the dog", priority=Priority.HIGH, duration=15, frequency=Frequency.DAILY)
task2 = Task(name="task2", description="Take the dog for a walk", priority=Priority.NORMAL, duration=30, frequency=Frequency.DAILY)
task3 = Task(name="task3", description="Give the cat medication", priority=Priority.HIGH, duration=10, frequency=Frequency.WEEKLY)

owner.add_pet(pet1)
owner.add_pet(pet2)
owner.add_task_to_pet(pet1, task1)
owner.add_task_to_pet(pet1, task2)
owner.add_task_to_pet(pet2, task3)

scheduler = owner.generate_scheduler("John's Pet Care Schedule") # this method generates a Scheduler inside the owner object
# print("Generated Schedule:")
# for task in scheduler.get_schedule():
#     print(f"- {task.description} (Priority: {task.priority.value}, Duration: {task.duration} mins, Frequency: {task.frequency.value})")
    
    
    
owner2 = Owner(name="Jane")

pet3 = Pet(name="cat2", id="3", species="Cat", age=2, breed="Persian", health_notes="Needs regular grooming", owner_name=owner2.name)
pet4 = Pet(name="dog2", id="4", species="Dog", age=4, breed="Beagle", health_notes="Healthy", owner_name=owner2.name)
    
task4 = Task(name="task4", description="Play with the cat", priority=Priority.LOW, duration=30, frequency=Frequency.DAILY, due_date=date.today())
task5 = Task(name="task5", description="Play with the dog", priority=Priority.LOW, duration=20, frequency=Frequency.DAILY, due_date=date.today())
task6 = Task(name="task6", description="Groom the cat", priority=Priority.LOW, duration=20, frequency=Frequency.DAILY, due_date=date.today()+ timedelta(days=1))

owner2.add_pet(pet3)
owner2.add_pet(pet4)
owner2.add_task_to_pet(pet3, task4)
owner2.add_task_to_pet(pet3, task6)
owner2.add_task_to_pet(pet4, task5)

scheduler2 = owner2.generate_scheduler("Jane's Pet Care Schedule")
print("\nSchedule after adding new tasks, sorted by time:")
scheduler2.sort_by_time()
for task in scheduler2.get_schedule():
    print(f"- {task.description} (Priority: {task.priority.value}, Duration: {task.duration} mins, Frequency: {task.frequency.value})")

print("\nSchedule after filtering by pet name 'cat2':")
filtered_scheduler = scheduler2.filter_by_pet_name("cat2")
for task in filtered_scheduler:
    print(f"- {task.description} (Priority: {task.priority.value}, Duration: {task.duration} mins, Frequency: {task.frequency.value})")