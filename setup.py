"""
This moodule handles the setup of the bot and the loading of the cogs.
"""
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path
from cogs.botmanager import BotManager
import os
import discord
import logging

logger = logging.getLogger('bot_logger')

async def get_prefix_for_guild(bot, message) -> str:
    """
    Get the prefix for the guild.

    Args:
        bot (commands.Bot): The bot instance.
        message (discord.Message): The message instance.

    Returns:
        str
    """
    return await BotManager.get_prefix_for_guild(bot, message)

def setup_intents() -> discord.Intents:
    """
    Setup intents for the bot.


    Returns:
        discord.Intents
    """
    intents = discord.Intents.default()
    intents.members = True
    intents.voice_states = True
    intents.reactions = True
    intents.messages = True
    intents.guilds = True
    intents.message_content = True
    return intents  

bot = commands.Bot(command_prefix=get_prefix_for_guild, intents=setup_intents(), case_insensitive=True, help_command=None)

async def load_cogs() -> None:
    """
    Loads all cogs in the cogs directory and its subdirectories.

    Returns:
        None
    """
    cogs_dir = Path('./cogs')
    for filepath in cogs_dir.rglob('*.py'):
        module_path = filepath.relative_to(cogs_dir).with_suffix('').as_posix().replace('/', '.')
        logger.info(f"Loading... {module_path}")
        await bot.load_extension(f'cogs.{module_path}')

def load_bot_token() -> str:
    """
    Loads the bot token from the environment variables.

    Returns:
        str
    """
    load_dotenv()   
    token = os.getenv("DISCORD_TOKEN")
    if token is None:
        raise ValueError("Token not found.")
    return token