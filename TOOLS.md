# Alice - Local Environment Notes

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
