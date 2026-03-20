# PawPal+ Project Reflection

## 1. System Design

### Core actions:
- User should be able to add/edit/remove/check tasks (walks, feeding, meds, enrichment, grooming, etc.)
- User should be able to add/edit information about a pet, as well as information about the owner
- User shoudl be able to request a daily plan that suits the user the best considering constraints and priorities, supported with explanation on why the plan works the best.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
  * Task:
    * Attributes: a list of Pet, description about the task, priority flag, duration.
    * Methods: add/edit/remove a Pet, edit the description, priority flag and duration.
  * Plan
    * Attributes: a list of Task, the generated schedule, explanation for this plan.
    * Methods: add/delete a Task, generate the schedule, generate and edit the explanation.
  * Owner
    * Attributes: a list of Pet, information about the owner, a list of Tasks, a list of Plans.
    * Methods: add/edit/remove a Pet, edit owner info, add/remove a Task, generate/remove a Plan.
  * Pet
    * Attributes: information about the pet, name of its owner.
    * Methods: edit info about the pet, edit info about the name of its owner.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

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
