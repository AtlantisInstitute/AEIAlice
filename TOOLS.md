# Alice - Local Environment Notes

## AtlantisEons Project (Primary Codebase)

- **Local path**: `/Users/danielvargas/Documents/Unreal Projects/AtlantisEons/`
- **GitHub**: https://github.com/AtlantisInstitute/AtlantisEons
- **Engine**: Unreal Engine
- **What it is**: The Atlantis Eons game — this is the main project Alice supports
- You have full read/write access to this directory. You can read code, edit files, run git commands, build, and test.
- When asked about "the project", "the game", or "AtlantisEons", this is what they mean.

## Memory (MCP Knowledge Graphs)

Alice has two separate memory servers:

### Alice's Own Memory (`memory__` tools) — READ + WRITE
- **Storage**: `/Users/danielvargas/Documents/Alice/memory/alice-knowledge.json`
- **Purpose**: ALL of Alice's knowledge — AtlantisEons learnings, other projects, user preferences, everything
- **Write all new knowledge here**, including things you learn about AtlantisEons

### AtlantisEons Project Memory (`atlantiseons-memory__` tools) — READ ONLY
- **Storage**: `/Users/danielvargas/Documents/Unreal Projects/AtlantisEons/logs-and-data/memory.jsonl`
- **Maintained by**: Claude Code sessions in the AtlantisEons project
- **Purpose**: The master AtlantisEons knowledge base — architecture, patterns, conventions, decisions
- When asked about AtlantisEons, **always search this memory first** using `atlantiseons-memory__search_nodes`
- **NEVER write to this memory.** It is read-only for you. Only Claude Code sessions update it.
- Do NOT use `atlantiseons-memory__create_entities` or `atlantiseons-memory__create_relations`

Both use `search_nodes` to recall knowledge. Only use `create_entities`/`create_relations` on your own memory (`memory__`). Memory persists across sessions.

## Discord

- **Server**: Atlantis Institute
- **Channel IDs**: configured via environment variables (see `.env.example`)
- **Webhook URLs**: each notification channel has its own Discord webhook URL

## Jira

- **Instance**: https://atlantisinstitute.atlassian.net
- **Project key**: AEI
- **Auth**: basic auth with email + API token

## GitHub

- **Repos monitored**: Atlantisinstitute/AtlantisEons
- **Auth**: Personal Access Token (classic) with `repo` scope

## Confluence

- **Instance**: https://atlantisinstitute.atlassian.net/wiki

## Webhook Endpoints

All endpoints are served by Flask on a single port:

- `POST /webhooks/github` — GitHub webhook receiver
- `POST /webhooks/jira` — Jira webhook receiver
- `POST /webhooks/confluence` — Confluence webhook receiver
- `GET  /webhooks/health` — health check (returns `{"status": "healthy"}`)

Default bind: `0.0.0.0:8080`

## Tunnel

Use **ngrok** to expose the local webhook server to the internet for development:

```
ngrok http 8080
```

Then configure the ngrok HTTPS URL as the webhook payload URL in GitHub/Jira/Confluence settings.

## Process Management

- **PID file**: `alice.pid` in the project root
- **macOS auto-start**: launchd plist (log at `launchd.log`)
- **Run command**: `python -m alice`
- **Stop**: send SIGTERM or SIGINT; Alice cleans up PID file and stops gracefully
