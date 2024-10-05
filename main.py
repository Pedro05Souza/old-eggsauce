"""
Main file to run the bot.
"""
from setup import *
from logs import set_bot_logger_flag, log_info
import discord
import logging

logger = logging.getLogger('bot_logger')
        
@bot.event
async def on_ready():   
    await bot.change_presence(activity=discord.Game(name="🥚eggbux."))
    await load_cogs()
    log_info(f"Bot is ready")
    log_info(f"Logged in as {bot.user.name} - {bot.user.id}")

def bot_start(bot_logging=False):
    """
    Run the bot.

    Args:
        bot_logging (bool, optional): Whether to log the bot's actions. Defaults to False.
    """
    set_bot_logger_flag(bot_logging)
    bot.run(load_bot_token())

if __name__ == "__main__":
    bot_start(bot_logging=True)