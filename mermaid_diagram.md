classDiagram
    class Pet {
        - String name
        - String species
        - int age
        - String breed
        - String healthNotes
        - String ownerName
        + editInfo()
        + editOwnerName()
    }

    class Task {
        - List~Pet~ pets
        - String description
        - String priority
        - int duration
        + addPet(Pet)
        + removePet(Pet)
        + editDescription(String)
        + editPriority(String)
        + editDuration(int)
    }

    class Scheduler {
        - List~Task~ tasks
        - List~Task~ schedule
        - String explanation
        + addTask(Task)
        + deleteTask(Task)
        + generateSchedule()
        + generateExplanation()
        + editExplanation(String)
    }

    class Owner {
        - List~Pet~ pets
        - String ownerInfo
        - List~Task~ tasks
        - List~Plan~ plans
        + addPet(Pet)
        + removePet(Pet)
        + editPet(Pet)
        + editOwnerInfo(String)
        + addTask(Task)
        + removeTask(Task)
        + generatePlan()
        + removePlan(Plan)
    }

    Owner "1" --> "*" Pet
    Owner "1" --> "*" Task
    Owner "1" --> "*" Scheduler
    Scheduler "1" --> "*" Task
    Task "*" --> "*" Pet