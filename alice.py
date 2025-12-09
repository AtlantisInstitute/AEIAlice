#!/usr/bin/env python3
"""
Alice - Discord Bot for Atlantis Institute
A helpful Discord bot to manage the Atlantis Institute server.
"""

import discord
from discord.ext import commands
import config
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Alice')

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
        intro_message = ("Hello, my name is Alice Synthesis 30 and I am the news AI assitant administrator "
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
    try:
        logger.info('Starting Alice bot...')
        bot.run(config.DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error('Failed to login. Please check your token in config.py')
    except Exception as e:
        logger.error(f'An error occurred: {e}')
    finally:
        logger.info('Alice bot stopped.')

if __name__ == '__main__':
    main()
