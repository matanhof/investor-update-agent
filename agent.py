"""
Carefam Investor Update Agent — Main Orchestrator

Usage:
    python agent.py --step outreach      # Send initial messages to team
    python agent.py --step check          # Check for responses
    python agent.py --step nudge          # Nudge non-responders
    python agent.py --step escalate       # Escalate to Matan
    python agent.py --step draft          # Generate the update draft
    python agent.py --step deliver        # Send draft to Matan
    python agent.py --test                # Test mode (sends only to Matan)
"""

import argparse
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from config import TEAM, DRAFT_RECIPIENT
import slack_client
import claude_client
import state


def load_last_update() -> str:
    """Load the most recent investor update for context."""
    updates_dir = os.path.join(os.path.dirname(__file__), "data", "past_updates")
    if not os.path.exists(updates_dir):
        return "(No previous update available)"

    # Find the most recent update file
    files = sorted(os.listdir(updates_dir), reverse=True)
    if not files:
        return "(No previous update available)"

    with open(os.path.join(updates_dir, files[0]), "r") as f:
        return f.read()


def load_voice_profile() -> str:
    """Load the voice profile document."""
    profile_path = os.path.join(os.path.dirname(__file__), "voice_profile.md")
    if os.path.exists(profile_path):
        with open(profile_path, "r") as f:
            return f.read()
    return "(Voice profile not found — using defaults)"


def step_outreach(test_mode=False):
    """Step 1: Send tailored outreach messages to each team member."""
    print("\n📤 Starting outreach...\n")

    current_state = state.start_new_cycle()
    last_update = load_last_update()

    targets = TEAM if not test_mode else [p for p in TEAM if p["name"] == "Matan"]

    for person in targets:
        print(f"  Generating message for {person['name']}...")

        # Use Claude to tailor the message based on last month's update
        message = claude_client.tailor_outreach(person, last_update)

        print(f"  Sending to {person['name']} ({person['slack_id']})...")
        result = slack_client.send_dm(person["slack_id"], message)

        if result["ok"]:
            state.record_outreach(
                current_state,
                person["name"],
                result["channel"],
                result["ts"],
            )
            print(f"  ✓ {person['name']} messaged successfully\n")
        else:
            print(f"  ✗ Failed to message {person['name']}: {result['error']}\n")

    state.set_step(current_state, "outreach")
    print("📤 Outreach complete!\n")


def step_check_responses():
    """Check for new responses from team members."""
    print("\n🔍 Checking for responses...\n")

    current_state = state.load_state()

    for name, info in current_state["contacts"].items():
        if info["responded"]:
            print(f"  ✓ {name} already responded")
            continue

        if not info.get("message_ts"):
            continue

        # Check for new messages from this person
        messages = slack_client.get_dm_responses(
            # Find the person's slack_id from TEAM config
            next(p["slack_id"] for p in TEAM if p["name"] == name),
            info["message_ts"],
        )

        if messages:
            # Combine all their messages into one response
            response_text = "\n".join(msg.get("text", "") for msg in messages)
            state.record_response(current_state, name, response_text)
            print(f"  ✓ {name} responded! ({len(messages)} message(s))")
        else:
            print(f"  ○ {name} hasn't responded yet")

    print("\n🔍 Response check complete!\n")


def step_nudge():
    """Nudge team members who haven't responded."""
    print("\n🔔 Sending nudges...\n")

    current_state = state.load_state()
    non_responders = state.get_non_responders(current_state)

    if not non_responders:
        print("  Everyone has responded! No nudges needed.\n")
        return

    for name in non_responders:
        person = next((p for p in TEAM if p["name"] == name), None)
        if not person:
            continue

        info = current_state["contacts"][name]
        if info.get("nudged"):
            print(f"  ○ {name} already nudged, skipping")
            continue

        message = claude_client.generate_nudge(person)
        result = slack_client.send_dm(person["slack_id"], message)

        if result["ok"]:
            state.record_nudge(current_state, name)
            print(f"  ✓ Nudged {name}")
        else:
            print(f"  ✗ Failed to nudge {name}")

    state.set_step(current_state, "nudge")
    print("\n🔔 Nudges complete!\n")


def step_escalate():
    """Escalate non-responses to Matan."""
    print("\n⚠️  Checking for escalations...\n")

    current_state = state.load_state()
    non_responders = state.get_non_responders(current_state)

    # Don't escalate Matan to himself
    non_responders = [n for n in non_responders if n != "Matan"]

    if not non_responders:
        print("  No escalations needed.\n")
        return

    for name in non_responders:
        info = current_state["contacts"][name]
        if info.get("escalated"):
            continue

        message = claude_client.generate_escalation(name)
        result = slack_client.send_dm(DRAFT_RECIPIENT, message)

        if result["ok"]:
            state.record_escalation(current_state, name)
            print(f"  ✓ Escalated {name} to Matan")

    state.set_step(current_state, "escalate")
    print("\n⚠️  Escalations complete!\n")


def step_draft():
    """Generate the investor update draft."""
    print("\n📝 Generating draft...\n")

    # First, do a final check for any new responses
    step_check_responses()

    current_state = state.load_state()
    inputs = state.get_all_inputs(current_state)
    last_update = load_last_update()
    voice_profile = load_voice_profile()

    # Log what we have
    for name, response in inputs.items():
        status = "✓ has input" if response else "✗ missing"
        print(f"  {status}: {name}")

    print("\n  Generating draft with Claude...\n")

    draft = claude_client.generate_draft(inputs, last_update, voice_profile)

    # Save the draft
    current_state["draft"] = draft
    state.save_state(current_state)

    # Also save to a file for easy access
    draft_path = os.path.join(os.path.dirname(__file__), "data", "latest_draft.md")
    os.makedirs(os.path.dirname(draft_path), exist_ok=True)
    with open(draft_path, "w") as f:
        f.write(draft)

    state.set_step(current_state, "draft")
    print(f"  ✓ Draft saved to {draft_path}")
    print("\n📝 Draft generation complete!\n")


def step_deliver():
    """Send the draft to Matan for review."""
    print("\n📬 Delivering draft...\n")

    current_state = state.load_state()
    draft = current_state.get("draft")

    if not draft:
        print("  ✗ No draft found! Run --step draft first.\n")
        return

    # Send the draft to Matan
    header = (
        "📋 *Your investor update draft is ready!*\n\n"
        "Here's what I put together based on the team's inputs. "
        "Please review, edit as needed, and let me know if you'd like any changes.\n\n"
        "---\n\n"
    )

    # Slack has a 4000 char limit per message, so split if needed
    full_message = header + draft
    if len(full_message) <= 4000:
        slack_client.send_dm(DRAFT_RECIPIENT, full_message)
    else:
        # Send in chunks
        slack_client.send_dm(DRAFT_RECIPIENT, header + "_(Draft is long, sending in parts...)_")
        chunks = [draft[i:i + 3500] for i in range(0, len(draft), 3500)]
        for i, chunk in enumerate(chunks):
            slack_client.send_dm(DRAFT_RECIPIENT, f"*Part {i + 1}:*\n\n{chunk}")

    current_state["draft_sent"] = True
    state.save_state(current_state)
    state.set_step(current_state, "deliver")

    print("  ✓ Draft sent to Matan!")
    print("\n📬 Delivery complete!\n")


def main():
    parser = argparse.ArgumentParser(description="Carefam Investor Update Agent")
    parser.add_argument(
        "--step",
        choices=["outreach", "check", "nudge", "escalate", "draft", "deliver"],
        help="Which step to run",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode — only sends to Matan",
    )

    args = parser.parse_args()

    if not args.step and not args.test:
        parser.print_help()
        sys.exit(1)

    if args.test:
        print("\n🧪 TEST MODE — only sending to Matan\n")
        step_outreach(test_mode=True)
        return

    step_map = {
        "outreach": step_outreach,
        "check": step_check_responses,
        "nudge": step_nudge,
        "escalate": step_escalate,
        "draft": step_draft,
        "deliver": step_deliver,
    }

    step_map[args.step]()


if __name__ == "__main__":
    main()
