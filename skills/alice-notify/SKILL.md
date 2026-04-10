---
name: alice-notify
description: Send a custom notification to a Discord channel through Alice
version: 1.0.0
user-invocable: true
---

# alice-notify

Send a custom notification through Alice to a Discord channel.

## Instructions

1. Ask the user what message they want to send and which channel (`general`, `github`, `jira`, or `commits`).
2. POST the notification to Alice's Discord webhook URL for that channel. The webhook URLs are configured in the `.env` file as `DISCORD_WEBHOOK_GENERAL`, `DISCORD_WEBHOOK_GITHUB`, etc.
3. The payload format is:
   ```json
   {
     "username": "Alice",
     "avatar_url": "https://cdn.discordapp.com/avatars/1448058432920883232/4524fe6126f36c36594fa3c88c4aac3a.png",
     "content": "Your message here"
   }
   ```
4. Report success or failure to the user.
