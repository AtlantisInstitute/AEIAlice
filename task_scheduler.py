"""
Task Scheduler for Alice Bot
Handles background polling tasks for Jira and GitHub integrations.
"""

import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import config

logger = logging.getLogger('Alice.Scheduler')

class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.notification_manager = None

    def set_notification_manager(self, manager):
        """Set the notification manager for sending notifications."""
        self.notification_manager = manager

    # Jira polling removed - now using webhooks for real-time notifications
    # GitHub polling removed - now using webhooks for real-time notifications

    async def send_status_update(self):
        """Send a periodic status update."""
        try:
            await self.notification_manager.send_status_notification(
                "🤖 Alice integrations are running smoothly!\n"
                "Monitoring Jira tasks and GitHub repositories for updates."
            )
        except Exception as e:
            logger.error(f"Error sending status update: {e}")

    def setup_jobs(self):
        """Setup the scheduled jobs."""
        # All polling removed - now using webhooks for real-time notifications
        logger.info("Jira using webhooks (no polling)")
        logger.info("GitHub using webhooks (no polling)")

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

        # Initial status message disabled to avoid chat spam
        # await self.send_status_update()

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Task scheduler stopped")

# Global instance
task_scheduler = TaskScheduler()