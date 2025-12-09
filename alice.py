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

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    logger.info(f'Alice is online! Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'Connected to {len(bot.guilds)} server(s)')

    # Send online message and Confluence link to each guild
    for guild in bot.guilds:
        channel = await find_status_channel(guild)
        if channel:
            # Send online message
            await channel.send("🟢 **Alice Synthesis 30 is now online!** Ready to assist Atlantis Institute with AI-powered administration. 🤖")

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

            logger.info(f'Sent online message and Confluence link to #{channel.name} in {guild.name}')

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

@bot.event
async def on_disconnect():
    """Called when the bot disconnects from Discord."""
    logger.info('Alice is disconnecting...')

    # Try to send offline messages to guilds before disconnecting
    # Note: This may not always work as the bot is disconnecting
    try:
        for guild in bot.guilds:
            channel = await find_status_channel(guild)
            if channel:
                await channel.send("🔴 **Alice Synthesis 30 is going offline.** AI systems powering down. See you next time! 👋")
                logger.info(f'Sent offline message to #{channel.name} in {guild.name}')
    except Exception as e:
        logger.warning(f'Could not send offline messages: {e}')
        logger.info('Alice disconnected without sending offline messages')

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

def main():
    """Main function to run the bot."""
    try:
        logger.info('Starting Alice bot...')
        bot.run(config.DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error('Failed to login. Please check your token in config.py')
    except Exception as e:
        logger.error(f'An error occurred: {e}')
        logger.info('If you see SSL certificate errors, try running with: export SSL_CERT_FILE=/etc/ssl/cert.pem')
    finally:
        logger.info('Alice bot stopped.')

if __name__ == '__main__':
    main()
