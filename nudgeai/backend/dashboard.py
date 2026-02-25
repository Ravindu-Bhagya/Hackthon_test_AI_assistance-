import json
import streamlit as st
from task_extractor import extract_task

st.set_page_config(page_title="NudgeAI Dashboard", layout="wide")
st.title("🚀 NudgeAI - Task Dashboard")

# Load demo emails
with open("data/demo_emails.json") as f:
    emails = json.load(f)

st.subheader("Incoming Emails / Tasks")

tasks = []

for email in emails:
    # Extract task from email
    task_info = extract_task(email["body"])
    
    # Combine with email subject
    task_info["email_subject"] = email["subject"]
    
    tasks.append(task_info)

# Display tasks in a table
if tasks:
    for i, task in enumerate(tasks):
        st.markdown(f"### Email {i+1}: {task['email_subject']}")
        st.write(task)

        # Confirmation buttons for high-confidence tasks
        if task["task"] and task["confidence"] in ["high", "medium"]:
            col1, col2 = st.columns(2)
            if col1.button(f"Confirm Task {i+1}"):
                st.success(f"✅ Task Confirmed: {task['task']}")
            if col2.button(f"Dismiss Task {i+1}"):
                st.warning(f"❌ Task Dismissed: {task['task']}")
        else:
            st.info("No actionable task detected or low confidence")
