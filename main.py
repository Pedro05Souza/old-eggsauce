from discord.ext import commands
from discord import Intents
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="!", intents=Intents.all())

def main():
    bot.load_extension('comandos')
    bot.start(TOKEN)

if __name__ == "__main__":
    main()