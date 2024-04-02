from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
import discord
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="!", intents=Intents.all())

@bot.event
async def on_ready():
    print("Ready")
    await bot.change_presence(activity=discord.Game(name="Ballsack"))
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            await bot.load_extension(f'commands.{filename[:-3]}')

bot.run(TOKEN) #Does not use a coroutine but is a blocking function - i.e. must be the last one to run

