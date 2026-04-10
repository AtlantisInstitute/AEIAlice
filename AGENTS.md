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

---

## Software Design Philosophy

These principles (from "A Philosophy of Software Design" by John Ousterhout) are Alice's foundation for all code design, review, and architecture decisions. Apply them when writing code, reviewing code, or advising on design.

### Core Principles

1. **The enemy is complexity.** Every design decision should reduce complexity. Complexity is anything that makes a system hard to understand or modify.
2. **Strategic over tactical.** Never just "get it working." Invest 10-20% of effort in clean design. Working code that is poorly designed is not done.
3. **Make modules deep.** The best modules have simple interfaces but powerful functionality. A deep module hides complexity; a shallow module just shuffles it.
4. **Hide information.** Each module should encapsulate design decisions in its implementation without exposing them in its interface. If the same knowledge appears in multiple modules, that's information leakage — fix it.
5. **General-purpose interfaces are simpler.** Design interfaces to be somewhat general-purpose. A general `insert(position, string)` is simpler and more powerful than separate `backspace()` and `delete()` methods.
6. **Different layer, different abstraction.** Adjacent layers with similar abstractions indicate wrong decomposition. Pass-through methods are a red flag.
7. **Pull complexity downward.** When complexity must exist, put it in the implementation, not the interface. It's better for the implementer to suffer than for every caller to suffer.
8. **Define errors out of existence.** Restructure APIs so error conditions cannot occur. Exception handling is one of the worst sources of complexity.
9. **Design it twice.** Always consider at least two alternatives before committing to a design.
10. **Write comments first.** Comments are a design tool. If you can't describe a clean interface in comments, the design is wrong. Comments should explain *why*, not repeat *what* the code says.
11. **Choose names that create images.** Vague names like `data`, `info`, `result` indicate unclear thinking. If it's hard to name, the design may need work.
12. **Consistency reduces cognitive load.** Same concept, same name, same pattern — everywhere. Don't change established conventions.
13. **Length is not the problem — abstraction is.** A long method with a clean abstraction is better than many tiny methods that fragment the logic.

### Red Flags in Code

| Red Flag | What It Means |
|---|---|
| Shallow module | Interface nearly as complex as implementation |
| Information leakage | Same design decision in multiple modules |
| Pass-through method | Delegates to another method with similar signature |
| Temporal decomposition | Structured by execution order, not information hiding |
| Special-general mixture | General mechanism contains special-case code |
| Conjoined methods | Two methods that can't be understood independently |
| Comment repeats code | `// increment i` for `i++` — says nothing new |
| Vague name | `data`, `tmp`, `handle` — what *kind*? |
| Hard to describe | Convoluted interface comment means convoluted design |

### Knowledge Base

For the full treatment of these principles with examples, edge cases, and chapter-by-chapter detail, read: `knowledge/philosophy-of-software-design.md`
