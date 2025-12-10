#!/usr/bin/env python3
"""
Alice - Discord Bot for Atlantis Institute
A helpful Discord bot to manage the Atlantis Institute server.
"""

import discord
from discord.ext import commands
import config
import logging
import os
import sys
import signal
import psutil
import atexit
import threading
import asyncio

# Import integration modules
from notification_manager import init_notification_manager
from webhook_handler import webhook_handler
from task_scheduler import task_scheduler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Alice')

# PID file location
PID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'alice.pid')

def kill_all_alice_instances():
    """Kill all running Alice bot instances."""
    current_pid = os.getpid()
    killed_count = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and 'alice.py' in ' '.join(cmdline).lower():
                if proc.info['pid'] != current_pid:
                    logger.info(f"Killing old Alice instance (PID: {proc.info['pid']})")
                    proc.kill()
                    killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if killed_count > 0:
        logger.info(f"Killed {killed_count} old Alice instance(s)")
    return killed_count

def check_single_instance():
    """Ensure only one instance of Alice is running."""
    # Kill any existing instances first
    kill_all_alice_instances()
    
    # Create PID file with current process ID
    try:
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
        logger.info(f'PID file created: {PID_FILE}')
    except Exception as e:
        logger.warning(f'Could not create PID file: {e}')

def cleanup_pid_file():
    """Remove the PID file on exit."""
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
            logger.info('PID file removed')
    except Exception as e:
        logger.warning(f'Could not remove PID file: {e}')

def stop_integrations():
    """Stop all integration services."""
    logger.info('Stopping integrations...')

    # Stop task scheduler
    if task_scheduler:
        task_scheduler.stop()

    logger.info('Integrations stopped')

def signal_handler(signum, frame):
    """Handle termination signals gracefully."""
    logger.info(f'Received signal {signum}, shutting down Alice...')

    # Stop task scheduler
    if task_scheduler:
        task_scheduler.stop()

    kill_all_alice_instances()
    cleanup_pid_file()
    sys.exit(0)

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True  # Enable reading message content
intents.members = True  # Enable member-related events
intents.guilds = True  # Enable guild join/leave events

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Global variables for integrations
notification_manager = None
webhook_thread = None

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    global notification_manager, webhook_thread

    logger.info(f'Alice is online! Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'Connected to {len(bot.guilds)} server(s)')

    # Set a custom status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="over Atlantis Institute integrations"
        )
    )

    # Initialize notification manager
    notification_manager = init_notification_manager(bot)

    # Setup webhook handler
    webhook_handler.set_notification_manager(notification_manager)
    webhook_handler.set_event_loop(asyncio.get_event_loop())

    # Start webhook server in background thread
    webhook_thread = threading.Thread(
        target=webhook_handler.run,
        daemon=True,
        name="WebhookServer"
    )
    webhook_thread.start()
    logger.info("Webhook server started")

    # Setup and start task scheduler
    task_scheduler.set_notification_manager(notification_manager)
    await task_scheduler.start()
    logger.info("Task scheduler started")

    # Send startup notification
    await notification_manager.send_general_notification(
        "🚀 Alice is Online",
        "🤖 Alice Synthesis 30 is now monitoring your Jira and GitHub integrations!\n\n"
        "**Active Integrations:**\n"
        "• Jira task monitoring\n"
        "• GitHub PR/issue monitoring\n"
        "• Webhook support for real-time notifications\n\n"
        "**Webhook Endpoints:**\n"
        f"• GitHub: `http://your-server:{config.WEBHOOK_CONFIG['port']}{config.WEBHOOK_CONFIG['path']}/github`\n"
        f"• Jira: `http://your-server:{config.WEBHOOK_CONFIG['port']}{config.WEBHOOK_CONFIG['path']}/jira`",
        discord.Color.green()
    )

@bot.event
async def on_message(message):
    """Called whenever a message is sent in a channel the bot can see."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Process commands
    await bot.process_commands(message)

@bot.event
async def on_guild_join(guild):
    """Called when the bot joins a new guild (server)."""
    logger.info(f'Alice has joined a new guild: {guild.name} (ID: {guild.id})')

    # Find a suitable channel to send the intro message
    # Try system channel first, then general channel, then the first text channel
    channel = None

    if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
        channel = guild.system_channel
    else:
        # Look for a general channel
        for ch in guild.text_channels:
            if ch.name.lower() in ['general', 'main', 'lobby', 'chat'] and ch.permissions_for(guild.me).send_messages:
                channel = ch
                break

        # If no general channel found, use the first text channel the bot can send to
        if not channel:
            for ch in guild.text_channels:
                if ch.permissions_for(guild.me).send_messages:
                    channel = ch
                    break

    if channel:
        intro_message = ("Hello, my name is Alice Synthesis 30 and I am the new AI assitant administrator "
                        "for Atlantis Institute and will update the team on here with all git commits done on Atlantis Eons")
        await channel.send(intro_message)
        logger.info(f'Sent intro message to #{channel.name} in {guild.name}')
    else:
        logger.warning(f'Could not find a suitable channel to send intro message in {guild.name}')

@bot.command(name='hello', help='Say hello to Alice!')
async def hello(ctx):
    """Basic hello command to test the bot."""
    await ctx.send(f'Hello {ctx.author.mention}! I am Alice, your friendly Discord bot for Atlantis Institute! 🤖')

@bot.command(name='ping', help='Check bot latency')
async def ping(ctx):
    """Check the bot's response time."""
    latency = round(bot.latency * 1000)  # Convert to milliseconds
    await ctx.send(f'Pong! Latency: {latency}ms')

@bot.command(name='integrations', help='Check integration status')
async def integrations_status(ctx):
    """Show the status of all integrations."""
    embed = discord.Embed(
        title="🤖 Alice Integration Status",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )

    # Jira status
    try:
        from jira_integration import jira_integration
        jira_connected = jira_integration.connect()
        embed.add_field(
            name="📋 Jira Integration",
            value=f"Status: {'✅ Connected' if jira_connected else '❌ Disconnected'}\n"
                  f"Project: {config.JIRA_CONFIG['project_key']}\n"
                  f"Server: {config.JIRA_CONFIG['server']}",
            inline=False
        )
    except Exception as e:
        embed.add_field(
            name="📋 Jira Integration",
            value=f"Status: ❌ Error\nError: {str(e)}",
            inline=False
        )

    # GitHub status
    try:
        from github_integration import github_integration
        github_connected = github_integration.connect()
        repos = ', '.join([repo.split('/')[-1] for repo in config.GITHUB_CONFIG['repos']])
        embed.add_field(
            name="🐙 GitHub Integration",
            value=f"Status: {'✅ Connected' if github_connected else '❌ Disconnected'}\n"
                  f"Repos: {repos}",
            inline=False
        )
    except Exception as e:
        embed.add_field(
            name="🐙 GitHub Integration",
            value=f"Status: ❌ Error\nError: {str(e)}",
            inline=False
        )

    # Webhook status
    embed.add_field(
        name="🔗 Webhook Server",
        value=f"Status: ✅ Running\n"
              f"Port: {config.WEBHOOK_CONFIG['port']}\n"
              f"Path: {config.WEBHOOK_CONFIG['path']}",
        inline=False
    )

    # Scheduler status
    scheduler_status = "✅ Running" if task_scheduler.scheduler.running else "❌ Stopped"
    embed.add_field(
        name="⏰ Task Scheduler",
        value=f"Status: {scheduler_status}\n"
              f"Jira polling: Every {config.POLLING_INTERVALS['jira']}s\n"
              f"GitHub polling: Every {config.POLLING_INTERVALS['github']}s",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command(name='check', help='Manually trigger integration checks')
@commands.has_permissions(administrator=True)
async def manual_check(ctx):
    """Manually trigger checks for all integrations."""
    await ctx.send("🔄 Starting manual integration checks...")

    # Check Jira
    await ctx.send("📋 Checking Jira for updates...")
    await task_scheduler.check_jira_updates()

    # Check GitHub
    await ctx.send("🐙 Checking GitHub for updates...")
    await task_scheduler.check_github_updates()

    await ctx.send("✅ Manual checks completed!")

@bot.command(name='webhook', help='Get webhook endpoint URLs')
@commands.has_permissions(administrator=True)
async def webhook_info(ctx):
    """Show webhook endpoint information for setup."""
    embed = discord.Embed(
        title="🔗 Webhook Configuration",
        description="Use these URLs to configure webhooks in your external services:",
        color=discord.Color.blue()
    )

    base_url = f"http://your-server:{config.WEBHOOK_CONFIG['port']}{config.WEBHOOK_CONFIG['path']}"

    embed.add_field(
        name="🐙 GitHub Webhook",
        value=f"```\n{base_url}/github\n```"
              "**GitHub Settings:**\n"
              "• Content type: `application/json`\n"
              "• Events: Pull requests, Issues\n"
              "• Secret: Configure in config.py",
        inline=False
    )

    embed.add_field(
        name="📋 Jira Webhook",
        value=f"```\n{base_url}/jira\n```"
              "**Jira Settings:**\n"
              "• Events: Issue created, Issue updated\n"
              "• Secret: Configure in config.py",
        inline=False
    )

    embed.set_footer(text="Replace 'your-server' with your actual server address or domain")

    await ctx.send(embed=embed)


def main():
    """Main function to run the bot."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Register cleanup function
    atexit.register(cleanup_pid_file)
    atexit.register(kill_all_alice_instances)
    atexit.register(stop_integrations)
    
    # Ensure single instance
    check_single_instance()
    
    try:
        logger.info('Starting Alice bot...')
        bot.run(config.DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error('Failed to login. Please check your token in config.py')
    except KeyboardInterrupt:
        logger.info('Keyboard interrupt received, shutting down...')
    except Exception as e:
        logger.error(f'An error occurred: {e}')
        logger.info('If you see SSL certificate errors, try running with: export SSL_CERT_FILE=/etc/ssl/cert.pem')
    finally:
        logger.info('Cleaning up and shutting down Alice...')
        kill_all_alice_instances()
        cleanup_pid_file()
        logger.info('Alice bot stopped.')

if __name__ == '__main__':
    main()
