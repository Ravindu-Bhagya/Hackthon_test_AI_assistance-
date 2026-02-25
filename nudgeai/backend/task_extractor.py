"""
Local mock task extractor for hackathon demo.
Returns deterministic AI-like outputs for demo emails without calling OpenAI.
"""

from datetime import datetime, timedelta

# In-memory storage for tasks
confirmed_tasks = []

def extract_task(content, source="email", subject_or_channel=""):
    """
    Mock AI engine to extract tasks from emails, calendar, or slack messages.
    Uses pattern matching to identify actionable tasks, assignees, deadlines, and confidence.
    """
    text = (content or "").lower()
    subject_text = (subject_or_channel or "").lower()
    combined_text = text + " " + subject_text
    
    task = None
    assignee = "You"
    deadline = None
    confidence = "low"

    # Email logic with extensive action item detection
    if source == "email":
        # High confidence patterns
        if "revised document" in combined_text or "send the revised document" in combined_text:
            task = "Send the revised document"
            assignee = "Ravindu"
            deadline = "Friday"
            confidence = "high"
        elif "follow up with the client" in combined_text or ("follow up" in combined_text and "client" in combined_text):
            task = "Follow up with the client"
            assignee = "Ravindu"
            deadline = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            confidence = "high"
        elif "urgent" in subject_text or "asap" in combined_text or "immediately" in combined_text:
            task = "Complete urgent task: " + subject_or_channel[:50]
            assignee = "You"
            deadline = "Today"
            confidence = "high"
        elif "password reset" in combined_text or ("password" in combined_text and "reset" in combined_text):
            task = "Update security credentials"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            confidence = "high"
        elif "phishing" in combined_text or "security" in combined_text:
            task = "Update security and change credentials"
            assignee = "You"
            deadline = "Today"
            confidence = "high"
        # Medium confidence patterns
        elif "revisions" in combined_text or ("update" in combined_text and "version" in combined_text):
            task = "Revise and update document/proposal"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "please review" in combined_text or ("review" in combined_text and not "resolved" in combined_text):
            task = "Review: " + subject_or_channel[:50]
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "please check" in combined_text or ("check" in combined_text and not "deployment" in combined_text):
            task = "Check and verify: " + subject_or_channel[:50]
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "quote" in combined_text or "proposal" in combined_text:
            task = "Prepare quote/proposal"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "confirm" in combined_text or ("approval" in combined_text and "go-live" in combined_text):
            task = "Confirm approval/signature"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            confidence = "high"
        elif "schedule" in combined_text or ("meeting" in combined_text and ("schedule" in combined_text or "propose" in combined_text)):
            task = "Schedule meeting/call"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "invoice" in combined_text or "payment" in combined_text or "billing" in combined_text:
            task = "Process invoice/payment/billing"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "feedback" in combined_text or ("report" in combined_text and not "outage" in combined_text) or "summary" in combined_text or "submit" in combined_text:
            task = "Submit feedback/report/summary"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "training" in combined_text or "compliance" in combined_text or "acknowledge" in combined_text or ("policy" in combined_text and "read" in combined_text):
            task = "Complete training/acknowledge policy"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "contract" in combined_text or ("review" in combined_text and "contract" in combined_text):
            task = "Review and finalize contract"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "data" in combined_text or ("export" in combined_text and "data" in combined_text):
            task = "Prepare and send data export"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "approve" in combined_text and ("post" in combined_text or "copy" in combined_text or "campaign" in combined_text):
            task = "Approve marketing content"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "incident" in combined_text or "outage" in combined_text:
            task = "Create incident/outage report"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "change request" in combined_text or "scope change" in combined_text:
            task = "Estimate impact and respond to change request"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "recruit" in combined_text or "research" in combined_text or "study" in combined_text:
            task = "Recruit users/prepare research"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "press" in combined_text:
            task = "Review and edit press release"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "finalize" in combined_text or "sow" in combined_text:
            task = "Finalize statement of work"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "renewal" in combined_text:
            task = "Review and approve contract renewal"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
            confidence = "medium"
        # Low confidence / No action
        elif "no action" in combined_text or "fyi" in combined_text or "digest" in combined_text or "resolved" in combined_text or "deployment" in combined_text:
            task = None
            confidence = "low"
        # Default for messages with directive words
        elif any(word in combined_text for word in ["can you", "could you", "please", "would you"]):
            task = "Review and respond: " + subject_or_channel[:50]
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            confidence = "low"

    # Calendar logic
    elif source == "calendar":
        if "prepare" in text:
            task = "Prepare meeting summary"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            confidence = "high"

    # Slack logic
    elif source == "slack":
        if "check" in text and "logs" in text:
            task = "Check server logs"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            confidence = "medium"
        elif "deployment" in text:
            task = "Update deployment checklist"
            assignee = "You"
            deadline = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            confidence = "medium"

    # Save to memory if confirmed
    if task:
        confirmed_tasks.append({
            "task": task,
            "assignee": assignee,
            "deadline": deadline,
            "confidence": confidence,
            "added_on": datetime.now(),
            "source": source,
            "subject_or_channel": subject_or_channel
        })

    return {
        "task": task,
        "assignee": assignee,
        "deadline": deadline,
        "confidence": confidence,
        "source": source,
        "subject_or_channel": subject_or_channel
    }
