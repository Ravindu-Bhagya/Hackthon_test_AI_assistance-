# dashboard.py - NudgeAI Personal Assistant Dashboard

import json
import streamlit as st
from datetime import datetime, timedelta
import sys
import os

# Add backend to path for imports BEFORE any backend imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai_agent import get_ai_response, process_task_action

st.set_page_config(page_title="NudgeAI Dashboard", layout="wide")
st.title("🚀 NudgeAI - Personal Assistant Dashboard")

# Get base directory
base_dir = os.path.join(os.path.dirname(__file__), '..')

# Load extracted tasks from JSON file
tasks_file = os.path.join(base_dir, 'data', 'tasks.json')
if os.path.exists(tasks_file):
    with open(tasks_file) as f:
        all_tasks = json.load(f)
else:
    all_tasks = []

# Initialize session state for modals
if "show_email_modal" not in st.session_state:
    st.session_state.show_email_modal = None
if "show_chat_modal" not in st.session_state:
    st.session_state.show_chat_modal = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}  # {task_idx: [messages...]}
if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

# MODAL: View Source Email - Display at top if active
if st.session_state.show_email_modal is not None:
    task_idx = st.session_state.show_email_modal
    if task_idx < len(all_tasks):
        task = all_tasks[task_idx]
        email_data = task.get("source_email", {})
        
        with st.container(border=True):
            st.subheader(f"📧 Source Email: {task['task']}")
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**From:** {email_data.get('from', 'unknown@example.com')}")
                st.write(f"**Subject:** {email_data.get('subject', '(No subject)')}")
            with col2:
                if st.button("❌ Close Email", key="close_email_modal"):
                    st.session_state.show_email_modal = None
                    st.rerun()
            
            st.markdown("---")
            st.write("**Email Body:**")
            st.write(email_data.get('body', 'No body content'))
            
            st.markdown("---")
            st.subheader("📧 Reply to this email:")
            reply_text = st.text_area(
                "Your reply:",
                placeholder="Type your response here...",
                key=f"reply_text_modal_{task_idx}",
                label_visibility="collapsed",
                height=120
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 Send Reply", key=f"send_reply_modal_{task_idx}"):
                    if reply_text:
                        st.success(f"✅ Reply sent to {email_data.get('from', 'sender')}!")
                        st.info(f"Your reply: {reply_text}")
                        st.session_state.show_email_modal = None
                        st.rerun()
                    else:
                        st.warning("Please write a reply before sending!")
            with col2:
                if st.button("Cancel", key=f"cancel_reply_{task_idx}"):
                    st.session_state.show_email_modal = None
                    st.rerun()
        st.divider()

# MODAL: Chatbot Task Completion - Display at top if active
if st.session_state.show_chat_modal is not None:
    task_idx = st.session_state.show_chat_modal
    if task_idx < len(all_tasks):
        task = all_tasks[task_idx]
        
        with st.container(border=True):
            st.subheader(f"💬 AI Agent Assistant: {task['task']}")
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**Task:** {task['task']}")
                st.write(f"**Owner:** {task.get('owner', 'Unassigned')}")
            with col2:
                if st.button("❌ Close Chat", key="close_chat_modal"):
                    st.session_state.show_chat_modal = None
                    # Clear chat history when closing
                    if task_idx in st.session_state.chat_history:
                        del st.session_state.chat_history[task_idx]
                    st.rerun()
            
            st.markdown("---")
            
            # Initialize chat history for this task
            if task_idx not in st.session_state.chat_history:
                st.session_state.chat_history[task_idx] = [
                    {
                        "role": "assistant",
                        "content": f"👋 Hi! I'm your AI assistant. I'm here to help you complete '{task['task']}'. What would you like to do? You can ask for help, tell me about your progress, or ask me to help you complete this task."
                    }
                ]
            
            # Display conversation history
            chat_container = st.container()
            with chat_container:
                for message in st.session_state.chat_history[task_idx]:
                    if message["role"] == "user":
                        st.write(f"👤 **You:** {message['content']}")
                    else:
                        st.write(f"🤖 **AI Agent:** {message['content']}")
            
            st.markdown("---")
            
            # Chat input
            # If a clear flag exists from the previous run, clear the widget value BEFORE instantiation
            clear_key = f"clear_chat_{task_idx}"
            widget_key = f"chat_input_modal_{task_idx}"
            if st.session_state.get(clear_key):
                # set the widget value to empty and remove the clear flag
                st.session_state[widget_key] = ""
                del st.session_state[clear_key]

            col1, col2 = st.columns([4, 1])
            with col1:
                user_input = st.text_input(
                    "Your message:",
                    placeholder="Ask for help, describe what you've done, or tell me to complete this task...",
                    key=widget_key,
                    label_visibility="collapsed"
                )
            with col2:
                send_button = st.button("📤 Send", key=f"send_chat_modal_{task_idx}")
            
            if send_button and user_input:
                # Add user message to history
                st.session_state.chat_history[task_idx].append({
                    "role": "user",
                    "content": user_input
                })
                
                # Get AI response
                ai_response = get_ai_response(task['task'], user_input, task.get('owner', 'You'))
                
                # Add AI response to history
                st.session_state.chat_history[task_idx].append({
                    "role": "assistant",
                    "content": ai_response["response"]
                })
                
                # Handle completion action
                if ai_response["action"] == "complete":
                    all_tasks[task_idx]["status"] = "completed"
                    all_tasks[task_idx]["chat_completion"] = user_input
                    all_tasks[task_idx]["completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_tasks()
                    st.success("✅ Task marked as completed!")
                    st.balloons()
                    st.session_state.show_chat_modal = None
                    if task_idx in st.session_state.chat_history:
                        del st.session_state.chat_history[task_idx]
                    # set a clear flag so the widget is cleared on the next run (pre-widget assignment)
                    st.session_state[f"clear_chat_{task_idx}"] = True
                    st.rerun()

                # set flag to clear input after sending
                st.session_state[f"clear_chat_{task_idx}"] = True
                st.rerun()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Mark as Complete", key=f"mark_complete_chat_{task_idx}"):
                    all_tasks[task_idx]["status"] = "completed"
                    all_tasks[task_idx]["completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_tasks()
                    st.success("✅ Task completed!")
                    st.balloons()
                    st.session_state.show_chat_modal = None
                    if task_idx in st.session_state.chat_history:
                        del st.session_state.chat_history[task_idx]
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancel", key=f"cancel_chat_final_{task_idx}"):
                    st.session_state.show_chat_modal = None
                    if task_idx in st.session_state.chat_history:
                        del st.session_state.chat_history[task_idx]
                    st.rerun()
        st.divider()

def save_tasks():
    """Save updated tasks back to JSON file"""
    with open(tasks_file, "w") as f:
        json.dump(all_tasks, f, indent=4)

def mark_task_complete(task_index):
    """Mark a task as complete"""
    all_tasks[task_index]["status"] = "completed"
    all_tasks[task_index]["completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_tasks()

def set_reminder(task_index, reminder_option):
    """Set a reminder for a task"""
    reminder_map = {
        "1 hour before": 1,
        "1 day before": 24,
        "2 days before": 48,
        "1 week before": 168,
        "On due date": 0,
    }
    all_tasks[task_index]["reminder"] = reminder_option
    all_tasks[task_index]["reminder_hours"] = reminder_map.get(reminder_option, 0)
    save_tasks()

# Display tasks by status
st.subheader("📋 Pending Tasks")

# Filter pending tasks
pending_tasks = [(i, t) for i, t in enumerate(all_tasks) if t.get("status") == "pending"]

# Sort by priority: high > medium > low
priority_order = {"high": 0, "medium": 1, "low": 2}
pending_tasks.sort(key=lambda x: priority_order.get(x[1].get("priority", "low"), 3))

if pending_tasks:
    for original_idx, task in pending_tasks:
        priority = task.get("priority", "medium").lower()
        
        # Color coding by priority
        if priority == "high":
            st.error(f"🔴 **[HIGH PRIORITY]** {task['task']}")
        elif priority == "medium":
            st.warning(f"🟡 **[MEDIUM]** {task['task']}")
        else:
            st.info(f"🔵 **[LOW]** {task['task']}")
        
        # Display task details
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"👤 Owner: {task.get('owner', 'Unassigned')}")
        with col2:
            st.caption(f"📅 Due: {task.get('deadline', 'No deadline')}")
        with col3:
            st.caption(f"📧 Source: {task.get('source', 'unknown')}")
        
        st.caption(f"💡 {task.get('suggestion', '')}")
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # View Source Email button
            if st.button("📧 View Email", key=f"view_email_{original_idx}"):
                st.session_state.show_email_modal = original_idx
                st.rerun()
        
        with col2:
            # Mark as Done button
            if st.button("✅ Mark Done", key=f"mark_done_{original_idx}"):
                mark_task_complete(original_idx)
                st.success("✅ Task marked as done!")
                st.rerun()
        
        with col3:
            # Reminder dropdown
            reminder_option = st.selectbox(
                "⏰ Set Reminder",
                ["1 hour before", "1 day before", "2 days before", "1 week before", "On due date"],
                key=f"reminder_{original_idx}",
                label_visibility="collapsed"
            )
            if reminder_option and str(reminder_option) != st.session_state.get(f"last_reminder_{original_idx}"):
                st.session_state[f"last_reminder_{original_idx}"] = reminder_option
                set_reminder(original_idx, reminder_option)
                st.info(f"⏰ Reminder set: {reminder_option}")
                st.rerun()
        
        with col4:
            # Chatbot icon button
            if st.button("💬 Chat", key=f"chat_{original_idx}"):
                st.session_state.show_chat_modal = original_idx
                st.rerun()
        
        st.divider()
else:
    st.info("✅ No pending tasks!")

# Display completed tasks
st.subheader("✅ Completed Tasks")
completed_tasks = [t for t in all_tasks if t.get("status") == "completed"]

if completed_tasks:
    for task in completed_tasks:
        st.success(f"✅ {task['task']}")
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"Completed: {task.get('completed_date', 'N/A')}")
        with col2:
            if task.get("reminder"):
                st.caption(f"⏰ Reminder was: {task['reminder']}")
        st.divider()
else:
    st.info("No completed tasks yet.")

# Daily Summary
st.subheader("📊 Daily Summary")
total_tasks = len(all_tasks)
completed_count = len(completed_tasks)
pending_count = len(pending_tasks)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Tasks", total_tasks)
with col2:
    st.metric("Completed", completed_count)
with col3:
    st.metric("Pending", pending_count)

# Priority breakdown
high_priority = len([t for t in all_tasks if t.get("priority") == "high"])
medium_priority = len([t for t in all_tasks if t.get("priority") == "medium"])
low_priority = len([t for t in all_tasks if t.get("priority") == "low"])

st.write("**Priority Breakdown:**")
st.write(f"🔴 High Priority: {high_priority}")
st.write(f"🟡 Medium Priority: {medium_priority}")
st.write(f"🔵 Low Priority: {low_priority}")