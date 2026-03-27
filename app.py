import streamlit as st
from datetime import date, datetime, time, timedelta
from pawpal_system import Pet, Task, Owner, Schedule

# -- Session state bootstrap --------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", daily_available_minutes=180)
if "pets" not in st.session_state:
    st.session_state.pets = []          # multi-pet list
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "schedules" not in st.session_state:
    st.session_state.schedules = []

owner = st.session_state.owner

# -- Helper: expand recurring tasks ------------------------------------------

def expand_recurring(template: Task, days: int = 7):
    if template.recurrence != "daily":
        return [template]
    return [
        Task(
            id=f"{template.id}-day{i}",
            name=template.name,
            duration_minutes=template.duration_minutes,
            priority=template.priority,
            task_type=template.task_type,
            pet_name=template.pet_name,
            earliest_start=template.earliest_start + timedelta(days=i) if template.earliest_start else None,
            latest_end=template.latest_end + timedelta(days=i)         if template.latest_end   else None,
            recurrence=template.recurrence,
        )
        for i in range(days)
    ]

# =============================================================================
# SECTION 1 — Pet Profile
# =============================================================================

st.title("PawPal Scheduler")
st.subheader("1. Pet Profile")

col1, col2, col3, col4 = st.columns(4)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    breed = st.text_input("Breed")
with col4:
    age = st.number_input("Age", min_value=0, max_value=30, value=2)

if st.button("Add Pet"):
    names = [p.name for p in st.session_state.pets]
    if pet_name in names:
        st.warning(f"{pet_name} is already added.")
    else:
        new_pet = Pet(name=pet_name, species=species, breed=breed or None, age=int(age))
        st.session_state.pets.append(new_pet)
        owner.pet = new_pet          # keep owner.pet pointing to the latest pet
        st.success(f"Added pet: {new_pet.name}")

if st.session_state.pets:
    st.write("**Your pets:**", "  |  ".join(p.name for p in st.session_state.pets))

# =============================================================================
# SECTION 2 — Add Tasks
# =============================================================================

st.subheader("2. Add Tasks")

pet_options = [p.name for p in st.session_state.pets] or ["(add a pet first)"]

c1, c2, c3 = st.columns(3)
with c1:
    task_title = st.text_input("Task title", value="Morning walk")
    assigned_pet = st.selectbox("Assign to pet", pet_options)
with c2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with c3:
    task_type = st.selectbox("Type", ["exercise", "feeding", "medication", "grooming", "enrichment", "health", "general"])
    recurrence = st.selectbox("Recurrence", ["none", "daily"])

ct1, ct2 = st.columns(2)
with ct1:
    start_time = st.time_input("Earliest start", value=time(8, 0))
with ct2:
    end_time = st.time_input("Latest end", value=time(10, 0))

if st.button("Add Task"):
    if assigned_pet == "(add a pet first)":
        st.error("Add a pet before adding tasks.")
    else:
        prio_map = {"low": 1, "medium": 2, "high": 3}
        task = Task(
            id=f"task-{len(st.session_state.tasks) + 1}",
            name=task_title,
            duration_minutes=int(duration),
            priority=prio_map[priority],
            task_type=task_type,
            pet_name=assigned_pet,
            earliest_start=datetime.combine(date.today(), start_time),
            latest_end=datetime.combine(date.today(), end_time),
            recurrence=recurrence if recurrence != "none" else None,
        )
        st.session_state.tasks.append(task)
        st.success(f"Added task: {task.name} for {assigned_pet}"
                   + (" (repeats daily)" if task.recurrence else ""))

if st.session_state.tasks:
    st.write("**Tasks added so far:**")
    st.table([
        {
            "Pet":       t.pet_name or "-",
            "Task":      t.name,
            "Start":     t.earliest_start.strftime("%H:%M") if t.earliest_start else "-",
            "End":       t.latest_end.strftime("%H:%M")     if t.latest_end     else "-",
            "Duration":  f"{t.duration_minutes}min",
            "Priority":  t.priority,
            "Recurring": t.recurrence or "-",
        }
        for t in st.session_state.tasks
    ])

# =============================================================================
# SECTION 3 — Build Schedule
# =============================================================================

st.subheader("3. Build Schedule")

if st.button("Generate Schedule"):
    today = date.today()
    schedule = Schedule(today)

    # Expand recurring tasks before adding to schedule
    for t in st.session_state.tasks:
        for instance in expand_recurring(t, days=1):   # today's instance only
            schedule.add_task(instance)

    st.session_state.schedules.append(schedule)
    st.success(f"Schedule generated with {len(schedule.tasks)} tasks ({schedule.total_scheduled_minutes} min total).")

# =============================================================================
# SECTION 4 — View Schedule (sort + filter + conflicts)
# =============================================================================

if st.session_state.schedules:
    schedule = st.session_state.schedules[-1]   # show the most recent schedule

    st.subheader("4. Today's Schedule")

    # -- Filter controls ------------------------------------------------------
    fc1, fc2 = st.columns(2)
    with fc1:
        pet_filter = st.selectbox(
            "Filter by pet",
            ["All pets"] + [p.name for p in st.session_state.pets],
            key="pet_filter"
        )
    with fc2:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "Pending", "Completed"],
            key="status_filter"
        )

    # -- Apply filters using Schedule methods ---------------------------------
    pet_name_arg    = None if pet_filter    == "All pets" else pet_filter
    completed_arg   = None if status_filter == "All"      else (status_filter == "Completed")

    filtered = schedule.filter_tasks(pet_name=pet_name_arg, completed=completed_arg)

    # -- Sort filtered results by time using the Schedule lambda key ----------
    sorted_tasks = sorted(filtered, key=lambda t: t.earliest_start or datetime.max)

    if sorted_tasks:
        st.table([
            {
                "Status":   "Done" if t.completed else "Pending",
                "Start":    t.earliest_start.strftime("%H:%M") if t.earliest_start else "-",
                "End":      t.latest_end.strftime("%H:%M")     if t.latest_end     else "-",
                "Pet":      t.pet_name or "-",
                "Task":     t.name,
                "Duration": f"{t.duration_minutes}min",
                "Priority": t.priority,
                "Type":     t.task_type,
            }
            for t in sorted_tasks
        ])
    else:
        st.info("No tasks match the selected filters.")

    # -- Mark tasks complete (auto-recurrence) --------------------------------
    st.subheader("5. Mark Task Complete")
    pending_tasks = schedule.filter_tasks(completed=False)
    if pending_tasks:
        task_options = {f"{t.name} ({t.earliest_start.strftime('%H:%M') if t.earliest_start else '?'}) [{t.pet_name}]": t.id for t in pending_tasks}
        selected_label = st.selectbox("Select a task to complete", list(task_options.keys()), key="complete_task")
        if st.button("Mark Complete"):
            task_id = task_options[selected_label]
            next_task = schedule.mark_task_complete(task_id)
            if next_task:
                st.success(
                    f"Done! Next occurrence auto-created for "
                    f"{next_task.earliest_start.strftime('%Y-%m-%d %H:%M') if next_task.earliest_start else 'TBD'} "
                    f"(recurrence: {next_task.recurrence})."
                )
            else:
                st.success("Task marked complete.")
            st.rerun()
    else:
        st.info("All tasks are complete!")

    # -- Conflict detection ---------------------------------------------------
    st.subheader("6. Conflict Detection")
    warnings = schedule.find_conflicts()
    if warnings:
        for w in warnings:
            st.warning(w)
        st.write(f"**{len(warnings)} conflict(s) detected.**")
    else:
        st.success("No scheduling conflicts found.")

    # -- Schedule reasoning log -----------------------------------------------
    with st.expander("Schedule log"):
        st.write(schedule.explain_decision())
