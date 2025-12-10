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

    async def check_jira_updates(self):
        """Check for new Jira tasks and completed tasks."""
        try:
            from jira_integration import jira_integration

            logger.info("Checking for Jira updates...")

            # Check for new tasks
            new_tasks = jira_integration.get_new_issues()
            for task in new_tasks:
                await self.notification_manager.notify_jira_new_task(task)

            # Check for completed tasks
            completed_tasks = jira_integration.get_completed_issues()
            for task in completed_tasks:
                await self.notification_manager.notify_jira_task_completed(task)

            if new_tasks or completed_tasks:
                logger.info(f"Jira updates: {len(new_tasks)} new, {len(completed_tasks)} completed")
            else:
                logger.debug("No new Jira updates found")

        except Exception as e:
            logger.error(f"Error checking Jira updates: {e}")
            await self.notification_manager.send_error_notification(
                f"Failed to check Jira updates: {str(e)}"
            )

    async def check_github_updates(self):
        """Check for new GitHub PRs and issues."""
        try:
            from github_integration import github_integration

            logger.info("Checking for GitHub updates...")

            # Check for new PRs
            new_prs = github_integration.get_new_prs()
            for pr in new_prs:
                await self.notification_manager.notify_github_new_pr(pr)

            # Check for closed PRs
            closed_prs = github_integration.get_closed_prs()
            for pr in closed_prs:
                await self.notification_manager.notify_github_pr_closed(pr)

            # Check for new issues
            new_issues = github_integration.get_new_issues()
            for issue in new_issues:
                await self.notification_manager.notify_github_new_issue(issue)

            # Check for closed issues
            closed_issues = github_integration.get_closed_issues()
            for issue in closed_issues:
                await self.notification_manager.notify_github_issue_closed(issue)

            # Check for new commits
            new_commits = github_integration.get_new_commits()
            for commit in new_commits:
                await self.notification_manager.notify_github_new_commit(commit)

            # Update last check time
            github_integration.update_last_check()

            total_updates = len(new_prs) + len(closed_prs) + len(new_issues) + len(closed_issues) + len(new_commits)
            if total_updates > 0:
                logger.info(f"GitHub updates: {len(new_prs)} new PRs, {len(closed_prs)} closed PRs, "
                          f"{len(new_issues)} new issues, {len(closed_issues)} closed issues, "
                          f"{len(new_commits)} new commits")
            else:
                logger.debug("No new GitHub updates found")

        except Exception as e:
            logger.error(f"Error checking GitHub updates: {e}")
            await self.notification_manager.send_error_notification(
                f"Failed to check GitHub updates: {str(e)}"
            )

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
        # Jira polling job
        jira_interval = config.POLLING_INTERVALS.get('jira', 300)  # Default 5 minutes
        self.scheduler.add_job(
            self.check_jira_updates,
            trigger=IntervalTrigger(seconds=jira_interval),
            id='jira_polling',
            name='Jira Updates Check',
            max_instances=1
        )
        logger.info(f"Scheduled Jira polling every {jira_interval} seconds")

        # GitHub polling job
        github_interval = config.POLLING_INTERVALS.get('github', 180)  # Default 3 minutes
        self.scheduler.add_job(
            self.check_github_updates,
            trigger=IntervalTrigger(seconds=github_interval),
            id='github_polling',
            name='GitHub Updates Check',
            max_instances=1
        )
        logger.info(f"Scheduled GitHub polling every {github_interval} seconds")

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