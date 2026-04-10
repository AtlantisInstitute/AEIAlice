"""
Notification Manager for Alice
Handles sending notifications to Discord channels via webhook URLs.
OpenClaw now owns the Discord bot gateway connection for AI conversations.
This module posts notifications using Discord Webhook URLs (HTTP POST).
"""

import logging
import requests
import json
from typing import Optional
import config

logger = logging.getLogger('Alice.Notifications')


class NotificationManager:
    def __init__(self):
        self.bot_name = "Alice"
        self.avatar_url = "https://cdn.discordapp.com/avatars/1448058432920883232/4524fe6126f36c36594fa3c88c4aac3a.png"

    def send_to_channel(self, channel_type: str, message: str, embed: Optional[dict] = None) -> bool:
        """Send a message to a Discord channel via webhook URL."""
        try:
            webhook_url = config.DISCORD_WEBHOOKS.get(channel_type)
            if not webhook_url:
                logger.warning(f"No webhook URL configured for channel type: {channel_type}")
                return False

            payload = {"username": self.bot_name, "avatar_url": self.avatar_url}

            if embed:
                payload["embeds"] = [embed]
            else:
                payload["content"] = message

            response = requests.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code in (200, 204):
                logger.info(f"Sent {channel_type} notification via webhook")
                return True
            else:
                logger.error(f"Webhook POST failed for {channel_type}: {response.status_code} {response.text}")
                return False

        except requests.exceptions.Timeout:
            logger.error(f"Webhook timeout for {channel_type} channel")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Webhook error for {channel_type} channel: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending to {channel_type} channel: {e}")
            return False

    def notify_jira_new_task(self, task_data: dict):
        """Send notification for new Jira task."""
        from jira_integration import jira_integration
        message = jira_integration.format_issue_notification(task_data, 'new')
        return self.send_to_channel('jira', message)

    def notify_jira_task_completed(self, task_data: dict):
        """Send notification for completed Jira task."""
        from jira_integration import jira_integration
        message = jira_integration.format_issue_notification(task_data, 'completed')
        return self.send_to_channel('jira', message)

    def notify_github_new_pr(self, pr_data: dict):
        """Send notification for new GitHub PR."""
        from github_integration import github_integration
        message = github_integration.format_pr_notification(pr_data, 'new')
        return self.send_to_channel('github', message)

    def notify_github_pr_closed(self, pr_data: dict):
        """Send notification for closed GitHub PR."""
        from github_integration import github_integration
        event_type = 'merged' if pr_data.get('merged') else 'closed'
        message = github_integration.format_pr_notification(pr_data, event_type)
        return self.send_to_channel('github', message)

    def notify_github_new_issue(self, issue_data: dict):
        """Send notification for new GitHub issue."""
        from github_integration import github_integration
        message = github_integration.format_issue_notification(issue_data, 'new')
        return self.send_to_channel('github', message)

    def notify_github_issue_closed(self, issue_data: dict):
        """Send notification for closed GitHub issue."""
        from github_integration import github_integration
        message = github_integration.format_issue_notification(issue_data, 'closed')
        return self.send_to_channel('github', message)

    def notify_github_new_commit(self, commit_data: dict):
        """Send notification for new GitHub commit."""
        from github_integration import github_integration
        message = github_integration.format_commit_notification(commit_data)
        return self.send_to_channel('commits', message)

    def notify_confluence_page_created(self, page_data: dict):
        """Send notification for new Confluence page."""
        message = f"""**I am Alice! Flowers bloom!**

📄 **New Confluence Page Created**

**Title:** {page_data['title']}
**Space:** {page_data['space']}
**Created by:** {page_data['creator']}
**URL:** {page_data['url']}"""
        return self.send_to_channel('general', message)

    def notify_confluence_page_updated(self, page_data: dict):
        """Send notification for updated Confluence page."""
        message = f"""**I am Alice! Flowers bloom!**

📝 **Confluence Page Updated**

**Title:** {page_data['title']}
**Space:** {page_data['space']}
**Edited by:** {page_data['editor']}
**URL:** {page_data['url']}"""
        return self.send_to_channel('general', message)

    def notify_confluence_comment_created(self, comment_data: dict):
        """Send notification for new Confluence comment."""
        message = f"""**I am Alice! Flowers bloom!**

💬 **New Confluence Comment**

**Page:** {comment_data['page_title']}
**Space:** {comment_data['space']}
**Commenter:** {comment_data['commenter']}
**URL:** {comment_data['url']}"""
        return self.send_to_channel('general', message)

    def send_general_notification(self, title: str, message: str, color: int = 0x3498db):
        """Send a general notification with an embed."""
        embed = {
            "title": title,
            "description": message,
            "color": color,
            "footer": {"text": "Alice - Atlantis Institute Bot"}
        }
        return self.send_to_channel('general', "", embed=embed)

    def send_error_notification(self, error_message: str):
        """Send an error notification."""
        self.send_general_notification(
            "⚠️ Integration Error",
            error_message,
            color=0xe74c3c
        )

    def send_status_notification(self, status_message: str):
        """Send a status update notification."""
        self.send_general_notification(
            "📊 Status Update",
            status_message,
            color=0x2ecc71
        )


# Global instance
notification_manager = None


def init_notification_manager():
    """Initialize the global notification manager."""
    global notification_manager
    notification_manager = NotificationManager()
    return notification_manager
