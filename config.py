"""
Carefam Investor Update Agent — Configuration

To find Slack user IDs:
  Click on a person's profile in Slack → "..." menu → "Copy member ID"
"""

# Team contacts: each person the agent reaches out to
TEAM = [
    {
        "name": "Eyal",
        "role": "CTO",
        "slack_id": "U05EUQK7XPT",
        "sections": ["R&D, Product, Design"],
        "asks": [
            "What shipped this month? Any new features or releases worth highlighting?",
            "Anything major in progress that's worth mentioning (even if not launched yet)?",
            "Any AI/agent updates?",
        ],
    },
    {
        "name": "Molly",
        "role": "Marketplace Lead",
        "slack_id": "U08A0BHQ63H",
        "sections": ["Supply side", "Ops efficiency", "KPIs"],
        "asks": [
            "This month's KPIs (profiles with a match, recruiters, facilities, interviews, candidates started work) + the MoM % changes",
            "What's the headline on the supply/candidate side this month?",
            "Anything notable on ops efficiency — process improvements, funnel changes, anything that moved the needle?",
        ],
    },
    {
        "name": "Tony",
        "role": "AE",
        "slack_id": "U0A11K4VAPK",
        "sections": ["Demand side (new deals, pipeline)"],
        "asks": [
            "Any new customers signed or onboarded this month?",
            "How are pipeline deals progressing? Anything close to closing?",
            "Any expansion within existing customers?",
            "New states or facility types we're entering?",
        ],
    },
    {
        "name": "Terrence",
        "role": "CS",
        "slack_id": "U09JVU635QV",
        "sections": ["Demand side (customer wins, expansions)"],
        "asks": [
            "Any notable wins or success stories with existing customers?",
            "Customers expanding (adding more facilities, new use cases)?",
            "Any strong feedback or signals worth sharing?",
        ],
    },
    {
        "name": "Matan",
        "role": "CEO",
        "slack_id": "U05EJJMUP44",
        "sections": ["Hires", "Strategic updates", "Partnerships", "Other Things Happening", "Asks"],
        "asks": [
            "Any new hires or team changes?",
            "Strategic updates, partnerships, or new product directions?",
            "Conferences or events you attended or are attending?",
            "Anything for the 'Asks' section — intros you're looking for?",
            "Anything else for 'Other Things Happening'?",
        ],
    },
]

# The person who receives the final draft for review
DRAFT_RECIPIENT = "U05EJJMUP44"

# Schedule (day of month)
SCHEDULE = {
    "outreach": 25,   # Send initial messages
    "nudge": 27,      # Remind non-responders
    "escalate": 28,   # Flag to Matan if still missing
    "draft": 29,      # Generate draft
    "deliver": 30,    # Send draft to Matan
}

# Claude model for drafting (Sonnet is cost-effective and high quality)
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Max tokens for draft generation
CLAUDE_MAX_TOKENS = 4096
