"""
This moodule handles the setup of the bot and the loading of the cogs.
"""
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path
from cogs import BotManager
from logs import log_info
import os
import discord

__all__ = [
    "get_prefix_for_guild",
    "setup_intents",
    "bot",
    "load_cogs",
    "load_bot_token",
]

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

        if filepath.stem == '__init__':
            continue

        module_path = filepath.relative_to(cogs_dir).with_suffix('').as_posix().replace('/', '.')
        log_info(f"Loading...{module_path}")
        await bot.load_extension(f'cogs.{module_path}')

def load_bot_token(is_production) -> str:
    """
    Loads the bot token from the environment variables.

    Returns:
        str
    """
    load_dotenv()

    if is_production:   
        token = os.getenv("PROD")
    
    else:
        token = os.getenv("DEV")

    if token is None:
        raise ValueError("Token not found.")
    return token