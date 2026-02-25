# backend/main.py

import json
import os
from task_extractor import extract_task
from datetime import datetime

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # Go up one level to nudgeai/

# Load demo emails
emails_path = os.path.join(project_root, "data", "demo_emails.json")
with open(emails_path) as f:
    emails = json.load(f)

print("⚠️ Using demo emails for task extraction.\n")

# Collect all extracted tasks
all_tasks = []

# Process each demo email
for email in emails:
    print(f"📧 EMAIL: {email['subject']}")
    result = extract_task(email["body"], source="email", subject_or_channel=email["subject"])
    if result["task"]:  # Only add if a task was extracted
        task_obj = {
            "task": result["task"],
            "owner": result.get("assignee", "Unknown"),
            "deadline": result.get("deadline", "No deadline"),
            "priority": "high" if result.get("confidence") == "high" else "medium" if result.get("confidence") == "medium" else "low",
            "suggestion": f"Action item from {result['source']}: {result.get('subject_or_channel', '')}",
            "status": "pending",
            "source": result["source"],
            "confidence": result.get("confidence", "low"),
            "source_email": {
                "from": email.get("from", "unknown@example.com"),
                "subject": email.get("subject", ""),
                "body": email.get("body", "")
            },
            "reminder": None,
            "reminder_triggered": False
        }
        all_tasks.append(task_obj)
        print(f"✅ Extracted: {result['task']} (Confidence: {result.get('confidence', 'low')})")
    else:
        print("⏭️ No actionable task detected.")

# Save all tasks to tasks.json
tasks_path = os.path.join(project_root, "data", "tasks.json")
with open(tasks_path, "w") as f:
    json.dump(all_tasks, f, indent=4)

print(f"\n📊 Total tasks extracted and saved: {len(all_tasks)}")