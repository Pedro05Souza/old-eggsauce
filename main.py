from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
from pathlib import Path
import discord
import os   
import asyncio 
load_dotenv()   
TOKEN = os.getenv("DISCORD_TOKEN")  
bot = commands.Bot(command_prefix="!", intents=Intents.all(), case_insensitive=True) # set the command prefix according to your liking.

async def load_cogs():
    """Load all cogs in the cogs directory and its subdirectories."""
    cogs_dir = Path('./cogs')
    for filepath in cogs_dir.rglob('*.py'):
        module_path = filepath.relative_to(cogs_dir).with_suffix('').as_posix().replace('/', '.')
        await bot.load_extension(f'cogs.{module_path}')

asyncio.run(load_cogs())

@bot.event
async def on_ready():   
    await bot.change_presence(activity=discord.Game(name="🥚eggbux."))
    print("Command Package loaded")

bot.run(TOKEN) #Does not use a coroutine but is a blocking function - i.e. must be the last one to run