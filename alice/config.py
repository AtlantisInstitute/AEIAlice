"""
Alice Configuration - Environment-based settings.

All secrets and configuration are loaded from environment variables.
Use a .env file in the project root for local development (loaded via python-dotenv).
"""

import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Discord Bot Token (retained for reference; Alice uses webhooks, not the gateway)
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN', '')

# Notification Channels Configuration
NOTIFICATION_CHANNELS = {
    'general': int(os.environ.get('DISCORD_CHANNEL_GENERAL', '0')),
    'jira': int(os.environ.get('DISCORD_CHANNEL_JIRA', '0')),
    'github': int(os.environ.get('DISCORD_CHANNEL_GITHUB', '0')),
    'commits': int(os.environ.get('DISCORD_CHANNEL_COMMITS', '0')),
}

# Jira Integration Configuration
JIRA_CONFIG = {
    'server': os.environ.get('JIRA_SERVER', 'https://your-company.atlassian.net'),
    'username': os.environ.get('JIRA_USERNAME', ''),
    'api_token': os.environ.get('JIRA_API_TOKEN', ''),
    'project_key': os.environ.get('JIRA_PROJECT_KEY', 'AEI'),
    'webhook_secret': os.environ.get('JIRA_WEBHOOK_SECRET', ''),
}

# GitHub Integration Configuration
GITHUB_CONFIG = {
    'token': os.environ.get('GITHUB_TOKEN', ''),
    'repos': [r.strip() for r in os.environ.get('GITHUB_REPOS', '').split(',') if r.strip()],
    'webhook_secret': os.environ.get('GITHUB_WEBHOOK_SECRET', ''),
}

# Confluence Integration Configuration
CONFLUENCE_CONFIG = {
    'server': os.environ.get('CONFLUENCE_SERVER', 'https://your-company.atlassian.net/wiki'),
    'webhook_secret': os.environ.get('CONFLUENCE_WEBHOOK_SECRET', ''),
}

# Webhook Configuration
WEBHOOK_CONFIG = {
    'port': int(os.environ.get('WEBHOOK_PORT', '8080')),
    'host': os.environ.get('WEBHOOK_HOST', '0.0.0.0'),
    'path': os.environ.get('WEBHOOK_PATH', '/webhooks'),
}

# Discord Webhook URLs for posting notifications (no bot gateway needed)
DISCORD_WEBHOOKS = {
    'general': os.environ.get('DISCORD_WEBHOOK_GENERAL', ''),
    'jira': os.environ.get('DISCORD_WEBHOOK_JIRA', ''),
    'github': os.environ.get('DISCORD_WEBHOOK_GITHUB', ''),
    'commits': os.environ.get('DISCORD_WEBHOOK_COMMITS', ''),
}

# GitHub poll interval in seconds
GITHUB_POLL_INTERVAL = int(os.environ.get('GITHUB_POLL_INTERVAL', '60'))

# Polling Intervals (legacy compat - now mostly webhook-driven)
POLLING_INTERVALS = {}
