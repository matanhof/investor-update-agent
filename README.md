# Carefam Investor Update Agent

An autonomous agent that gathers monthly inputs from your team via Slack, drafts investor updates in your voice using Claude, and sends the draft for your review.

## How It Works

1. **Day 0 (25th of each month):** The agent DMs each team member on Slack with tailored questions based on last month's update
2. **Day 2:** Auto-nudges anyone who hasn't responded
3. **Day 3:** Escalates non-responses to Matan
4. **Day 4:** Generates a draft with available inputs (flags missing sections)
5. **Day 5 (30th):** Sends the final draft to Matan for review on Slack

## Setup

### 1. Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. Name it something like "Investor Update Bot" and select your workspace
3. Go to **OAuth & Permissions** → scroll to **Scopes** → add these **Bot Token Scopes**:
   - `chat:write` (send messages)
   - `im:write` (open DMs)
   - `im:read` (read DM responses)
   - `im:history` (read DM history)
   - `users:read` (look up users)
   - `users:read.email` (look up users by email)
4. Go to **Install App** → **Install to Workspace** → Authorize
5. Copy the **Bot User OAuth Token** (starts with `xoxb-`)
6. Go to **Basic Information** → copy the **Signing Secret**

### 2. Get a Claude API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an API key
3. Note: this agent uses Claude Sonnet for cost efficiency (~$0.50/month)

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### 4. Set Up Team Contacts

Edit `config.py` to add Slack user IDs for each team member. To find a user's Slack ID:
- Click on their profile in Slack → click the "..." menu → "Copy member ID"

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Test Locally

```bash
# Send test messages (to yourself only)
python agent.py --test

# Run the full cycle manually
python agent.py --step outreach
python agent.py --step check_responses
python agent.py --step draft
```

### 7. Deploy to Railway

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add your environment variables in Railway's dashboard
4. Add a cron job (Railway supports this natively):
   - Outreach: `0 9 25 * *` (25th of each month at 9am ET)
   - Nudge: `0 9 27 * *` (27th at 9am ET)
   - Escalate: `0 9 28 * *` (28th at 9am ET)
   - Draft: `0 9 29 * *` (29th at 9am ET)
   - Deliver: `0 9 30 * *` (30th at 9am ET)

## File Structure

```
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── config.py             # Team contacts, schedule, settings
├── agent.py              # Main orchestrator
├── slack_client.py       # Slack messaging functions
├── claude_client.py      # Claude API for tailoring questions & drafting
├── state.py              # Tracks who's been contacted, who responded
├── voice_profile.md      # Your writing voice profile
├── outreach_templates.md # Message templates
└── data/
    └── monthly_state.json # Persisted state for current cycle
```
# trigger
