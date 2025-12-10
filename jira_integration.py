"""
Jira Integration Module for Alice Bot
Handles monitoring Jira projects for new and completed tasks.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from jira import JIRA
from jira.exceptions import JIRAError
import config

logger = logging.getLogger('Alice.Jira')

class JiraIntegration:
    def __init__(self):
        self.jira = None
        # Use timezone-aware datetime for proper comparison with Jira timestamps
        # Start from current time to avoid duplicate notifications on restart
        self.last_check = datetime.now(timezone.utc)
        self.known_issues = set()  # Track known issue keys to detect new ones

    def connect(self) -> bool:
        """Connect to Jira using configuration settings."""
        try:
            if not self.jira:
                self.jira = JIRA(
                    server=config.JIRA_CONFIG['server'],
                    basic_auth=(config.JIRA_CONFIG['username'], config.JIRA_CONFIG['api_token'])
                )
            # Test connection
            self.jira.myself()
            logger.info("Successfully connected to Jira")
            return True
        except JIRAError as e:
            logger.error(f"Failed to connect to Jira: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Jira: {e}")
            return False

    def get_recent_issues(self, hours_back: int = 1) -> List[Dict]:
        """Get issues created or updated in the last N hours."""
        if not self.jira:
            if not self.connect():
                return []

        try:
            # JQL query to find issues created or updated recently in the project
            jql = f'project = "{config.JIRA_CONFIG["project_key"]}" AND (created > -{hours_back}h OR updated > -{hours_back}h) ORDER BY updated DESC'

            issues = self.jira.search_issues(jql, maxResults=50)

            issue_data = []
            for issue in issues:
                issue_data.append({
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'status': issue.fields.status.name,
                    'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                    'created': issue.fields.created,
                    'updated': issue.fields.updated,
                    'creator': issue.fields.creator.displayName,
                    'priority': issue.fields.priority.name if issue.fields.priority else 'Not set',
                    'type': issue.fields.issuetype.name,
                    'url': f"{config.JIRA_CONFIG['server']}/browse/{issue.key}"
                })

            logger.info(f"Retrieved {len(issue_data)} recent Jira issues")
            return issue_data

        except JIRAError as e:
            logger.error(f"Error querying Jira: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error querying Jira: {e}")
            return []

    def get_new_issues(self) -> List[Dict]:
        """Get issues that were created since the last check."""
        current_time = datetime.now(timezone.utc)
        hours_back = max(1, int((current_time - self.last_check).total_seconds() / 3600) + 1)

        recent_issues = self.get_recent_issues(hours_back)
        new_issues = []

        for issue in recent_issues:
            issue_created = datetime.fromisoformat(issue['created'].replace('Z', '+00:00'))

            if issue_created > self.last_check and issue['key'] not in self.known_issues:
                new_issues.append(issue)
                self.known_issues.add(issue['key'])

        self.last_check = current_time
        logger.info(f"Found {len(new_issues)} new Jira issues")
        return new_issues

    def get_completed_issues(self) -> List[Dict]:
        """Get issues that were completed since the last check."""
        if not self.jira:
            if not self.connect():
                return []

        try:
            # JQL query to find issues that transitioned to done status recently
            jql = f'project = "{config.JIRA_CONFIG["project_key"]}" AND status CHANGED TO ("Done", "Closed", "Resolved") AFTER "{self.last_check.strftime("%Y-%m-%d %H:%M")}"'

            issues = self.jira.search_issues(jql, maxResults=50)

            completed_issues = []
            for issue in issues:
                # Get the changelog to find when it was completed
                changelog = self.jira.issue(issue.key, expand='changelog')
                completion_time = None

                for history in changelog.changelog.histories:
                    for item in history.items:
                        if item.field == 'status' and item.toString in ['Done', 'Closed', 'Resolved']:
                            completion_time = datetime.fromisoformat(history.created.replace('Z', '+00:00'))
                            break
                    if completion_time:
                        break

                if completion_time and completion_time > self.last_check:
                    completed_issues.append({
                        'key': issue.key,
                        'summary': issue.fields.summary,
                        'status': issue.fields.status.name,
                        'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                        'completed_at': completion_time.isoformat(),
                        'url': f"{config.JIRA_CONFIG['server']}/browse/{issue.key}"
                    })

            logger.info(f"Found {len(completed_issues)} completed Jira issues")
            return completed_issues

        except JIRAError as e:
            logger.error(f"Error querying completed issues: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error querying completed issues: {e}")
            return []

    def format_issue_notification(self, issue: Dict, event_type: str) -> str:
        """Format a Discord notification message for a Jira issue."""
        if event_type == 'new':
            return f"""🆕 **New Jira Task Created**

**{issue['key']}:** {issue['summary']}
**Type:** {issue['type']}
**Priority:** {issue['priority']}
**Assignee:** {issue['assignee']}
**Created by:** {issue['creator']}
**URL:** {issue['url']}"""

        elif event_type == 'completed':
            return f"""✅ **Jira Task Completed**

**{issue['key']}:** {issue['summary']}
**Assignee:** {issue['assignee']}
**Completed:** {datetime.fromisoformat(issue['completed_at']).strftime('%Y-%m-%d %H:%M UTC')}
**URL:** {issue['url']}"""

        return f"Unknown event type: {event_type}"

# Global instance
jira_integration = JiraIntegration()