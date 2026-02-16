"""
Claude client — handles tailoring outreach questions and drafting the investor update.
"""

import os
import anthropic
from config import CLAUDE_MODEL, CLAUDE_MAX_TOKENS


def get_client():
    """Initialize Anthropic client."""
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def tailor_outreach(person: dict, last_update: str) -> str:
    """
    Generate a tailored Slack DM for a team member, based on last month's update.

    Args:
        person: dict with name, role, sections, asks
        last_update: the full text of last month's investor update
    
    Returns:
        The message string to send via Slack
    """
    client = get_client()

    prompt = f"""You are a helpful assistant that drafts Slack DMs to collect inputs for a monthly investor update.

You need to write a casual Slack DM to {person['name']} ({person['role']}) asking for their input for this month's investor update.

Their areas of responsibility: {', '.join(person['sections'])}

Standard questions to ask them:
{chr(10).join(f'- {q}' for q in person['asks'])}

Here is last month's investor update for context. Use it to add 1-2 specific follow-up questions about things mentioned last month that are relevant to this person's area:

---
{last_update}
---

Rules:
- Keep it casual — like a quick Slack DM between teammates
- Start with "Hey {person['name']}!" 
- Keep it short — no more than 8-10 lines total
- Include the standard questions PLUS 1-2 tailored follow-ups from last month
- End with something like "A few bullets is totally fine — I'll handle the writing"
- Don't be overly formal or robotic
- Use an occasional emoji but don't overdo it"""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def generate_draft(inputs: dict, last_update: str, voice_profile: str) -> str:
    """
    Generate the investor update draft based on collected inputs.

    Args:
        inputs: dict mapping person names to their responses
        last_update: full text of last month's update (for continuity)
        voice_profile: the voice profile document
    
    Returns:
        The full draft text of the investor update
    """
    client = get_client()

    # Format the inputs
    inputs_text = ""
    for name, response in inputs.items():
        if response:
            inputs_text += f"\n### {name}:\n{response}\n"
        else:
            inputs_text += f"\n### {name}:\n[NO RESPONSE — flag this section]\n"

    prompt = f"""You are an AI assistant that drafts monthly investor updates for Carefam, a healthcare hiring marketplace.

Your job is to write this month's investor update based on the raw inputs provided by the team, following the exact voice and structure described in the voice profile.

## Voice Profile:
{voice_profile}

## Last Month's Update (for continuity and reference):
{last_update}

## Raw Inputs Collected This Month:
{inputs_text}

## Instructions:

1. Follow the EXACT structure from the voice profile:
   - Title (Month 'YY Update)
   - "Dear Investors,"
   - Welcome line with reading time (estimate based on length)
   - TLDR paragraph (semicolon-separated highlights)
   - Month over Month KPIs (use Molly's numbers)
   - Marketplace section with Supply side, Demand side, Operational efficiency
   - R&D, Product, Design
   - Other Things Happening
   - Asks (if provided)
   - Closing and sign-off

2. Write in Matan's voice — direct, transparent, conversational, optimistic but grounded. Use contractions. Occasional emoji is fine (sparingly).

3. The TLDR should be a standalone summary — an investor should be able to read only this and know the state of the business.

4. For any section where input is missing, write: [NEEDS INPUT: description of what's missing]

5. Maintain continuity with last month's update — if a deal or initiative was mentioned, follow up on it naturally.

6. Do NOT fabricate any numbers, names, or facts. Only use information provided in the inputs.

7. Keep the total length to 2-4 minutes of reading time (roughly 500-800 words).

Write the complete investor update now:"""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def generate_nudge(person: dict) -> str:
    """Generate a casual follow-up nudge message."""
    return (
        f"Hey {person['name']}! Just a friendly nudge on the investor update "
        f"— would love to get your input by end of tomorrow. "
        f"Even a quick voice note or a few bullets would be great 🙏"
    )


def generate_escalation(person_name: str) -> str:
    """Generate an escalation message to Matan about a non-responder."""
    return (
        f"Hey Matan — heads up, I haven't heard back from {person_name} yet "
        f"for the investor update. Want me to draft their section based on "
        f"what I know, or do you want to ping them?"
    )
