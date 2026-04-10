# Alice - Operational Rules

## Notification Routing

| Event Source | Event Type | Discord Channel |
|---|---|---|
| GitHub | push (commits) | `commits` |
| GitHub | pull_request, issues | `github` |
| Jira | issue_created, issue_updated | `jira` |
| Confluence | page/comment events | `general` |
| Alice | errors, status updates | `general` |

## Webhook Signature Verification

- GitHub webhooks: verify `X-Hub-Signature-256` header using HMAC-SHA256 if a webhook secret is configured. If no secret is set, accept all payloads.
- Jira webhooks: verify `X-Jira-Signature` header using HMAC-SHA256 if a webhook secret is configured.
- Confluence webhooks: no signature verification (Atlassian does not send one by default).

## Polling and Deduplication

- GitHub commits are polled every 60 seconds via APScheduler as a fallback for webhooks.
- Each integration maintains in-memory sets (`known_commits`, `known_issues`, `known_prs`) to deduplicate events.
- Push webhook handler also checks `known_commits` before sending notifications.
- Merge commits matching `Merge branch 'feature/instanceN'` are silently skipped.

## Startup Sequence

1. Kill any existing Alice instances (PID-based detection).
2. Write PID file.
3. Initialize NotificationManager.
4. Start Flask webhook server on a background thread (port 8080).
5. Seed `known_commits` with the 50 most recent commits per repo — this prevents notification spam on restart.
6. Start APScheduler and run an initial commit check.
7. Enter the async event loop.

## Error Handling

- Errors during webhook processing return HTTP 500 but do not crash the service.
- Errors during polling are logged and retried on the next interval.
- Critical integration errors are sent to the `general` Discord channel via `send_error_notification`.
- Alice must never crash silently — all exceptions are logged.

## Security

- API tokens, webhook URLs, and secrets are loaded from environment variables (`.env` file).
- Tokens must never appear in log output or Discord notifications.
- The `.env` file must never be committed to version control.
