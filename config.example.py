# Alice Discord Bot Configuration - Example Template
# Copy this file to config.py and fill in your actual values

# Bot Token for Atlantis Institute Discord Server
DISCORD_TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"

# Notification Channels Configuration
# Get channel IDs by right-clicking channels in Discord (enable Developer Mode)
NOTIFICATION_CHANNELS = {
    'general': 123456789012345678,  # Replace with actual Discord channel ID for general notifications
    'jira': 123456789012345679,     # Replace with actual Discord channel ID for Jira notifications
    'github': 123456789012345680,   # Replace with actual Discord channel ID for GitHub notifications (PRs, Issues)
    'commits': 123456789012345681,  # Replace with actual Discord channel ID for commit/push notifications
}

# Jira Integration Configuration
JIRA_CONFIG = {
    'server': 'https://your-company.atlassian.net',  # Replace with your Jira server URL
    'username': 'your-email@company.com',  # Replace with your Jira username/email
    'api_token': 'your-jira-api-token',  # Replace with your Jira API token from https://id.atlassian.com/manage-profile/security/api-tokens
    'project_key': 'PROJ',  # Replace with your Jira project key (e.g., 'ATL' for Atlantis project)
    'webhook_secret': 'your-webhook-secret',  # Optional: secret for webhook signature verification
}

# GitHub Integration Configuration
GITHUB_CONFIG = {
    'token': 'your-github-personal-access-token',  # Replace with your GitHub PAT from https://github.com/settings/tokens
    'repos': [
        'YourOrg/YourRepo',  # Replace with your repository (e.g., 'AtlantisInstitute/AtlantisEons')
        # Add more repositories as needed
    ],
    'webhook_secret': 'your-github-webhook-secret',  # Optional: secret for webhook signature verification
}

# Webhook Configuration
WEBHOOK_CONFIG = {
    'port': 8080,  # Port for webhook server (make sure this port is accessible)
    'host': '0.0.0.0',  # Host for webhook server (0.0.0.0 for all interfaces)
    'path': '/webhooks',  # Base path for webhooks
}

# Polling Intervals (in seconds)
POLLING_INTERVALS = {
    'jira': 300,  # Check Jira every 5 minutes
    'github': 180,  # Check GitHub every 3 minutes
}