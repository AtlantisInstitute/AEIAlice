# Alice Architecture

## Overview

Alice is a notification daemon. She does not connect to the Discord gateway — she posts messages to Discord channels via webhook HTTP POSTs. Inbound events arrive via Flask webhook endpoints or are detected by polling.

## Data Flow

### Webhook Path (real-time)

```
GitHub/Jira/Confluence
        │
        ▼
  Flask Server (port 8080)
  ┌─────────────────────┐
  │  WebhookHandler     │
  │  - /webhooks/github │
  │  - /webhooks/jira   │
  │  - /webhooks/confluence │
  └────────┬────────────┘
           │ verifies signature, parses event
           ▼
  NotificationManager
  ┌─────────────────────┐
  │  format message      │
  │  POST to Discord     │
  │  webhook URL         │
  └────────┬────────────┘
           │
           ▼
     Discord Channel
```

### Polling Path (fallback for commits)

```
  APScheduler (every 60s)
        │
        ▼
  GitHubIntegration
  ┌──────────────────────┐
  │  fetch recent commits │
  │  compare known_commits│
  │  detect new commits   │
  └────────┬─────────────┘
           │
           ▼
  NotificationManager
  ┌─────────────────────┐
  │  format message      │
  │  POST to Discord     │
  │  webhook URL         │
  └────────┬────────────┘
           │
           ▼
     Discord Channel
```

## Module Responsibilities

| Module | Location | Role |
|---|---|---|
| `bot.py` | `alice/bot.py` | Orchestrator — PID mgmt, threading, signal handling, startup |
| `config.py` | `alice/config.py` | Loads all settings from environment variables |
| `notification_manager.py` | `alice/notifications/` | Formats events into Discord messages, POSTs via webhook URLs |
| `webhook_handler.py` | `alice/handlers/` | Flask server, receives/verifies/routes inbound webhooks |
| `task_scheduler.py` | `alice/scheduling/` | APScheduler, polls GitHub for commits on an interval |
| `github_integration.py` | `alice/integrations/` | PyGithub wrapper, tracks known PRs/issues/commits |
| `jira_integration.py` | `alice/integrations/` | Jira API wrapper, tracks known issues, JQL queries |

## Singleton Pattern

Each integration module exports a module-level instance and an init function. The bot orchestrator initializes them at startup and wires them together via `set_notification_manager()`.

## Alice and OpenClaw

Alice and OpenClaw are complementary services sharing the same Discord server:

- **Alice** is a background daemon that monitors GitHub/Jira/Confluence and posts notifications.
- **OpenClaw** is a Discord bot (gateway connection) that handles AI conversations and interactive commands.

They run as separate processes and do not share state.
