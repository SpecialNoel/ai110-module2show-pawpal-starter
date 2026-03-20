classDiagram
    class Priority {
        <<enumeration>>
        LOW
        NORMAL
        HIGH
    }
    
    class Frequency {
        <<enumeration>>
        ONCE
        DAILY
        WEEKLY
        MONTHLY
    }

    class Pet {
        - String name
        - String id
        - String species
        - int age
        - String breed
        - String health_notes
        - String owner_name
        - List~Task~ tasks
        + add_task(Task)
        + remove_task(Task)
        + edit_info()
        + edit_owner_name()
    }

    class Task {
        - String name
        - List~Pet~ pets
        - String description
        - Priority priority
        - int duration
        - Frequency frequency
        - Date due_date
        - bool completed
        + add_pet(Pet)
        + remove_pet(Pet)
        + edit_description()
        + edit_priority()
        + edit_duration()
        + edit_frequency()
        + is_recurring()
        + create_next_instance()
        + mark_completed()
    }

    class Scheduler {
        - String name
        - Owner owner
        - List~Task~ schedule
        - String explanation
        - String warning
        + generate_schedule()
        + generate_explanation()
        + edit_explanation()
        + has_conflicts()
        + find_time_conflicts()
        + get_conflict_warning()
        + get_schedule()
        + filter_by_pet_name()
        + filter_by_completion()
        + get_tasks_by_pet()
        + add_task()
    }

    class Owner {
        - List~Pet~ pets
        - String name
        - String email
        - List~Scheduler~ schedulers
        - List~String~ available_time
        + add_pet(Pet)
        + remove_pet(Pet)
        + edit_pet(Pet)
        + edit_owner_name()
        + edit_owner_email()
        + add_task_to_pet()
        + remove_task_from_pet()
        + get_all_tasks()
        + generate_scheduler()
        + remove_scheduler()
    }

    Priority --> Task : uses
    Frequency --> Task : uses
    Pet "1" --> "*" Task : has
    Task "*" --> "*" Pet : assigned to
    Owner "1" --> "*" Pet : owns
    Owner "1" --> "*" Scheduler : creates
    Scheduler "1" --> "*" Task : optimizes
    Scheduler "1" --> "1" Owner : references