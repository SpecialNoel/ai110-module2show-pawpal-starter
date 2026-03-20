# PawPal+ Project Reflection

## 1. System Design

### Core actions:
- User should be able to add/edit/remove/check tasks (walks, feeding, meds, enrichment, grooming, etc.)
- User should be able to add/edit information about a pet, as well as information about the owner
- User shoudl be able to request a daily scheduler that suits the user the best considering constraints and priorities, supported with explanation on why the scheduler works the best.

**a. Initial design**

- Briefly describe your initial UML design.
  * The user should essentially be an Owner object, which can have lots of Pets and individual Tasks. The user can generate and save Schedulers based on the Tasks they choose as well as their constraints and priority.
- What classes did you include, and what responsibilities did you assign to each?
  * Task:
    * Attributes: a list of Pet, description about the task, priority flag, duration.
    * Methods: add/edit/remove a Pet, edit the description, priority flag and duration.
  * Scheduler
    * Attributes: a list of Task, the generated schedule, explanation for this scheduler.
    * Methods: add/delete a Task, generate the schedule, generate and edit the explanation.
  * Owner
    * Attributes: a list of Pet, information about the owner, a list of Tasks, a list of Schedulers.
    * Methods: add/edit/remove a Pet, edit owner info, add/remove a Task, generate/remove a Scheduler.
  * Pet
    * Attributes: information about the pet, name of its owner.
    * Methods: edit info about the pet, edit info about the name of its owner.

**b. Design changes**

- Did your design change during implementation?
  * Yes, I did change the design of the very first skeleton during implementation.
- If yes, describe at least one change and why you made it.
  * I replaced the type of Priority used in Task from string to enum because it is easier to read and edit enums than strings if the available values of Priority are all pre-defined constants.
  * I also added id field to Pet to avoid Pets having the same breed and name.
  * I added completed field to Task to keep track of whether the Task is completed or not.
  * I added name field to Scheduler to make it easier to reference each Scheduler.
  * I added available_time field to Owner to specify the time constaints the Owner has.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  * The scheduler considers time and priority for now.
- How did you decide which constraints mattered most?
  * Time should be mattering the most since the plan simply won't work if the owner has conflicts on time. 
    Priority comes next as the owner needs a best order to efficiently carry out tasks of their pets.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  * The scheduler considers only the exact due date rather than the overlapping durations when handling task conflicts.
- Why is that tradeoff reasonable for this scenario?
  * By sticking with checking only the exact due date, the user will have less complexity on using the app as they don't need to specify start and end time, and it eases the UI on the time input part.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  * Design brainstorming: Copilot suggests the following logic improvements to make the app more efficient to users of the app:
    * Implement the Knapsack algorithm in Scheduler for best ordering Tasks with respect to constaints.
    * Implement the calendar logic in Scheduler to support recurring tasks scheduling.
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  * tasks conflict handling
  * schedule filtering
  * recurring task scheduling
- Why were these tests important?
  * 

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
