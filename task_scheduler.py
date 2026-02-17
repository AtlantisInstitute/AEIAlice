"""
Task Scheduler for Alicebot
Handles background polling tasks for Jira and GitHub integrations.
"""

import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import config

logger = logging.getLogger('Alicebot.Scheduler')

# Polling interval for GitHub commits (in seconds)
GITHUB_POLL_INTERVAL = 60  # Check every 60 seconds

class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.notification_manager = None

    def set_notification_manager(self, manager):
        """Set the notification manager for sending notifications."""
        self.notification_manager = manager

    async def check_github_commits(self):
        """Check for new GitHub commits and send notifications."""
        try:
            from github_integration import github_integration

            # Get new commits since last check
            new_commits = github_integration.get_new_commits()

            for commit in new_commits:
                logger.info(f"Found new commit: {commit['sha']} - {commit['message'][:50]}")
                await self.notification_manager.notify_github_new_commit(commit)
                await asyncio.sleep(1)  # Small delay between notifications

            # Update the last check time
            github_integration.update_last_check()

        except Exception as e:
            logger.error(f"Error checking GitHub commits: {e}")

    async def send_status_update(self):
        """Send a periodic status update."""
        try:
            await self.notification_manager.send_status_notification(
                "🤖 Alicebot integrations are running smoothly!\n"
                "Monitoring Jira tasks and GitHub repositories for updates."
            )
        except Exception as e:
            logger.error(f"Error sending status update: {e}")

    def setup_jobs(self):
        """Setup the scheduled jobs."""
        # GitHub commit polling (runs alongside webhooks as fallback)
        self.scheduler.add_job(
            self.check_github_commits,
            trigger=IntervalTrigger(seconds=GITHUB_POLL_INTERVAL),
            id='github_commits',
            name='GitHub Commit Polling',
            max_instances=1
        )
        logger.info(f"Scheduled GitHub commit polling every {GITHUB_POLL_INTERVAL} seconds")

        # Status update job (daily) - Disabled to avoid chat spam
        # Users can check bot status using !integrations command
        # self.scheduler.add_job(
        #     self.send_status_update,
        #     trigger=IntervalTrigger(hours=24),
        #     id='status_update',
        #     name='Daily Status Update',
        #     max_instances=1
        # )
        # logger.info("Scheduled daily status updates")

    async def start(self):
        """Start the scheduler."""
        if not self.notification_manager:
            raise ValueError("Notification manager must be set before starting scheduler")

        self.setup_jobs()
        self.scheduler.start()
        logger.info("Task scheduler started")

        # Do an initial check for GitHub commits on startup
        logger.info("Running initial GitHub commit check...")
        await self.check_github_commits()

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Task scheduler stopped")

# Global instance
task_scheduler = TaskScheduler()