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

def signal_handler(signum, frame):
    """Handle termination signals gracefully."""
    logger.info(f'Received signal {signum}, shutting down Alice...')
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

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    logger.info(f'Alice is online! Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'Connected to {len(bot.guilds)} server(s)')

    # Set a custom status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="over Atlantis Institute"
        )
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


def main():
    """Main function to run the bot."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Register cleanup function
    atexit.register(cleanup_pid_file)
    atexit.register(kill_all_alice_instances)
    
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
