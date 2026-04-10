"""
Task Scheduler for Alice
Handles background polling tasks for GitHub integration.
Notifications are sent via Discord webhook URLs (HTTP POST).
"""

import logging
import asyncio
import re
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from alice.config import GITHUB_POLL_INTERVAL

logger = logging.getLogger('Alice.Scheduler')


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
            from alice.integrations.github_integration import github_integration

            new_commits = github_integration.get_new_commits()

            for commit in new_commits:
                if re.match(r"Merge branch 'feature/instance\d+'", commit['message']):
                    logger.info(f"Skipping feature/instance merge commit: {commit['sha']} - {commit['message'][:50]}")
                    continue
                logger.info(f"Found new commit: {commit['sha']} - {commit['message'][:50]}")
                self.notification_manager.notify_github_new_commit(commit)
                await asyncio.sleep(1)  # Small delay between notifications

            github_integration.update_last_check()

        except Exception as e:
            logger.error(f"Error checking GitHub commits: {e}")

    async def send_status_update(self):
        """Send a periodic status update."""
        try:
            self.notification_manager.send_status_notification(
                "🤖 Alice integrations are running smoothly!\n"
                "Monitoring Jira tasks and GitHub repositories for updates."
            )
        except Exception as e:
            logger.error(f"Error sending status update: {e}")

    def setup_jobs(self):
        """Setup the scheduled jobs."""
        self.scheduler.add_job(
            self.check_github_commits,
            trigger=IntervalTrigger(seconds=GITHUB_POLL_INTERVAL),
            id='github_commits',
            name='GitHub Commit Polling',
            max_instances=1
        )
        logger.info(f"Scheduled GitHub commit polling every {GITHUB_POLL_INTERVAL} seconds")

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
