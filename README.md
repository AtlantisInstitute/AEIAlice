# Alice 🤖

**Alice Synthesis 30** is the official AI Discord bot for Atlantis Institute, designed to manage the Discord server and provide automated integrations with development tools.

## Features

### 🤖 Core Functionality
- **Basic Commands**: Hello and ping commands to test functionality
- **Extensible Architecture**: Built with discord.py for easy addition of new features
- **Logging**: Comprehensive logging for monitoring and debugging
- **Secure Configuration**: Token stored securely in configuration file

### 🔗 Tool Integrations & Notifications Hub
- **Jira Integration**: Monitors project tasks for new issues and completions
- **GitHub Integration**: Tracks pull requests and issues across repositories
- **Real-time Webhooks**: Instant notifications via webhook endpoints
- **Automated Polling**: Background checks for updates at configurable intervals
- **Discord Notifications**: Channel-specific alerts for different types of updates

## Setup

### Prerequisites

- Python 3.8 or higher
- A Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications)

### Installation

1. **Clone or download** this repository to your local machine

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure integrations** (see Integration Setup section below)

3. **Configure the bot**:
   - Copy `config.example.py` to `config.py`
   - Fill in your actual API tokens, channel IDs, and configuration values
   - **Security Note**: Never commit `config.py` to version control

4. **Invite the bot to your server**:
   - Go to the Discord Developer Portal
   - Select your application
   - Go to the "OAuth2" section
   - Under "Scopes", check "bot"
   - Under "Bot Permissions", select the permissions your bot needs
   - Copy the generated URL and use it to invite the bot to your server

## Usage

### 🚀 Quick Start

```bash
python alice.py
```

The bot will:
1. **Connect to Discord** and join Atlantis E. Institute server
2. **Start webhook server** on port 8080 for real-time notifications
3. **Begin polling Jira** every 5 minutes for new/completed tasks
4. **Send notifications** to #general channel for all updates

### Available Commands

- `!hello` - Alice introduces herself
- `!ping` - Check bot latency
- `!integrations` - Check status of all integrations
- `!check` - Manually trigger integration checks (admin only)
- `!webhook` - Get webhook endpoint URLs for configuration (admin only)

### Integration Setup

#### ✅ Current Configuration Status

| Integration | Status | Details |
|-------------|--------|---------|
| **Discord** | ✅ Ready | Atlantis E. Institute server (#general channel) |
| **Jira** | ✅ Connected | AEI project monitoring (new/completed tasks) |
| **GitHub** | ✅ Connected | Atlantisinstitute/AtlantisEons repo (PRs/issues monitoring) |
| **Webhooks** | ✅ Ready | Port 8080 for real-time notifications |

#### ✅ Discord Channel Configuration (COMPLETED)
- **Server**: Atlantis E. Institute
- **Channel**: #general (ID: 1008953754273460225)
- **Status**: ✅ Configured for all notification types

#### GitHub Configuration (Optional)

1. **Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token with `repo` permissions
   - Update `config.py`:

```python
GITHUB_CONFIG = {
    'token': 'your-github-token-here',
    'repos': ['AtlantisInstitute/your-repo-name'],
}
```

2. **Webhook Setup** (Optional):
   - Repository Settings → Webhooks
   - Payload URL: `http://your-server:8080/webhooks/github`
   - Content type: `application/json`
   - Events: Pull requests, Issues

#### GitHub Configuration

1. **Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate a token with `repo` permissions
   - Update `config.py` with your token and repository list

2. **Webhook Setup** (Optional - for real-time notifications):
   - Go to your repository Settings → Webhooks
   - Add webhook with URL: `http://your-server:8080/webhooks/github`
   - Content type: `application/json`
   - Events: Pull requests, Issues
   - Set secret if configured in `config.py`

#### Discord Channel Setup

Update the channel IDs in `config.py` for notifications:
- `general`: General announcements
- `jira`: Jira-specific notifications
- `github`: GitHub-specific notifications

### Available Commands

- `!hello` - Alice introduces herself
- `!ping` - Check bot latency
- `!integrations` - Check status of all integrations
- `!check` - Manually trigger integration checks (admin only)
- `!webhook` - Get webhook endpoint URLs for configuration (admin only)

### Adding New Features

Alice is built with a modular architecture using discord.py's commands extension. To add new commands:

1. Add new command functions in `alice.py` using the `@bot.command()` decorator
2. For complex features, consider creating separate cog files for organization

## Project Structure

```
Alice/
├── alice.py              # Main bot file with Discord integration
├── config.py             # Configuration (API tokens, channels, etc.)
├── requirements.txt      # Python dependencies
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── jira_integration.py   # Jira API integration and monitoring
├── github_integration.py # GitHub API integration and monitoring
├── notification_manager.py # Discord notification system
├── webhook_handler.py    # Webhook server for real-time updates
└── task_scheduler.py     # Background polling scheduler
```

## Security

- The bot token is stored in `config.py` which is excluded from version control
- Never share your bot token publicly
- Regularly rotate bot tokens for security

## Development

Alice is built with discord.py, a modern, easy-to-use, feature-rich, and async-ready API wrapper for Discord.

### Adding Commands

```python
@bot.command(name='newcommand', help='Description of command')
async def newcommand(ctx):
    # Your command logic here
    await ctx.send('Command response')
```

### Adding Event Handlers

```python
@bot.event
async def on_event_name():
    # Event handling logic here
    pass
```

## Support

For questions or issues with Alice, please contact the Atlantis Institute development team.

## License

This project is proprietary to Atlantis Institute.
