# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
=> The initial UML design uses a class diagram with four main classes: Owner, Pet, Task, and Schedule. Owner owns a Pet and both relate to a Schedule, which contains multiple Tasks.
- What classes did you include, and what responsibilities did you assign to each?
=> Classes included: Owner (manages owner profile and constraints), Pet (holds pet information and needs), Task (represents individual care activities with attributes like duration and priority), Schedule (builds and manages the daily plan, including optimization and explanations).

Core user actions:
- Add owner and pet information, including preferences and constraints.
- Add or edit pet care tasks (walks, feeding, medications, grooming, enrichment) with duration and priority.
- Generate and view a daily schedule/plan for today’s care tasks, including explanations for decisions.

**b. Design changes**

- Yes, the design changed during implementation to add missing relationships and fix logic bottlenecks. Added a `pet` attribute to `Owner` to explicitly model the ownership relationship from the UML. Added `owner` and `pet` attributes to `Schedule`, set during `build_plan`, for better encapsulation. Updated `add_task` and `remove_task` in `Schedule` to maintain `total_scheduled_minutes` accurately by incrementing/decrementing the duration. These changes improve data integrity and align the code more closely with the UML relationships.

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
