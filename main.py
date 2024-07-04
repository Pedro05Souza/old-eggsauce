from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
from db.botConfigDB import BotConfig
from pathlib import Path
import discord
import os   
import asyncio 
load_dotenv()   
TOKEN = os.getenv("DISCORD_TOKEN")

def get_prefix_for_guild(bot, message):
    """Get the prefix for the guild."""
    if message:
        guild_id = message.guild.id
        if BotConfig.read(guild_id)['prefix']:
            return BotConfig.read(guild_id)['prefix']
        return "!"

bot = commands.Bot(command_prefix=get_prefix_for_guild, intents=Intents.all(), case_insensitive=True)
async def load_cogs():
    """Load all cogs in the cogs directory and its subdirectories."""
    cogs_dir = Path('./cogs')
    for filepath in cogs_dir.rglob('*.py'):
        module_path = filepath.relative_to(cogs_dir).with_suffix('').as_posix().replace('/', '.')
        print(f'Loading {module_path}...')
        await bot.load_extension(f'cogs.{module_path}')

asyncio.run(load_cogs())

@bot.event
async def on_ready():   
    await bot.change_presence(activity=discord.Game(name="🥚eggbux."))
    print("Command Package loaded")

bot.run(TOKEN) #Does not use a coroutine but is a blocking function - i.e. must be the last one to run