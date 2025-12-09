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

# Global flag to track if Confluence link has been posted this session
confluence_link_posted = False

async def find_status_channel(guild):
    """Find a suitable channel to send status messages."""
    # Try system channel first, then general channel, then the first text channel
    if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
        return guild.system_channel
    else:
        # Look for a general channel
        for ch in guild.text_channels:
            if ch.name.lower() in ['general', 'main', 'lobby', 'chat'] and ch.permissions_for(guild.me).send_messages:
                return ch

        # If no general channel found, use the first text channel the bot can send to
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                return ch
    return None

async def post_confluence_link():
    """Post the Confluence project link to all guilds."""
    for guild in bot.guilds:
        channel = await find_status_channel(guild)
        if channel:
            # Send and pin Confluence project link
            confluence_message = await channel.send(
                "📋 **Atlantis Institute Project Documentation**\n"
                "🔗 https://atlantisinstitute.atlassian.net/wiki/x/DgCUD\n"
                "📌 *This link has been pinned for easy access to project documentation.*"
            )

            # Pin the message
            try:
                await confluence_message.pin()
                logger.info(f'Pinned Confluence link in #{channel.name} in {guild.name}')
            except discord.Forbidden:
                logger.warning(f'Could not pin Confluence link in #{channel.name} - missing permissions')
            except Exception as e:
                logger.warning(f'Error pinning Confluence link: {e}')

            logger.info(f'Posted Confluence link to #{channel.name} in {guild.name}')

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    logger.info(f'Alice is online! Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'Connected to {len(bot.guilds)} server(s)')

    # Post Confluence link once per session (not on every reconnect)
    global confluence_link_posted
    if not confluence_link_posted:
        await post_confluence_link()
        confluence_link_posted = True

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

@bot.command(name='docs', aliases=['confluence', 'project'], help='Get Atlantis Institute project documentation link')
async def docs(ctx):
    """Send the Atlantis Institute Confluence project documentation link."""
    await ctx.send(
        "📋 **Atlantis Institute Project Documentation**\n"
        "🔗 https://atlantisinstitute.atlassian.net/wiki/x/DgCUD\n"
        "*Access all project documentation, requirements, and resources here.*"
    )

@bot.command(name='pin-docs', aliases=['pin-confluence'], help='Post and pin the project documentation link (admin only)')
async def pin_docs(ctx):
    """Post and pin the Confluence project documentation link."""
    # Check if user has manage messages permission
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("❌ You need 'Manage Messages' permission to use this command.")
        return

    global confluence_link_posted
    confluence_link_posted = True  # Mark as posted to avoid duplicate posting
    await post_confluence_link()
    await ctx.send("✅ Project documentation link posted and pinned!")

def main():
    """Main function to run the bot."""
    global confluence_link_posted
    try:
        logger.info('Starting Alice bot...')
        confluence_link_posted = False  # Reset flag on startup
        bot.run(config.DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error('Failed to login. Please check your token in config.py')
    except Exception as e:
        logger.error(f'An error occurred: {e}')
        logger.info('If you see SSL certificate errors, try running with: export SSL_CERT_FILE=/etc/ssl/cert.pem')
    finally:
        confluence_link_posted = False  # Reset flag on shutdown
        logger.info('Alice bot stopped.')

if __name__ == '__main__':
    main()
