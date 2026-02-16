"""
Slack client — handles sending DMs and reading responses.
"""

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def get_client():
    """Initialize Slack client."""
    return WebClient(token=os.environ["SLACK_BOT_TOKEN"])


def send_dm(slack_id: str, message: str) -> dict:
    """Send a direct message to a user by their Slack user ID."""
    client = get_client()
    try:
        # Open a DM channel with the user
        response = client.conversations_open(users=[slack_id])
        channel_id = response["channel"]["id"]

        # Send the message
        result = client.chat_postMessage(channel=channel_id, text=message)
        print(f"✓ Message sent to {slack_id} in channel {channel_id}")
        return {"ok": True, "channel": channel_id, "ts": result["ts"]}

    except SlackApiError as e:
        print(f"✗ Failed to send message to {slack_id}: {e.response['error']}")
        return {"ok": False, "error": e.response["error"]}


def get_dm_responses(slack_id: str, since_ts: str) -> list[dict]:
    """
    Read messages from a DM conversation with a user since a given timestamp.
    Returns messages FROM the user (not from the bot).
    """
    client = get_client()
    try:
        # Open the DM channel
        response = client.conversations_open(users=[slack_id])
        channel_id = response["channel"]["id"]

        # Fetch message history since the outreach was sent
        result = client.conversations_history(
            channel=channel_id,
            oldest=since_ts,
            limit=50,
        )

        # Filter to only messages from the user (not the bot)
        user_messages = [
            msg for msg in result.get("messages", [])
            if msg.get("user") == slack_id and msg.get("type") == "message"
        ]

        return user_messages

    except SlackApiError as e:
        print(f"✗ Failed to read messages from {slack_id}: {e.response['error']}")
        return []


def get_user_name(slack_id: str) -> str:
    """Get a user's display name from their Slack ID."""
    client = get_client()
    try:
        result = client.users_info(user=slack_id)
        profile = result["user"]["profile"]
        return profile.get("real_name", profile.get("display_name", "Unknown"))
    except SlackApiError:
        return "Unknown"
