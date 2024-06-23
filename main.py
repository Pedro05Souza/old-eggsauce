from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
import discord
import os   
import asyncio  
load_dotenv()   
TOKEN = os.getenv("DISCORD_TOKEN")  
bot = commands.Bot(command_prefix="!", intents=Intents.all(), case_insensitive=True) # set the command prefix according to your liking.


async def load_cogs():
    """Load all cogs in the cogs directory"""
    for filename in os.listdir('./cogs'):
            if filename.endswith('.py'): 
                await bot.load_extension(f'cogs.{filename[:-3]}')

asyncio.run(load_cogs())

@bot.event
async def on_ready():   
    await bot.change_presence(activity=discord.Game(name="🥚eggbux."))
    print("Command Package loaded")

bot.run(TOKEN) #Does not use a coroutine but is a blocking function - i.e. must be the last one to run