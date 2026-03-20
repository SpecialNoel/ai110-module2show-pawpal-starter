import streamlit as st
import pandas as pd
from pawpal_system import Owner, Pet, Task, Priority, Frequency
from datetime import date

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF6B6B;
    }
    .success-card {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# Header
col_title, col_info = st.columns([3, 1])
with col_title:
    st.title("🐾 PawPal+")
    st.markdown("**Your intelligent pet care planning assistant**")
with col_info:
    st.markdown("### v1.0")

st.markdown("---")

# Initialize session state
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Demo Owner")
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "pets" not in st.session_state:
    st.session_state.pets = []
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# ============= SIDEBAR =============
with st.sidebar:
    st.header("📋 Pet & Task Management")
    
    sidebar_tabs = st.tabs(["🐕 Pets", "✓ Tasks", "📊 Summary"])
    
    # TAB 1: Pets
    with sidebar_tabs[0]:
        st.subheader("Add New Pet")
        with st.form("pet_form", clear_on_submit=True):
            pet_name = st.text_input("Pet name *", placeholder="e.g., Bella, Max")
            pet_species = st.selectbox("Species *", ["dog", "cat", "rabbit", "bird", "other"])
            col_age, col_breed = st.columns(2)
            with col_age:
                pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
            with col_breed:
                pet_breed = st.text_input("Breed", placeholder="Optional")
            
            if st.form_submit_button("➕ Create Pet", use_container_width=True):
                if pet_name:
                    pet_id = f"pet_{len(st.session_state.pets) + 1}"
                    new_pet = Pet(
                        name=pet_name,
                        id=pet_id,
                        species=pet_species,
                        age=pet_age,
                        breed=pet_breed if pet_breed else ""
                    )
                    st.session_state.pets.append(new_pet)
                    st.session_state.owner.add_pet(new_pet)
                    st.success(f"✅ {pet_name} added successfully!")
                else:
                    st.error("❌ Pet name is required")
        
        # Display pets
        if st.session_state.pets:
            st.divider()
            st.subheader("Your Pets")
            for pet in st.session_state.pets:
                with st.container(border=True):
                    col_name, col_delete = st.columns([3, 1])
                    with col_name:
                        st.write(f"**{pet.name}**")
                        st.caption(f"{pet.species.title()} • {pet.age} years old")
                        if pet.breed:
                            st.caption(f"Breed: {pet.breed}")
                    with col_delete:
                        if st.button("🗑️", key=f"delete_pet_{pet.id}", help="Remove pet"):
                            st.session_state.pets.remove(pet)
                            st.session_state.owner.remove_pet(pet)
                            st.rerun()
        else:
            st.info("👆 Add a pet to get started!")
    
    # TAB 2: Tasks
    with sidebar_tabs[1]:
        st.subheader("Add New Task")
        if not st.session_state.pets:
            st.warning("⚠️ Create a pet first before adding tasks")
        else:
            with st.form("task_form", clear_on_submit=True):
                task_desc = st.text_input("Task description *", placeholder="e.g., Morning walk")
                col_dur, col_pri = st.columns(2)
                with col_dur:
                    task_duration = st.number_input("Duration (min) *", min_value=1, max_value=480, value=15)
                with col_pri:
                    task_priority = st.selectbox("Priority *", ["low", "normal", "high"], index=1)
                
                task_frequency = st.selectbox("Frequency *", ["once", "daily", "weekly", "monthly"])
                selected_pets = st.multiselect(
                    "Pets *",
                    [p.name for p in st.session_state.pets],
                    help="Select at least one pet"
                )
                task_due_date = st.date_input("Due date", value=None)
                
                if st.form_submit_button("➕ Create Task", use_container_width=True):
                    if task_desc and selected_pets:
                        priority_map = {"low": Priority.LOW, "normal": Priority.NORMAL, "high": Priority.HIGH}
                        frequency_map = {"once": Frequency.ONCE, "daily": Frequency.DAILY, "weekly": Frequency.WEEKLY, "monthly": Frequency.MONTHLY}
                        
                        new_task = Task(
                            name=task_desc,
                            description=task_desc,
                            duration=int(task_duration),
                            priority=priority_map[task_priority],
                            frequency=frequency_map[task_frequency],
                            due_date=task_due_date
                        )
                        
                        for pet_name in selected_pets:
                            pet = next((p for p in st.session_state.pets if p.name == pet_name), None)
                            if pet:
                                st.session_state.owner.add_task_to_pet(pet, new_task)
                        
                        st.session_state.tasks.append(new_task)
                        st.success(f"✅ Task '{task_desc}' created!")
                    else:
                        st.error("❌ Task description and pets are required")
        
        # Display tasks
        if st.session_state.tasks:
            st.divider()
            st.subheader(f"Tasks ({len(st.session_state.tasks)})")
            for i, task in enumerate(st.session_state.tasks):
                status_icon = "✅" if task.completed else "⏳"
                with st.container(border=True):
                    col_info, col_action = st.columns([4, 1])
                    with col_info:
                        st.write(f"{status_icon} **{task.description}**")
                        pets_str = ", ".join([p.name for p in task.pets]) if task.pets else "—"
                        col_d, col_p, col_f = st.columns(3)
                        with col_d:
                            st.caption(f"⏱️ {task.duration}m")
                        with col_p:
                            st.caption(f"🎯 {task.priority.value}")
                        with col_f:
                            st.caption(f"🔄 {task.frequency.value}")
                    with col_action:
                        if st.button("🗑️", key=f"delete_task_{i}", help="Remove task"):
                            for pet in task.pets:
                                pet.remove_task(st.session_state.tasks[i])
                            st.session_state.tasks.pop(i)
                            st.rerun()
    
    # TAB 3: Summary
    with sidebar_tabs[2]:
        st.subheader("Setup Summary")
        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.metric("🐾 Pets", len(st.session_state.pets), delta=None)
        with metric_cols[1]:
            st.metric("✓ Tasks", len(st.session_state.tasks), delta=None)
        with metric_cols[2]:
            if st.session_state.scheduler:
                conflicts = st.session_state.scheduler.find_time_conflicts()
                total_conflicts = len(conflicts['same_pet']) + len(conflicts['different_pets'])
                if total_conflicts > 0:
                    st.metric("⚠️ Conflicts", total_conflicts, delta=None, delta_color="inverse")
                else:
                    st.metric("✅ Conflicts", 0, delta=None)
            else:
                st.metric("⚠️ Conflicts", "—", delta=None)

st.markdown("---")

# ============= MAIN CONTENT =============
# Generate Schedule Section
st.subheader("📅 Schedule Generator")
gen_col1, gen_col2 = st.columns([3, 1])
with gen_col1:
    st.markdown("Click the button below to generate an optimized schedule based on your pets and tasks.")
with gen_col2:
    if st.button("🔄 Generate Schedule", use_container_width=True, type="primary", key="gen_main"):
        if st.session_state.pets and st.session_state.tasks:
            st.session_state.scheduler = st.session_state.owner.generate_scheduler("Optimized Schedule")
            st.toast("✅ Schedule generated!", icon="🎉")
            st.rerun()
        else:
            st.error("❌ Need at least one pet and one task to generate a schedule")

st.divider()

# Display schedule if generated
if st.session_state.scheduler:
    scheduler = st.session_state.scheduler
    schedule = scheduler.get_schedule()
    
# Display schedule if generated
if st.session_state.scheduler:
    scheduler = st.session_state.scheduler
    schedule = scheduler.get_schedule()
    
    # PROMINENT CONFLICT WARNING - Display at top
    if scheduler.has_conflicts():
        # Large, eye-catching warning banner
        st.markdown("""
        <div style="
            background-color: #fff3cd;
            border: 3px solid #ff6b6b;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(255, 0, 0, 0.1);
        ">
            <h2 style="color: #d32f2f; margin: 0 0 10px 0;">⚠️ SCHEDULE CONFLICTS DETECTED</h2>
            <p style="color: #d32f2f; font-weight: bold; margin: 0; font-size: 1.1rem;">
        """ + scheduler.warning.replace("Same-pet conflicts:", "<br>🔴 <strong>Same-pet conflicts:</strong>").replace("Different-pets conflicts:", "<br>🟠 <strong>Different-pets conflicts:</strong>") + """
            </p>
            <p style="color: #666; margin: 10px 0 0 0; font-size: 0.95rem;">
                💡 Tip: Review the conflict analysis section below to resolve scheduling issues.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Also add an expander with quick fix suggestions
        with st.expander("💡 How to resolve conflicts", expanded=False):
            st.markdown("""
            **Common solutions:**
            - ✏️ Adjust task due dates to spread them across different days
            - ⏰ Change task times or durations to avoid overlaps
            - 👥 Assign some tasks to different pets if possible
            - 📋 Mark completed tasks to reduce the active workload
            """)
    else:
        # Success message with green styling
        st.markdown("""
        <div style="
            background-color: #d4edda;
            border: 3px solid #28a745;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(40, 167, 69, 0.1);
        ">
            <h2 style="color: #155724; margin: 0;">✅ SCHEDULE OPTIMIZED - NO CONFLICTS!</h2>
            <p style="color: #155724; margin: 5px 0 0 0;">Your schedule is perfectly planned with no task conflicts detected.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Main schedule display
    col_main, col_sidebar = st.columns([2.5, 1])
    
    with col_main:
        if schedule:
            st.subheader(f"📋 Optimized Task Schedule ({len(schedule)} tasks)")
            st.caption("⬇️ Sorted by priority (HIGH → NORMAL → LOW) then by duration (shortest first)")
            
            # Build display table
            display_data = []
            for i, task in enumerate(schedule, 1):
                pet_names = ", ".join([p.name for p in task.pets]) if task.pets else "—"
                due = task.due_date.strftime("%a, %m/%d") if task.due_date else "No date"
                status = "✅ Completed" if task.completed else "⏳ Pending"
                recurring = "🔄 Yes" if task.is_recurring() else "—"
                
                display_data.append({
                    "#": i,
                    "Task": task.description,
                    "Pet(s)": pet_names,
                    "⏱️": f"{task.duration}m",
                    "Priority": task.priority.value.title(),
                    "📅": due,
                    "Recurs": recurring,
                    "Status": status
                })
            
            # Display as professional table
            df = pd.DataFrame(display_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "#": st.column_config.NumberColumn("#", width="small"),
                    "Task": st.column_config.Column("Task", width="medium"),
                    "Pet(s)": st.column_config.Column("Pet(s)", width="medium"),
                    "⏱️": st.column_config.Column("Duration", width="small"),
                    "Priority": st.column_config.Column("Priority", width="small"),
                    "📅": st.column_config.Column("Due Date", width="medium"),
                    "Recurs": st.column_config.Column("Recurs", width="small"),
                    "Status": st.column_config.Column("Status", width="medium"),
                }
            )
            
            # Export button
            st.download_button(
                "📥 Download as CSV",
                df.to_csv(index=False),
                "pawpal_schedule.csv",
                "text/csv",
                use_container_width=True
            )
        else:
            st.info("📌 No tasks were assigned to pets in the current setup.")
    
    with col_sidebar:
        st.subheader("🔍 Quick View")
        
        # Use tabs for filtering
        filter_tabs = st.tabs(["All", "By Pet", "By Status", "Details"])
        
        with filter_tabs[0]:
            st.metric("Total Tasks", len(schedule))
            st.metric("Total Time", f"{sum(t.duration for t in schedule)} min")
            st.metric("Done", len([t for t in schedule if t.completed]))
        
        with filter_tabs[1]:
            if st.session_state.pets:
                pet_choice = st.selectbox("Select pet:", [p.name for p in st.session_state.pets], key="fp1")
                pet_tasks = scheduler.filter_by_pet_name(pet_choice)
                st.metric(f"{pet_choice}'s Tasks", len(pet_tasks))
                if pet_tasks:
                    st.write("**Tasks:**")
                    for task in pet_tasks:
                        st.checkbox(
                            task.description,
                            value=task.completed,
                            disabled=True,
                            key=f"cb_{id(task)}"
                        )
            else:
                st.info("No pets available")
        
        with filter_tabs[2]:
            status_choice = st.radio("View:", ["Pending", "Completed"], horizontal=True, key="fc2")
            is_completed = status_choice == "Completed"
            status_tasks = scheduler.filter_by_completion(is_completed)
            st.metric(f"{status_choice} Tasks", len(status_tasks))
            if status_tasks:
                st.write("**Tasks:**")
                for task in status_tasks:
                    st.write(f"• {task.description}")
        
        with filter_tabs[3]:
            metric_cols = st.columns(2)
            with metric_cols[0]:
                st.metric("Recurring", sum(1 for t in schedule if t.is_recurring()))
            with metric_cols[1]:
                unique_dates = len(set(t.due_date for t in schedule if t.due_date))
                st.metric("Unique Dates", unique_dates)
    
    st.divider()
    
    # Conflict Analysis Section - PROMINENT
    if scheduler.has_conflicts():
        st.subheader("🔴 DETAILED CONFLICT ANALYSIS")
        st.markdown("---")
        conflicts = scheduler.find_time_conflicts()
        
        col1, col2 = st.columns(2)
        
        # Same-pet conflicts
        with col1:
            if conflicts['same_pet']:
                st.markdown("""
                <div style="background-color: #ffe0e0; padding: 12px; border-radius: 6px; border-left: 4px solid #d32f2f;">
                    <h3 style="color: #d32f2f; margin: 0;">🔴 Same-Pet Conflicts</h3>
                    <p style="color: #666; margin: 5px 0 0 0; font-size: 0.9rem;">
                        Tasks assigned to the same pet on the same date
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                for idx, (task_a, task_b) in enumerate(conflicts['same_pet'], 1):
                    with st.container(border=True):
                        st.write(f"**Conflict #{idx}**")
                        col_task1, col_task2 = st.columns(2)
                        with col_task1:
                            st.write(f"📌 **Task 1:** {task_a.description}")
                            st.caption(f"⏱️ {task_a.duration}m | 🎯 {task_a.priority.value}")
                        with col_task2:
                            st.write(f"📌 **Task 2:** {task_b.description}")
                            st.caption(f"⏱️ {task_b.duration}m | 🎯 {task_b.priority.value}")
                        
                        pets_str = ", ".join([p.name for p in task_a.pets])
                        st.info(f"🐾 **Shared pet(s):** {pets_str}")
                        st.caption(f"📅 **Date:** {task_a.due_date}")
                        
                        # Suggest action
                        st.markdown("""
                        <div style="background-color: #fff8e1; padding: 8px; border-radius: 4px; margin-top: 8px;">
                            <small>💡 <strong>Fix:</strong> Schedule one task on a different day or change the time</small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.success("✅ **No same-pet conflicts detected!**")
        
        # Different-pet conflicts
        with col2:
            if conflicts['different_pets']:
                st.markdown("""
                <div style="background-color: #fff4e0; padding: 12px; border-radius: 6px; border-left: 4px solid #ff9800;">
                    <h3 style="color: #ff9800; margin: 0;">🟠 Different-Pet Conflicts</h3>
                    <p style="color: #666; margin: 5px 0 0 0; font-size: 0.9rem;">
                        Different pets with tasks at the same time
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                for idx, (task_a, task_b) in enumerate(conflicts['different_pets'], 1):
                    with st.container(border=True):
                        st.write(f"**Conflict #{idx}**")
                        col_task1, col_task2 = st.columns(2)
                        with col_task1:
                            pet_a = task_a.pets[0].name if task_a.pets else "Unknown"
                            st.write(f"📌 **Task 1:** {task_a.description}")
                            st.caption(f"🐾 {pet_a} | ⏱️ {task_a.duration}m")
                        with col_task2:
                            pet_b = task_b.pets[0].name if task_b.pets else "Unknown"
                            st.write(f"📌 **Task 2:** {task_b.description}")
                            st.caption(f"🐾 {pet_b} | ⏱️ {task_b.duration}m")
                        
                        st.caption(f"📅 **Scheduled for:** {task_a.due_date}")
                        
                        # Suggest action
                        st.markdown("""
                        <div style="background-color: #fff8e1; padding: 8px; border-radius: 4px; margin-top: 8px;">
                            <small>💡 <strong>Fix:</strong> Adjust schedules or reduce task overlap</small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.success("✅ **No different-pet conflicts detected!**")
    else:
        st.subheader("✅ CONFLICT ANALYSIS")
        st.markdown("""
        <div style="background-color: #d4edda; padding: 15px; border-radius: 6px; border-left: 4px solid #28a745;">
            <h3 style="color: #155724; margin: 0;">Perfect Schedule!</h3>
            <p style="color: #155724; margin: 8px 0 0 0;">
                No conflicts detected. Your schedule is fully optimized and ready to execute.
            </p>
        </div>
        """, unsafe_allow_html=True)

else:
    st.info(
        "👈 **Get started:** Add pets and tasks in the sidebar, then generate a schedule to see optimization, sorting, and conflict detection in action."
    )

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #888; font-size: 0.9rem;">
    🐾 <strong>PawPal+</strong> • Intelligent Pet Care Planning<br>
    Built with ❤️ for pet owners who care
    </div>
    """,
    unsafe_allow_html=True
)
