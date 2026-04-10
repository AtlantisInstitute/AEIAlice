---
name: alice-status
description: Check if the Alice notification service is running and healthy
version: 1.0.0
user-invocable: true
---

# alice-status

Check the health of the Alice notification service.

## Instructions

1. Send a GET request to `http://localhost:8080/webhooks/health`.
2. If the response is `{"status": "healthy", "service": "alice-notifications"}`, report that Alice is running and healthy.
3. If the request fails or times out, report that Alice appears to be down.
4. Optionally, check for a running process by looking for `alice.pid` in the project root directory.
