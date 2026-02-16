"""
State management — tracks who's been contacted, who's responded, and collected inputs.
Persists to a JSON file so state survives restarts.
"""

import json
import os
from datetime import datetime

STATE_DIR = os.path.join(os.path.dirname(__file__), "data")
STATE_FILE = os.path.join(STATE_DIR, "monthly_state.json")


def _ensure_dir():
    """Create data directory if it doesn't exist."""
    os.makedirs(STATE_DIR, exist_ok=True)


def load_state() -> dict:
    """Load current month's state from disk."""
    _ensure_dir()
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return _new_state()


def save_state(state: dict):
    """Save state to disk."""
    _ensure_dir()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def _new_state() -> dict:
    """Create a fresh state for a new monthly cycle."""
    now = datetime.now()
    return {
        "month": now.strftime("%B"),
        "year": now.strftime("%Y"),
        "cycle_started": now.isoformat(),
        "contacts": {},  # name -> {messaged, message_ts, channel, responded, response_text}
        "draft": None,
        "draft_sent": False,
        "step": "not_started",  # not_started, outreach, nudge, escalate, draft, deliver, done
    }


def start_new_cycle() -> dict:
    """Reset state for a new month."""
    state = _new_state()
    save_state(state)
    return state


def record_outreach(state: dict, name: str, channel: str, message_ts: str):
    """Record that we sent an outreach message to someone."""
    state["contacts"][name] = {
        "messaged": True,
        "message_ts": message_ts,
        "channel": channel,
        "responded": False,
        "response_text": None,
        "nudged": False,
        "escalated": False,
    }
    save_state(state)


def record_response(state: dict, name: str, response_text: str):
    """Record a team member's response."""
    if name in state["contacts"]:
        state["contacts"][name]["responded"] = True
        state["contacts"][name]["response_text"] = response_text
        save_state(state)


def record_nudge(state: dict, name: str):
    """Record that we sent a nudge to someone."""
    if name in state["contacts"]:
        state["contacts"][name]["nudged"] = True
        save_state(state)


def record_escalation(state: dict, name: str):
    """Record that we escalated a non-response."""
    if name in state["contacts"]:
        state["contacts"][name]["escalated"] = True
        save_state(state)


def get_non_responders(state: dict) -> list[str]:
    """Get list of names who haven't responded yet."""
    return [
        name for name, info in state["contacts"].items()
        if info["messaged"] and not info["responded"]
    ]


def get_all_inputs(state: dict) -> dict:
    """Get all collected inputs as a dict of name -> response_text."""
    return {
        name: info.get("response_text")
        for name, info in state["contacts"].items()
    }


def set_step(state: dict, step: str):
    """Update the current step in the cycle."""
    state["step"] = step
    save_state(state)
