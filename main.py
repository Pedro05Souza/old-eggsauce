from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="!", intents=Intents.all())

@bot.event
async def on_ready():
    print("Ready")
    await bot.load_extension('comandos') #Since discord.py 2.0 must be async function

bot.run(TOKEN) #Does not use a coroutine but is a blocking function - i.e. must be the last one to run

""" This is the bot.start() implementation -- Must use asyncio for an async loop as it is a coroutine
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(bot.start(TOKEN))
except KeyboardInterrupt:
    loop.run_until_complete(bot.logout())
finally:
    loop.close()
"""