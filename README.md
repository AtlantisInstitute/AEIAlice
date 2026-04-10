# Alice

**Alice** is the notification daemon for the Atlantis Institute development team. She monitors GitHub, Jira, and Confluence for events and sends formatted notifications to Discord channels via webhook HTTP posts.

Alice is **not** a Discord bot — she does not connect to the Discord gateway. AI conversations and interactive Discord commands are handled by [OpenClaw](openclaw/), a separate TypeScript project in this repo.

## Features

- **Real-time webhooks** — receives GitHub, Jira, and Confluence events via Flask endpoints
- **Commit polling** — polls GitHub every 60 seconds as a fallback for push events
- **Discord notifications** — posts formatted messages to channel-specific Discord webhooks
- **Deduplication** — tracks known commits, PRs, and issues to avoid duplicate notifications
- **Health endpoint** — `GET /webhooks/health` for monitoring

## Project Structure

```
Alice/
├── .env.example              # Required environment variables
├── pyproject.toml            # Python project metadata
├── requirements.txt          # Dependencies
├── SOUL.md                   # Alice personality guide
├── AGENTS.md                 # Operational rules and guardrails
├── TOOLS.md                  # Local environment notes
│
├── alice/                    # Main Python package
│   ├── __main__.py           # Entry point: python -m alice
│   ├── bot.py                # Orchestrator (PID, threads, signals)
│   ├── config.py             # Env-based configuration
│   ├── integrations/         # GitHub and Jira API clients
│   ├── handlers/             # Flask webhook server
│   ├── notifications/        # Discord webhook delivery
│   └── scheduling/           # APScheduler commit polling
│
├── skills/                   # OpenClaw skills
│   ├── alice-status/         # Check Alice health
│   └── alice-notify/         # Send notification through Alice
│
├── openclaw/                 # Separate TypeScript project (Discord bot)
├── tests/
└── docs/
    └── architecture.md       # Agent-readable architecture overview
```

## Setup

### Prerequisites

- Python 3.8+
- A Discord server with webhook URLs configured (Server Settings > Integrations > Webhooks)

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your actual values:
   - Discord webhook URLs for each notification channel
   - GitHub Personal Access Token with `repo` scope
   - Jira email and API token
   - Discord channel IDs

3. **Never commit `.env`** — it is excluded by `.gitignore`.

### Webhook Setup (Optional — for real-time notifications)

Configure webhooks in each service to point at your Alice instance:

- **GitHub**: Repository Settings > Webhooks > `https://your-host/webhooks/github`
- **Jira**: System > Webhooks > `https://your-host/webhooks/jira`
- **Confluence**: Administration > Webhooks > `https://your-host/webhooks/confluence`

For local development, use [ngrok](https://ngrok.com/) to expose port 8080:
```bash
ngrok http 8080
```

## Usage

```bash
python -m alice
```

Alice will:
1. Start the Flask webhook server on port 8080
2. Begin polling GitHub for new commits every 60 seconds
3. Send notifications to Discord when events are detected

### Health Check

```bash
curl http://localhost:8080/webhooks/health
```

### Stopping

Send `SIGTERM` or `SIGINT` (Ctrl+C). Alice cleans up her PID file and stops gracefully.

## Integration Status

| Integration | Method | Details |
|---|---|---|
| GitHub | Webhooks + Polling | PRs, issues, commits for Atlantisinstitute/AtlantisEons |
| Jira | Webhooks | New/completed issues in project AEI |
| Confluence | Webhooks | Page and comment events |
| Discord | Webhook HTTP POST | Channel-specific notification delivery |

## OpenClaw

The `openclaw/` directory contains a separate TypeScript project — a local-first personal AI assistant that handles Discord bot gateway connections and interactive AI conversations. Alice and OpenClaw complement each other: OpenClaw handles chat, Alice handles notifications.

## Security

- All secrets are stored in `.env` (excluded from version control)
- Webhook signatures are verified when secrets are configured
- API tokens are never logged or included in notifications

## License

This project is proprietary to Atlantis Institute.
