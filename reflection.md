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

=> Our conflict detection compares every pair of tasks using their full time windows (earliest_start to latest_end), which correctly catches overlapping durations — not just exact time matches. However, the tradeoff is that it treats the entire window as "busy" even though the actual task duration may be shorter than the window. For example, "Morning Walk" is only 30 minutes but has a 2-hour window (08:00-10:00). Any task placed anywhere inside that window gets flagged as a conflict, even though in reality the walk could be shifted earlier or later within the window to avoid the overlap. We chose this approach because it is simple, reliable, and never misses a real conflict — it over-warns rather than under-warns. For a pet owner's daily schedule with a small number of tasks, a few extra warnings are easy to review manually, whereas a missed conflict (like double-booking a vet appointment during a walk) could be a real problem. A more advanced scheduler could try to find the optimal placement within each window to minimize conflicts, but that adds significant complexity (constraint-satisfaction solving) that is not justified for a lightweight daily pet care app.

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
