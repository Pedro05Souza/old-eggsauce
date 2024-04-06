from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
import discord
import os
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="!", intents=Intents.all())

async def load_cogs():
    for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                await bot.load_extension(f'commands.{filename[:-3]}')

asyncio.run(load_cogs())

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Ballsack"))
    print("Command Package loaded")

bot.run(TOKEN) #Does not use a coroutine but is a blocking function - i.e. must be the last one to run

