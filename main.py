from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
from db.botConfigDB import BotConfig
from pathlib import Path
import logging
import discord
import os   
import asyncio 

logger = logging.getLogger('botcore')
load_dotenv()   
TOKEN = os.getenv("DISCORD_TOKEN")

def get_prefix_for_guild(bot, message):
    """Get the prefix for the guild."""
    if message:
        bot_data = BotConfig.read(message.guild.id)
        if bot_data['prefix']:
            return bot_data['prefix']
        return "!"

bot = commands.Bot(command_prefix=get_prefix_for_guild, intents=Intents.all(), case_insensitive=True, help_command=None)
async def load_cogs():
    """Load all cogs in the cogs directory and its subdirectories."""
    cogs_dir = Path('./cogs')
    for filepath in cogs_dir.rglob('*.py'):
        module_path = filepath.relative_to(cogs_dir).with_suffix('').as_posix().replace('/', '.')
        logger.info(f"Loading... {module_path}")
        await bot.load_extension(f'cogs.{module_path}')

asyncio.run(load_cogs())

@bot.event
async def on_ready():   
    await bot.change_presence(activity=discord.Game(name="🥚eggbux."))
    logger.info(f"Bot is ready")
    logger.info(f"Logged in as {bot.user.name} - {bot.user.id}")

async def main():
    try:
        await bot.start(TOKEN, reconnect=True) #Does not reconnect on disconnect
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logging.critical(f"Error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main())