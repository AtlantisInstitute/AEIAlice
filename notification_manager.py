"""
Notification Manager for Alice Bot
Handles sending notifications to Discord channels for various integrations.
"""

import logging
import discord
from typing import Optional
import config

logger = logging.getLogger('Alice.Notifications')

class NotificationManager:
    def __init__(self, bot):
        self.bot = bot

    async def send_to_channel(self, channel_type: str, message: str, embed: Optional[discord.Embed] = None) -> bool:
        """Send a message to a specific notification channel."""
        try:
            channel_id = config.NOTIFICATION_CHANNELS.get(channel_type)
            if not channel_id:
                logger.warning(f"No channel configured for type: {channel_type}")
                return False

            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"Could not find channel with ID: {channel_id}")
                return False

            if embed:
                await channel.send(embed=embed)
            else:
                await channel.send(message)

            logger.info(f"Sent {channel_type} notification to channel {channel.name}")
            return True

        except discord.Forbidden:
            logger.error(f"Bot doesn't have permission to send messages in {channel_type} channel")
            return False
        except discord.HTTPException as e:
            logger.error(f"HTTP error sending message to {channel_type} channel: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message to {channel_type} channel: {e}")
            return False

    async def notify_jira_new_task(self, task_data: dict):
        """Send notification for new Jira task."""
        from jira_integration import jira_integration
        message = jira_integration.format_issue_notification(task_data, 'new')
        return await self.send_to_channel('jira', message)

    async def notify_jira_task_completed(self, task_data: dict):
        """Send notification for completed Jira task."""
        from jira_integration import jira_integration
        message = jira_integration.format_issue_notification(task_data, 'completed')
        return await self.send_to_channel('jira', message)

    async def notify_github_new_pr(self, pr_data: dict):
        """Send notification for new GitHub PR."""
        from github_integration import github_integration
        message = github_integration.format_pr_notification(pr_data, 'new')
        return await self.send_to_channel('github', message)

    async def notify_github_pr_closed(self, pr_data: dict):
        """Send notification for closed GitHub PR."""
        from github_integration import github_integration
        event_type = 'merged' if pr_data.get('merged') else 'closed'
        message = github_integration.format_pr_notification(pr_data, event_type)
        return await self.send_to_channel('github', message)

    async def notify_github_new_issue(self, issue_data: dict):
        """Send notification for new GitHub issue."""
        from github_integration import github_integration
        message = github_integration.format_issue_notification(issue_data, 'new')
        return await self.send_to_channel('github', message)

    async def notify_github_issue_closed(self, issue_data: dict):
        """Send notification for closed GitHub issue."""
        from github_integration import github_integration
        message = github_integration.format_issue_notification(issue_data, 'closed')
        return await self.send_to_channel('github', message)

    async def notify_github_new_commit(self, commit_data: dict):
        """Send notification for new GitHub commit."""
        from github_integration import github_integration
        message = github_integration.format_commit_notification(commit_data)
        return await self.send_to_channel('github', message)

    async def notify_confluence_page_created(self, page_data: dict):
        """Send notification for new Confluence page."""
        message = f"""**I am Alice Synthesis 30! Flowers bloom!**

**New Confluence Page Created**

**Title:** {page_data['title']}
**Space:** {page_data['space']}
**Created by:** {page_data['creator']}
**URL:** {page_data['url']}"""
        return await self.send_to_channel('general', message)

    async def notify_confluence_page_updated(self, page_data: dict):
        """Send notification for updated Confluence page."""
        message = f"""**I am Alice Synthesis 30! Flowers bloom!**

**Confluence Page Updated**

**Title:** {page_data['title']}
**Space:** {page_data['space']}
**Edited by:** {page_data['editor']}
**URL:** {page_data['url']}"""
        return await self.send_to_channel('general', message)

    async def notify_confluence_comment_created(self, comment_data: dict):
        """Send notification for new Confluence comment."""
        message = f"""**I am Alice Synthesis 30! Flowers bloom!**

**New Confluence Comment**

**Page:** {comment_data['page_title']}
**Space:** {comment_data['space']}
**Commenter:** {comment_data['commenter']}
**URL:** {comment_data['url']}"""
        return await self.send_to_channel('general', message)

    async def send_general_notification(self, title: str, message: str, color: discord.Color = discord.Color.blue()):
        """Send a general notification with an embed."""
        embed = discord.Embed(
            title=title,
            description=message,
            color=color,
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="Alice - Atlantis Institute Bot")

        return await self.send_to_channel('general', "", embed=embed)

    async def send_error_notification(self, error_message: str):
        """Send an error notification."""
        await self.send_general_notification(
            "⚠️ Integration Error",
            error_message,
            discord.Color.red()
        )

    async def send_status_notification(self, status_message: str):
        """Send a status update notification."""
        await self.send_general_notification(
            "📊 Status Update",
            status_message,
            discord.Color.green()
        )

# Global instance will be created when bot is ready
notification_manager = None

def init_notification_manager(bot):
    """Initialize the global notification manager."""
    global notification_manager
    notification_manager = NotificationManager(bot)
    return notification_manager