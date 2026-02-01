"""
Webhook Handler for Alice Bot
Handles incoming webhooks from GitHub, Jira, and Confluence for real-time notifications.
"""

import logging
import hmac
import hashlib
from flask import Flask, request, jsonify
import json
import asyncio
import threading
from typing import Optional
import config

logger = logging.getLogger('Alice.Webhooks')

class WebhookHandler:
    def __init__(self):
        self.app = Flask(__name__)
        self.notification_manager = None
        self.loop = None

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes for webhooks."""

        @self.app.route(f"{config.WEBHOOK_CONFIG['path']}/github", methods=['POST'])
        def github_webhook():
            return self._handle_github_webhook()

        @self.app.route(f"{config.WEBHOOK_CONFIG['path']}/jira", methods=['POST'])
        def jira_webhook():
            return self._handle_jira_webhook()

        @self.app.route(f"{config.WEBHOOK_CONFIG['path']}/confluence", methods=['POST'])
        def confluence_webhook():
            return self._handle_confluence_webhook()

        @self.app.route(f"{config.WEBHOOK_CONFIG['path']}/health", methods=['GET'])
        def health_check():
            return jsonify({"status": "healthy", "service": "alice-webhooks"})

    def _verify_github_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature."""
        if not config.GITHUB_CONFIG.get('webhook_secret'):
            logger.warning("GitHub webhook secret not configured, skipping signature verification")
            return True

        secret = config.GITHUB_CONFIG['webhook_secret'].encode('utf-8')
        expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        expected_signature = f"sha256={expected_signature}"

        return hmac.compare_digest(expected_signature, signature)

    def _verify_jira_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Jira webhook signature."""
        if not config.JIRA_CONFIG.get('webhook_secret'):
            logger.warning("Jira webhook secret not configured, skipping signature verification")
            return True

        secret = config.JIRA_CONFIG['webhook_secret'].encode('utf-8')
        expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()

        return hmac.compare_digest(expected_signature, signature)

    def _handle_github_webhook(self):
        """Handle incoming GitHub webhook."""
        try:
            payload = request.get_data()
            signature = request.headers.get('X-Hub-Signature-256')

            # Verify signature if configured
            if not self._verify_github_signature(payload, signature):
                logger.warning("Invalid GitHub webhook signature")
                return jsonify({"error": "Invalid signature"}), 401

            event_type = request.headers.get('X-GitHub-Event')
            data = json.loads(payload.decode('utf-8'))

            logger.info(f"Received GitHub webhook: {event_type}")

            # Run async handling in the event loop (thread-safe)
            if self.loop and self.notification_manager:
                asyncio.run_coroutine_threadsafe(self._process_github_event(event_type, data), self.loop)
            else:
                logger.error(f"Cannot process webhook - loop: {self.loop is not None}, notification_manager: {self.notification_manager is not None}")

            return jsonify({"status": "processed"}), 200

        except Exception as e:
            logger.error(f"Error processing GitHub webhook: {e}")
            return jsonify({"error": "Internal server error"}), 500

    def _handle_jira_webhook(self):
        """Handle incoming Jira webhook."""
        try:
            payload = request.get_data()
            signature = request.headers.get('X-Jira-Signature')

            # Verify signature if configured
            if not self._verify_jira_signature(payload, signature):
                logger.warning("Invalid Jira webhook signature")
                return jsonify({"error": "Invalid signature"}), 401

            data = json.loads(payload.decode('utf-8'))

            logger.info("Received Jira webhook")

            # Run async handling in the event loop (thread-safe)
            if self.loop and self.notification_manager:
                asyncio.run_coroutine_threadsafe(self._process_jira_event(data), self.loop)

            return jsonify({"status": "processed"}), 200

        except Exception as e:
            logger.error(f"Error processing Jira webhook: {e}")
            return jsonify({"error": "Internal server error"}), 500

    def _handle_confluence_webhook(self):
        """Handle incoming Confluence webhook."""
        try:
            payload = request.get_data()
            data = json.loads(payload.decode('utf-8'))

            logger.info("Received Confluence webhook")

            # Run async handling in the event loop (thread-safe)
            if self.loop and self.notification_manager:
                asyncio.run_coroutine_threadsafe(self._process_confluence_event(data), self.loop)

            return jsonify({"status": "processed"}), 200

        except Exception as e:
            logger.error(f"Error processing Confluence webhook: {e}")
            return jsonify({"error": "Internal server error"}), 500

    async def _process_github_event(self, event_type: str, data: dict):
        """Process GitHub webhook event asynchronously."""
        try:
            if event_type == 'pull_request':
                await self._handle_github_pr_event(data)
            elif event_type == 'issues':
                await self._handle_github_issue_event(data)
            elif event_type == 'push':
                await self._handle_github_push_event(data)
            elif event_type == 'ping':
                logger.info("Received GitHub webhook ping")
            else:
                logger.debug(f"Ignored GitHub event type: {event_type}")

        except Exception as e:
            logger.error(f"Error processing GitHub event: {e}")

    async def _handle_github_pr_event(self, data: dict):
        """Handle GitHub pull request events."""
        pr = data.get('pull_request', {})
        action = data.get('action')

        if action == 'opened':
            pr_data = {
                'repo': data['repository']['full_name'],
                'number': pr['number'],
                'title': pr['title'],
                'author': pr['user']['login'],
                'created_at': pr['created_at'],
                'url': pr['html_url'],
            }
            await self.notification_manager.notify_github_new_pr(pr_data)

        elif action in ['closed', 'reopened']:
            pr_data = {
                'repo': data['repository']['full_name'],
                'number': pr['number'],
                'title': pr['title'],
                'author': pr['user']['login'],
                'closed_at': pr['closed_at'],
                'merged': pr.get('merged', False),
                'url': pr['html_url'],
            }
            if action == 'closed':
                await self.notification_manager.notify_github_pr_closed(pr_data)

    async def _handle_github_issue_event(self, data: dict):
        """Handle GitHub issue events."""
        issue = data.get('issue', {})
        action = data.get('action')

        if action == 'opened':
            issue_data = {
                'repo': data['repository']['full_name'],
                'number': issue['number'],
                'title': issue['title'],
                'author': issue['user']['login'],
                'created_at': issue['created_at'],
                'labels': [label['name'] for label in issue.get('labels', [])],
                'url': issue['html_url'],
            }
            await self.notification_manager.notify_github_new_issue(issue_data)

        elif action == 'closed':
            issue_data = {
                'repo': data['repository']['full_name'],
                'number': issue['number'],
                'title': issue['title'],
                'author': issue['user']['login'],
                'closed_at': issue['closed_at'],
                'url': issue['html_url'],
            }
            await self.notification_manager.notify_github_issue_closed(issue_data)

    async def _handle_github_push_event(self, data: dict):
        """Handle GitHub push events."""
        from github_integration import github_integration

        commits = data.get('commits', [])
        ref = data.get('ref', '')
        repo_full_name = data.get('repository', {}).get('full_name', '')

        logger.info(f"Processing push event: {len(commits)} commit(s) to {ref} in {repo_full_name}")

        # Only process commits to main/master branches
        if not ref.endswith('/main') and not ref.endswith('/master'):
            logger.info(f"Ignoring push to non-main branch: {ref}")
            return

        # Process each commit in the push (commits are already in chronological order from GitHub)
        for commit in commits:
            # Skip if we've already seen this commit (from polling)
            if commit['id'] in github_integration.known_commits:
                logger.info(f"Skipping already known commit: {commit['id'][:7]}")
                continue

            # Mark as known to prevent duplicate from polling
            github_integration.known_commits.add(commit['id'])

            commit_data = {
                'repo': repo_full_name,
                'sha': commit['id'][:7],  # Short SHA
                'full_sha': commit['id'],
                'message': commit['message'].split('\n')[0][:100],  # First line, truncated
                'author': commit['author']['name'],
                'author_username': commit['author'].get('username', commit['author']['name']),
                'date': commit['timestamp'],
                'url': commit['url'],
                'branch': ref.split('/')[-1],
            }
            logger.info(f"Sending commit notification: {commit_data['sha']} - {commit_data['message'][:50]}")
            await self.notification_manager.notify_github_new_commit(commit_data)
            await asyncio.sleep(1)  # Small delay between commit notifications

    async def _process_jira_event(self, data: dict):
        """Process Jira webhook event asynchronously."""
        try:
            webhook_event = data.get('webhookEvent')

            if webhook_event == 'jira:issue_created':
                await self._handle_jira_issue_created(data)
            elif webhook_event == 'jira:issue_updated':
                await self._handle_jira_issue_updated(data)
            else:
                logger.debug(f"Ignored Jira webhook event: {webhook_event}")

        except Exception as e:
            logger.error(f"Error processing Jira event: {e}")

    async def _handle_jira_issue_created(self, data: dict):
        """Handle Jira issue created event."""
        from jira_integration import jira_integration

        issue = data.get('issue', {})
        issue_key = issue.get('key')

        # Skip if we've already seen this issue
        if issue_key in jira_integration.known_issues:
            logger.debug(f"Skipping already known Jira issue: {issue_key}")
            return

        # Mark as known to prevent duplicates
        jira_integration.known_issues.add(issue_key)

        issue_data = {
            'key': issue_key,
            'summary': issue.get('fields', {}).get('summary'),
            'status': issue.get('fields', {}).get('status', {}).get('name'),
            'assignee': issue.get('fields', {}).get('assignee', {}).get('displayName') if issue.get('fields', {}).get('assignee') else 'Unassigned',
            'created': issue.get('fields', {}).get('created'),
            'creator': issue.get('fields', {}).get('creator', {}).get('displayName'),
            'priority': issue.get('fields', {}).get('priority', {}).get('name') if issue.get('fields', {}).get('priority') else 'Not set',
            'type': issue.get('fields', {}).get('issuetype', {}).get('name'),
            'url': f"{config.JIRA_CONFIG['server']}/browse/{issue_key}"
        }

        await self.notification_manager.notify_jira_new_task(issue_data)

    async def _handle_jira_issue_updated(self, data: dict):
        """Handle Jira issue updated event."""
        issue = data.get('issue', {})
        changelog = data.get('changelog', {})

        # Check if status changed to done
        for item in changelog.get('items', []):
            if item.get('field') == 'status' and item.get('toString') in ['Done', 'Closed', 'Resolved']:
                issue_data = {
                    'key': issue.get('key'),
                    'summary': issue.get('fields', {}).get('summary'),
                    'status': item.get('toString'),
                    'assignee': issue.get('fields', {}).get('assignee', {}).get('displayName') if issue.get('fields', {}).get('assignee') else 'Unassigned',
                    'completed_at': data.get('timestamp'),
                    'url': f"{config.JIRA_CONFIG['server']}/browse/{issue.get('key')}"
                }

                await self.notification_manager.notify_jira_task_completed(issue_data)
                break

    async def _process_confluence_event(self, data: dict):
        """Process Confluence webhook event asynchronously."""
        try:
            event_type = data.get('eventType', '')

            if event_type == 'page_created':
                await self._handle_confluence_page_created(data)
            elif event_type == 'page_updated':
                await self._handle_confluence_page_updated(data)
            elif event_type == 'comment_created':
                await self._handle_confluence_comment_created(data)
            else:
                logger.debug(f"Ignored Confluence event type: {event_type}")

        except Exception as e:
            logger.error(f"Error processing Confluence event: {e}")

    async def _handle_confluence_page_created(self, data: dict):
        """Handle Confluence page created event."""
        page = data.get('page', {})

        page_data = {
            'title': page.get('title'),
            'space': page.get('spaceKey', 'Unknown'),
            'creator': data.get('userAccountId', 'Unknown'),
            'url': f"{config.CONFLUENCE_CONFIG['server']}/pages/viewpage.action?pageId={page.get('id')}"
        }

        await self.notification_manager.notify_confluence_page_created(page_data)

    async def _handle_confluence_page_updated(self, data: dict):
        """Handle Confluence page updated event."""
        page = data.get('page', {})

        page_data = {
            'title': page.get('title'),
            'space': page.get('spaceKey', 'Unknown'),
            'editor': data.get('userAccountId', 'Unknown'),
            'url': f"{config.CONFLUENCE_CONFIG['server']}/pages/viewpage.action?pageId={page.get('id')}"
        }

        await self.notification_manager.notify_confluence_page_updated(page_data)

    async def _handle_confluence_comment_created(self, data: dict):
        """Handle Confluence comment created event."""
        comment = data.get('comment', {})
        page = data.get('page', {})

        comment_data = {
            'page_title': page.get('title'),
            'space': page.get('spaceKey', 'Unknown'),
            'commenter': data.get('userAccountId', 'Unknown'),
            'url': f"{config.CONFLUENCE_CONFIG['server']}/pages/viewpage.action?pageId={page.get('id')}"
        }

        await self.notification_manager.notify_confluence_comment_created(comment_data)

    def set_notification_manager(self, manager):
        """Set the notification manager for sending Discord messages."""
        self.notification_manager = manager

    def set_event_loop(self, loop):
        """Set the asyncio event loop for async operations."""
        self.loop = loop

    def run(self, host: str = None, port: int = None):
        """Run the Flask webhook server."""
        host = host or config.WEBHOOK_CONFIG['host']
        port = port or config.WEBHOOK_CONFIG['port']

        logger.info(f"Starting webhook server on {host}:{port}")
        self.app.run(host=host, port=port, debug=False, use_reloader=False)

# Global instance
webhook_handler = WebhookHandler()