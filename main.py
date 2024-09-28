"""
Main file to run the bot.
"""
from setup import *
import discord
import logging

logger = logging.getLogger('bot_logger')
        
@bot.event
async def on_ready():   
    await bot.change_presence(activity=discord.Game(name="🥚eggbux."))
    await load_cogs()
    logger.info(f"Bot is ready")
    logger.info(f"Logged in as {bot.user.name} - {bot.user.id}")

if __name__ == "__main__":
    bot.run(load_bot_token())