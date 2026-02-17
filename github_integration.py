"""
GitHub Integration Module for Alicebot
Handles monitoring GitHub repositories for PRs and issues.
"""

import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import List, Dict, Optional
from github import Github
from github.GithubException import GithubException
import config

logger = logging.getLogger('Alicebot.GitHub')

# Pacific timezone for California
PACIFIC_TZ = ZoneInfo('America/Los_Angeles')

def format_pacific_time(iso_date: str) -> str:
    """Convert ISO date string to Pacific time formatted string."""
    dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    pacific_dt = dt.astimezone(PACIFIC_TZ)
    return pacific_dt.strftime('%Y-%m-%d %H:%M PT')

class GitHubIntegration:
    def __init__(self):
        self.github = None
        # Use timezone-aware datetime for proper comparison
        # Start from 1 hour ago to catch recent commits on startup
        self.last_check = datetime.now(timezone.utc) - timedelta(hours=1)
        self.known_prs = set()  # Track known PR numbers
        self.known_issues = set()  # Track known issue numbers
        self.known_commits = set()  # Track known commit SHAs

    def connect(self) -> bool:
        """Connect to GitHub using configuration settings."""
        try:
            if not self.github:
                self.github = Github(config.GITHUB_CONFIG['token'])
            # Test connection
            self.github.get_user().login
            logger.info("Successfully connected to GitHub")

            # Seed known_commits with existing commits on first connect
            # This prevents notifying about old commits on startup
            if not self.known_commits:
                self._seed_known_commits()

            return True
        except GithubException as e:
            logger.error(f"Failed to connect to GitHub: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to GitHub: {e}")
            return False

    def _seed_known_commits(self):
        """Seed known_commits with existing commits to avoid spam on startup."""
        try:
            for repo_name in config.GITHUB_CONFIG['repos']:
                try:
                    repo = self.github.get_repo(repo_name)
                    default_branch = repo.default_branch
                    commits = repo.get_commits(sha=default_branch)

                    # Mark the most recent commits as known
                    commit_count = 0
                    for commit in commits:
                        if commit_count >= 50:
                            break
                        self.known_commits.add(commit.sha)
                        commit_count += 1

                    logger.info(f"Seeded {commit_count} existing commits from {repo_name}")

                except GithubException as e:
                    logger.error(f"Error seeding commits from {repo_name}: {e}")
        except Exception as e:
            logger.error(f"Error seeding known commits: {e}")

    def get_recent_prs(self, hours_back: int = 1) -> List[Dict]:
        """Get pull requests created or updated in the last N hours."""
        if not self.github:
            if not self.connect():
                return []

        all_prs = []
        for repo_name in config.GITHUB_CONFIG['repos']:
            try:
                repo = self.github.get_repo(repo_name)
                # Get PRs updated recently
                since = datetime.now(timezone.utc) - timedelta(hours=hours_back)
                prs = repo.get_pulls(state='all', sort='updated', direction='desc')

                for pr in prs:
                    if pr.updated_at > since:
                        all_prs.append({
                            'repo': repo_name,
                            'number': pr.number,
                            'title': pr.title,
                            'state': pr.state,
                            'author': pr.user.login,
                            'created_at': pr.created_at.isoformat(),
                            'updated_at': pr.updated_at.isoformat(),
                            'merged': pr.merged,
                            'url': pr.html_url,
                            'body': pr.body[:200] + '...' if pr.body and len(pr.body) > 200 else pr.body or '',
                        })

            except GithubException as e:
                logger.error(f"Error fetching PRs from {repo_name}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error fetching PRs from {repo_name}: {e}")

        logger.info(f"Retrieved {len(all_prs)} recent GitHub PRs")
        return all_prs

    def get_recent_issues(self, hours_back: int = 1) -> List[Dict]:
        """Get issues created or updated in the last N hours."""
        if not self.github:
            if not self.connect():
                return []

        all_issues = []
        for repo_name in config.GITHUB_CONFIG['repos']:
            try:
                repo = self.github.get_repo(repo_name)
                # Get issues updated recently (excluding PRs)
                since = datetime.now(timezone.utc) - timedelta(hours=hours_back)
                issues = repo.get_issues(state='all', sort='updated', direction='desc', since=since)

                for issue in issues:
                    # Skip if it's a PR
                    if issue.pull_request:
                        continue

                    all_issues.append({
                        'repo': repo_name,
                        'number': issue.number,
                        'title': issue.title,
                        'state': issue.state,
                        'author': issue.user.login,
                        'created_at': issue.created_at.isoformat(),
                        'updated_at': issue.updated_at.isoformat(),
                        'labels': [label.name for label in issue.labels],
                        'url': issue.html_url,
                        'body': issue.body[:200] + '...' if issue.body and len(issue.body) > 200 else issue.body or '',
                    })

            except GithubException as e:
                logger.error(f"Error fetching issues from {repo_name}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error fetching issues from {repo_name}: {e}")

        logger.info(f"Retrieved {len(all_issues)} recent GitHub issues")
        return all_issues

    def get_new_prs(self) -> List[Dict]:
        """Get PRs that were created since the last check."""
        current_time = datetime.now(timezone.utc)
        hours_back = max(1, int((current_time - self.last_check).total_seconds() / 3600) + 1)

        recent_prs = self.get_recent_prs(hours_back)
        new_prs = []

        for pr in recent_prs:
            pr_created = datetime.fromisoformat(pr['created_at'])

            if pr_created > self.last_check and pr['number'] not in self.known_prs:
                new_prs.append(pr)
                self.known_prs.add(pr['number'])

        logger.info(f"Found {len(new_prs)} new GitHub PRs")
        return new_prs

    def get_new_issues(self) -> List[Dict]:
        """Get issues that were created since the last check."""
        current_time = datetime.now(timezone.utc)
        hours_back = max(1, int((current_time - self.last_check).total_seconds() / 3600) + 1)

        recent_issues = self.get_recent_issues(hours_back)
        new_issues = []

        for issue in recent_issues:
            issue_created = datetime.fromisoformat(issue['created_at'])

            if issue_created > self.last_check and issue['number'] not in self.known_issues:
                new_issues.append(issue)
                self.known_issues.add(issue['number'])

        logger.info(f"Found {len(new_issues)} new GitHub issues")
        return new_issues

    def get_new_commits(self) -> List[Dict]:
        """Get commits that were pushed since the last check."""
        if not self.github:
            if not self.connect():
                return []

        new_commits = []
        for repo_name in config.GITHUB_CONFIG['repos']:
            try:
                repo = self.github.get_repo(repo_name)
                # Get the default branch to check for commits
                default_branch = repo.default_branch

                # Fetch recent commits WITHOUT date filtering
                # The 'since' parameter filters by commit DATE, not push date,
                # which misses commits that were authored earlier but pushed later.
                # Instead, we fetch recent commits and rely on known_commits set
                # to track what we've already seen.
                commits = repo.get_commits(sha=default_branch)

                # Only check the most recent commits (limit to avoid processing too many)
                commit_count = 0
                max_commits_to_check = 50  # Check last 50 commits max

                for commit in commits:
                    if commit_count >= max_commits_to_check:
                        break
                    commit_count += 1

                    commit_sha = commit.sha
                    if commit_sha not in self.known_commits:
                        # Get commit details
                        commit_data = {
                            'repo': repo_name,
                            'sha': commit_sha[:7],  # Short SHA
                            'full_sha': commit_sha,
                            'message': commit.commit.message.split('\n')[0][:100],  # First line, truncated
                            'author': commit.commit.author.name,
                            'author_username': commit.author.login if commit.author else 'Unknown',
                            'date': commit.commit.author.date.isoformat(),
                            'url': commit.html_url,
                            'branch': default_branch,
                        }

                        new_commits.append(commit_data)
                        self.known_commits.add(commit_sha)

            except GithubException as e:
                logger.error(f"Error fetching commits from {repo_name}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error fetching commits from {repo_name}: {e}")

        # Sort commits by date (oldest first) so they're posted in chronological order
        new_commits.sort(key=lambda c: c['date'])

        logger.info(f"Found {len(new_commits)} new GitHub commits")
        return new_commits

    def get_closed_prs(self) -> List[Dict]:
        """Get PRs that were closed/merged since the last check."""
        if not self.github:
            if not self.connect():
                return []

        closed_prs = []
        for repo_name in config.GITHUB_CONFIG['repos']:
            try:
                repo = self.github.get_repo(repo_name)
                # Get recently closed PRs
                prs = repo.get_pulls(state='closed', sort='updated', direction='desc')

                for pr in prs:
                    if pr.closed_at and pr.closed_at > self.last_check:
                        closed_prs.append({
                            'repo': repo_name,
                            'number': pr.number,
                            'title': pr.title,
                            'author': pr.user.login,
                            'closed_at': pr.closed_at.isoformat(),
                            'merged': pr.merged,
                            'url': pr.html_url,
                        })

            except GithubException as e:
                logger.error(f"Error fetching closed PRs from {repo_name}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error fetching closed PRs from {repo_name}: {e}")

        logger.info(f"Found {len(closed_prs)} closed GitHub PRs")
        return closed_prs

    def get_closed_issues(self) -> List[Dict]:
        """Get issues that were closed since the last check."""
        if not self.github:
            if not self.connect():
                return []

        closed_issues = []
        for repo_name in config.GITHUB_CONFIG['repos']:
            try:
                repo = self.github.get_repo(repo_name)
                # Get recently closed issues
                issues = repo.get_issues(state='closed', sort='updated', direction='desc')

                for issue in issues:
                    # Skip if it's a PR
                    if issue.pull_request:
                        continue

                    if issue.closed_at and issue.closed_at > self.last_check:
                        closed_issues.append({
                            'repo': repo_name,
                            'number': issue.number,
                            'title': issue.title,
                            'author': issue.user.login,
                            'closed_at': issue.closed_at.isoformat(),
                            'url': issue.html_url,
                        })

            except GithubException as e:
                logger.error(f"Error fetching closed issues from {repo_name}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error fetching closed issues from {repo_name}: {e}")

        logger.info(f"Found {len(closed_issues)} closed GitHub issues")
        return closed_issues

    def update_last_check(self):
        """Update the last check timestamp."""
        self.last_check = datetime.now(timezone.utc)

    def format_pr_notification(self, pr: Dict, event_type: str) -> str:
        """Format a Discord notification message for a GitHub PR."""
        repo_name = pr['repo'].split('/')[-1]  # Get repo name without org

        if event_type == 'new':
            return f"""🔄 **New Pull Request in {repo_name}**

**#{pr['number']}:** {pr['title']}
**Author:** {pr['author']}
**Created:** {format_pacific_time(pr['created_at'])}
**URL:** {pr['url']}"""

        elif event_type in ['closed', 'merged']:
            status = "✅ **Merged**" if pr.get('merged') else "❌ **Closed**"
            return f"""{status} **Pull Request {event_type.capitalize()} in {repo_name}**

**#{pr['number']}:** {pr['title']}
**Author:** {pr['author']}
**{event_type.capitalize()}:** {format_pacific_time(pr['closed_at'])}
**URL:** {pr['url']}"""

        return f"Unknown PR event type: {event_type}"

    def format_issue_notification(self, issue: Dict, event_type: str) -> str:
        """Format a Discord notification message for a GitHub issue."""
        repo_name = issue['repo'].split('/')[-1]  # Get repo name without org

        if event_type == 'new':
            labels = f" ({', '.join(issue['labels'])})" if issue['labels'] else ""
            return f"""🐛 **New Issue in {repo_name}**

**#{issue['number']}:** {issue['title']}{labels}
**Author:** {issue['author']}
**Created:** {format_pacific_time(issue['created_at'])}
**URL:** {issue['url']}"""

        elif event_type == 'closed':
            return f"""✅ **Issue Closed in {repo_name}**

**#{issue['number']}:** {issue['title']}
**Author:** {issue['author']}
**Closed:** {format_pacific_time(issue['closed_at'])}
**URL:** {issue['url']}"""

        return f"Unknown issue event type: {event_type}"

    def format_commit_notification(self, commit: Dict) -> str:
        """Format a Discord notification message for a GitHub commit."""
        repo_name = commit['repo'].split('/')[-1]  # Get repo name without org

        return f"""**I am Alicebot! Flowers bloom!**

📝 **New Commit to {repo_name}**

**{commit['sha']}:** {commit['message']}
**Author:** {commit['author']} (@{commit['author_username']})
**Date:** {format_pacific_time(commit['date'])}
**URL:** {commit['url']}"""

# Global instance
github_integration = GitHubIntegration()