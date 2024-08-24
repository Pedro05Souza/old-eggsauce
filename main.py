from discord.ext import commands
from dotenv import load_dotenv
from cogs.botcore import BotCore
from pathlib import Path
import logging
import discord
import os   
import asyncio 
logger = logging.getLogger('botcore')
load_dotenv()   
TOKEN = os.getenv("DISCORD_TOKEN")

async def get_prefix_for_guild(bot, message):
    return await BotCore.get_prefix_for_guild(bot, message)

def setup_intents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.members = True
    intents.voice_states = True
    intents.reactions = True
    intents.messages = True
    intents.guilds = True
    intents.message_content = True
    return intents

bot = commands.Bot(command_prefix=get_prefix_for_guild, intents=setup_intents(), case_insensitive=True, help_command=None)

async def load_cogs():
    """Load all cogs in the cogs directory and its subdirectories."""
    cogs_dir = Path('./cogs')
    for filepath in cogs_dir.rglob('*.py'):
        module_path = filepath.relative_to(cogs_dir).with_suffix('').as_posix().replace('/', '.')
        logger.info(f"Loading... {module_path}")
        await bot.load_extension(f'cogs.{module_path}')
        
@bot.event
async def on_ready():   
    await bot.change_presence(activity=discord.Game(name="🥚eggbux."))
    logger.info(f"Bot is ready")
    logger.info(f"Logged in as {bot.user.name} - {bot.user.id}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(load_cogs())
    loop.run_until_complete(bot.run(TOKEN))