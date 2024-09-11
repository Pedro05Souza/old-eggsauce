
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path
from cogs.botcore import BotCore
import logging
import os
import discord
logger = logging.getLogger('botcore')
load_dotenv()   

async def get_prefix_for_guild(bot, message):
    """Get the prefix for the guild."""
    return await BotCore.get_prefix_for_guild(bot, message)

def setup_intents() -> discord.Intents:
    """Setup the intents for the bot."""
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
    """Load all cogs in the cogs directory and its subdirectories."""
    cogs_dir = Path('./cogs')
    for filepath in cogs_dir.rglob('*.py'):
        module_path = filepath.relative_to(cogs_dir).with_suffix('').as_posix().replace('/', '.')
        logger.info(f"Loading... {module_path}")
        await bot.load_extension(f'cogs.{module_path}')

def load_bot_token() -> str:
    token = os.getenv("DISCORD_TOKEN")
    if token is None:
        raise ValueError("Token not found.")
    return token