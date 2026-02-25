"""AI Agent for task completion conversations
Provides both conversational responses and actionable operations that modify
the local `data/tasks.json` store (mark complete, set reminders, reassign,
add comments). Uses a lightweight NLP heuristic and optionally spaCy if
available, but always falls back to deterministic rule-based handling so
the agent works offline for a hackathon/demo environment.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Optional spaCy-based NLP agent. If spaCy is unavailable, fall back to the rule-based TaskAgent.
try:
    import spacy
    try:
        _nlp = spacy.load("en_core_web_sm")
    except Exception:
        try:
            _nlp = spacy.load("en")
        except Exception:
            _nlp = None
except Exception:
    _nlp = None


# Path to data/tasks.json (project root is two levels up from this file)
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "tasks.json"


def load_tasks() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []


def save_tasks(tasks: List[Dict[str, Any]]) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)


def _find_task_index(ref: Union[int, str]) -> Optional[int]:
    """Resolve a task reference to an index.

    Accepts either an integer index, or a short substring of the task text.
    Returns the first matching index or None if not found.
    """
    tasks = load_tasks()
    if isinstance(ref, int):
        if 0 <= ref < len(tasks):
            return ref
        return None
    # try numeric string
    try:
        idx = int(ref)
        if 0 <= idx < len(tasks):
            return idx
    except Exception:
        pass
    q = str(ref).lower()
    for i, t in enumerate(tasks):
        if q in t.get("task", "").lower():
            return i
    return None


class TaskAgent:
    """AI Agent that helps users complete tasks through conversation and actions."""

    def __init__(self):
        self.task_keywords = {
            "send": ["send", "email", "submit"],
            "review": ["review", "check", "verify"],
            "schedule": ["schedule", "book", "meeting", "call"],
            "approve": ["approve", "accept", "authorize"],
            "process": ["process", "handle", "execute"],
            "invoice": ["invoice", "billing", "payment"],
            "training": ["training", "learn", "course"],
            "feedback": ["feedback", "comment", "opinion"],
        }

    def categorize_task(self, task_description: str) -> str:
        task_lower = task_description.lower()
        for category, keywords in self.task_keywords.items():
            for keyword in keywords:
                if keyword in task_lower:
                    return category
        return "general"

    def get_response(self, task_description: str, user_message: str, task_owner: str = "You") -> Dict[str, Any]:
        """Return a conversational response and a suggested `action` the agent can take.

        The `action` value is a short token like 'complete', 'send', 'schedule', 'guide', etc.
        """
        category = self.categorize_task(task_description)
        text = user_message.lower()

        if any(w in text for w in ["done", "completed", "finished", "complete"]):
            return {
                "response": f"✅ Marking '{task_description}' complete.",
                "action": "complete",
                "confidence": "high",
            }

        if any(w in text for w in ["help", "how", "guide", "steps", "what"]):
            return {
                "response": f"I can guide you through: {task_description}. Tell me which step you need help with.",
                "action": "guide",
                "confidence": "medium",
            }

        if any(w in text for w in ["send", "email", "submit"]):
            return {
                "response": f"I can send or prepare this item for you: {task_description}. Confirm recipients or provide message body.",
                "action": "send",
                "confidence": "high",
            }

        if any(w in text for w in ["schedule", "book", "when", "time", "date"]):
            return {
                "response": f"I can schedule '{task_description}'. Please provide a preferred date/time.",
                "action": "schedule",
                "confidence": "medium",
            }

        if any(w in text for w in ["reassign", "assign to", "change owner", "assign"]):
            return {
                "response": f"Who should I assign '{task_description}' to?",
                "action": "reassign",
                "confidence": "medium",
            }

        # default acknowledge
        return {
            "response": f"Got it. For '{task_description}' I can guide, send, schedule, reassign, or mark complete. What would you like me to do?",
            "action": "acknowledge",
            "confidence": "low",
        }

    # Action implementations that modify data/tasks.json
    def mark_complete(self, task_ref: Union[int, str], note: Optional[str] = None) -> Dict[str, Any]:
        idx = _find_task_index(task_ref)
        if idx is None:
            return {"success": False, "message": "Task not found"}
        tasks = load_tasks()
        tasks[idx]["status"] = "completed"
        tasks[idx]["completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if note:
            tasks[idx].setdefault("agent_notes", []).append({"when": tasks[idx]["completed_date"], "note": note})
        save_tasks(tasks)
        return {"success": True, "message": "Task marked complete", "index": idx}

    def set_reminder(self, task_ref: Union[int, str], hours: int = 1) -> Dict[str, Any]:
        idx = _find_task_index(task_ref)
        if idx is None:
            return {"success": False, "message": "Task not found"}
        tasks = load_tasks()
        tasks[idx]["reminder_hours"] = int(hours)
        tasks[idx]["reminder"] = f"{hours} hour(s) before"
        tasks[idx]["reminder_triggered"] = False
        save_tasks(tasks)
        return {"success": True, "message": "Reminder set", "index": idx}

    def reassign(self, task_ref: Union[int, str], new_owner: str) -> Dict[str, Any]:
        idx = _find_task_index(task_ref)
        if idx is None:
            return {"success": False, "message": "Task not found"}
        tasks = load_tasks()
        old = tasks[idx].get("owner")
        tasks[idx]["owner"] = new_owner
        save_tasks(tasks)
        return {"success": True, "message": f"Reassigned from {old} to {new_owner}", "index": idx}

    def add_comment(self, task_ref: Union[int, str], comment: str, author: str = "agent") -> Dict[str, Any]:
        idx = _find_task_index(task_ref)
        if idx is None:
            return {"success": False, "message": "Task not found"}
        tasks = load_tasks()
        entry = {"when": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "author": author, "comment": comment}
        tasks[idx].setdefault("comments", []).append(entry)
        save_tasks(tasks)
        return {"success": True, "message": "Comment added", "index": idx}


class NLPAgent(TaskAgent):
    """A lightweight NLP-powered agent using spaCy when available.

    Falls back to TaskAgent behaviour when spaCy/model is not available.
    """

    def __init__(self):
        super().__init__()
        self.nlp = _nlp

    def _extract_intent(self, user_message: str) -> str:
        text = user_message.lower()
        if any(w in text for w in ["done", "completed", "finished", "complete"]):
            return "complete"
        if any(w in text for w in ["help", "how", "guide", "steps", "what"]):
            return "guide"
        if any(w in text for w in ["schedule", "book", "meeting", "call", "time", "date"]):
            return "schedule"
        if any(w in text for w in ["send", "email", "submit"]):
            return "send"
        if any(w in text for w in ["approve", "approve this", "sign off", "authorize"]):
            return "approve"
        if any(w in text for w in ["reassign", "assign to", "assign"]):
            return "reassign"
        if self.nlp:
            doc = self.nlp(user_message)
            for token in doc:
                if token.dep_ == "ROOT":
                    lemma = token.lemma_.lower()
                    if lemma in ["send", "schedule", "approve", "review", "process", "complete", "reassign"]:
                        return lemma
        return "acknowledge"

    def get_response(self, task_description: str, user_message: str, task_owner: str = "You") -> Dict[str, Any]:
        if not self.nlp:
            return super().get_response(task_description, user_message, task_owner)
        intent = self._extract_intent(user_message)
        if intent == "complete":
            return {"response": f"✅ Got it — I'll mark '{task_description}' complete.", "action": "complete", "confidence": "high"}
        if intent in ["send", "schedule", "approve", "review", "process", "reassign"]:
            return super().get_response(task_description, user_message, task_owner)
        return super().get_response(task_description, user_message, task_owner)


def get_ai_response(task_description: str, user_message: str, task_owner: str = "You", auto_execute: bool = False, task_ref: Optional[Union[int, str]] = None) -> Dict[str, Any]:
    """Get an AI response and optionally execute the suggested action on the task store.

    If `auto_execute` is True and the agent suggests an actionable `action` and
    `task_ref` is supplied, the corresponding data mutation will be executed.
    """
    agent = NLPAgent() if _nlp else TaskAgent()
    resp = agent.get_response(task_description, user_message, task_owner)

    # If requested, execute certain actions automatically
    if auto_execute and task_ref is not None and resp.get("action"):
        action = resp.get("action")
        if action == "complete":
            result = agent.mark_complete(task_ref, note=user_message)
            resp["executed"] = result
        elif action == "schedule":
            # naive: expect user_message contains relative time; default to 1 hour
            resp["executed"] = agent.set_reminder(task_ref, hours=1)
        elif action == "send":
            # record that agent prepared/sent the item
            resp["executed"] = agent.add_comment(task_ref, f"Sent by agent: {user_message}")
        elif action == "reassign":
            # attempt to extract new owner name; naive parse: last token
            parts = user_message.split()
            new_owner = parts[-1] if len(parts) > 0 else ""
            resp["executed"] = agent.reassign(task_ref, new_owner)
        else:
            resp["executed"] = {"success": False, "message": "No execution rule for action"}

    return resp


def process_task_action(task_ref: Union[int, str], action_type: str, **kwargs) -> Dict[str, Any]:
    """Execute a specific action on a task by reference.

    action_type can be: 'complete', 'set_reminder', 'reassign', 'comment'.
    """
    agent = NLPAgent() if _nlp else TaskAgent()
    if action_type == "complete":
        return agent.mark_complete(task_ref, note=kwargs.get("note"))
    if action_type == "set_reminder":
        hours = int(kwargs.get("hours", 1))
        return agent.set_reminder(task_ref, hours=hours)
    if action_type == "reassign":
        new_owner = kwargs.get("new_owner", "")
        return agent.reassign(task_ref, new_owner)
    if action_type == "comment":
        comment = kwargs.get("comment", "")
        return agent.add_comment(task_ref, comment, author=kwargs.get("author", "agent"))
    return {"success": False, "message": "Unknown action"}


if __name__ == "__main__":
    # Quick manual smoke test
    print("ai_agent.py smoke test")
    tasks = load_tasks()
    print(f"Loaded {len(tasks)} tasks")
    agent = NLPAgent() if _nlp else TaskAgent()
    if tasks:
        # show a sample response
        print(agent.get_response(tasks[0].get("task", ""), "Please mark this complete"))
        print(process_task_action(0, "comment", comment="Agent test comment"))
