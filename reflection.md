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

=> Our conflict detection compares every pair of tasks using their full time windows (earliest_start to latest_end), which correctly catches overlapping durations — not just exact time matches. However, the tradeoff is that it treats the entire window as "busy" even though the actual task duration may be shorter than the window. For example, "Morning Walk" is only 30 minutes but has a 2-hour window (08:00-10:00). Any task placed anywhere inside that window gets flagged as a conflict, even though in reality the walk could be shifted earlier or later within the window to avoid the overlap. This approach is reasoanable because it is simple, reliable, and never misses a real conflict — it over-warns rather than under-warns. For a pet owner's daily schedule with a small number of tasks, a few extra warnings are easy to review manually, whereas a missed conflict (like double-booking a vet appointment during a walk) could be a real problem. A more advanced scheduler could try to find the optimal placement within each window to minimize conflicts, but that adds significant complexity (constraint-satisfaction solving) that is not justified for a lightweight daily pet care app.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

=> I used AI pretty heavily throughout the project but in different ways at different stages. Early on I used it for brainstorming the UML design and then I'd describe what PawPal needed to do and ask it to help me figure out which classes made sense and what methods each one should have. During implementation it was most useful for writing the scheduling logic, especially the conflict detection and recurring task pieces where the timedelta math was tricky to get right. I also used it to help draft tests after I had the core code working. The prompts that helped the most were specific ones, like "what are the edge cases for a pet scheduler with sorting and recurring tasks" gave me way better results than just asking "help me test my code." Asking it to review my code and list what behaviors to verify was also really productive because it caught things I hadn't thought about, like what happens when a task has no start time.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

=> When the AI suggested changing the demo screenshot path in my README from the original path to a different format, I rejected that edit because I knew the original path was what my course platform expected. It was trying to be helpful by switching to a simpler Markdown image syntax, but that would have broken how the image loads on the platform I'm actually submitting to. I verified by checking that clicking the existing link already opened the image correctly, so I knew the path was right and the rendering issue was just a preview quirk, not a wrong path. That was a good reminder that the AI doesn't always know the context of where your work gets deployed.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

=> I tested seven behaviors total. The happy path tests cover basic task completion, adding tasks to a pet, building a plan that sorts by priority and sums up the total minutes correctly, and completing a daily recurring task to make sure it generates the next day's occurrence. The edge case tests cover a pet with zero tasks (making sure nothing crashes on an empty schedule), two tasks scheduled at the exact same time for the same pet (conflict detection), and sorting tasks chronologically where some tasks have no start time. These tests matter because they cover the core things a user actually depends on — if the scheduler sorts wrong, the daily view is confusing; if recurrence breaks, the owner has to manually re-enter tasks every day; and if conflicts aren't caught, a pet could get double-booked for a vet visit and a grooming at the same time.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

=> I'd say 4 out of 5 stars. The main scheduling features all work and are tested — priority sorting, time sorting, daily recurrence, and same-pet conflict detection all pass. But I know there are gaps. If I had more time I'd add tests for weekly recurrence to make sure the 7-day shift works right, cross-pet conflicts where the owner is double-booked across different animals, and the filter_tasks method to make sure filtering by pet name and completion status actually narrows results correctly. I'd also want to test what happens when you complete a recurring task multiple times in a row to make sure the ID chain doesn't break.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

=> Honestly the conflict detection turned out better than I expected. Initially I thought it would just be a simple "do these two tasks start at the same time" check, but the final version compares actual time windows and classifies conflicts as same-pet or cross-pet, which makes the warnings way more useful. Seeing those warnings show up in the Streamlit UI with actual tips like "your pet can't do two things at once" made it feel like a real app instead of just a class project. The recurring task logic is also something I'm proud of — the way mark_done creates and returns a new task that gets automatically added to the schedule is clean and the user never has to think about it.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

=> The biggest thing I'd redesign is how time windows work. Right now the scheduler treats the entire window as blocked time, which means it over-flags conflicts. A 30-minute walk with an 8:00-10:00 window shouldn't conflict with a 9:30 feeding, because the walk could easily finish by 8:30. I'd want to add actual placement logic that picks the best start time within each window to minimize overlaps. I'd also add the ability to edit or delete tasks from the UI instead of just adding them — right now if you make a typo you're stuck with it unless you restart the app. And the weekly recurrence view would be nice since right now everything is focused on a single day.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

=> The biggest thing I learned is that starting with a UML diagram and then comparing it to what you actually built is really valuable. My initial design had methods like score_priority and estimate_end_time that I never ended up needing, and it was missing things like pet_name on Task and sort_by_time on Schedule that turned out to be essential. The gap between the plan and the reality taught me that design is iterative — you can't know everything upfront, but having that starting blueprint still keeps you organized. Working with AI reinforced that too. It's great at generating code and suggesting structure, but you still have to be the one who decides what actually makes sense for your specific situation.
