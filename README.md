# Alice 🤖

**Alice** is the official Discord bot for Atlantis Institute, designed to help manage and enhance the Discord server experience.

## Features

- **Basic Commands**: Hello and ping commands to test functionality
- **Extensible Architecture**: Built with discord.py for easy addition of new features
- **Logging**: Comprehensive logging for monitoring and debugging
- **Secure Configuration**: Token stored securely in configuration file

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

3. **Configure the bot**:
   - Open `config.py`
   - Replace the `DISCORD_TOKEN` with your bot's token
   - **Security Note**: Never commit `config.py` to version control

4. **Invite the bot to your server**:
   - Go to the Discord Developer Portal
   - Select your application
   - Go to the "OAuth2" section
   - Under "Scopes", check "bot"
   - Under "Bot Permissions", select the permissions your bot needs
   - Copy the generated URL and use it to invite the bot to your server

## Usage

### Running the Bot

```bash
python alice.py
```

The bot will log in and display status information when ready.

### Available Commands

- `!hello` - Alice introduces herself
- `!ping` - Check bot latency

### Adding New Features

Alice is built with a modular architecture using discord.py's commands extension. To add new commands:

1. Add new command functions in `alice.py` using the `@bot.command()` decorator
2. For complex features, consider creating separate cog files for organization

## Project Structure

```
Alice/
├── alice.py          # Main bot file
├── config.py         # Configuration (contains bot token)
├── requirements.txt  # Python dependencies
├── .gitignore        # Git ignore rules
└── README.md         # This file
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
