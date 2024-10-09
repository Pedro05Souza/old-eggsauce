"""
Main file to run the bot.
"""
from setup import *
from logs import set_bot_logger_flag, log_info
import discord
 
@bot.event
async def on_ready():   
    await bot.change_presence(activity=discord.Game(name="🥚eggbux."))
    await load_cogs()
    log_info(f"Bot is ready")
    log_info(f"Logged in as {bot.user.name} - {bot.user.id}")

def bot_start(bot_logging=False, is_production=False):
    """
    Runs the bot.

    Args:
        bot_logging (bool, optional): Whether the bot's logging system should be enabled.
        is_production (bool, optional): Whether the bot should start in production mode.
    """
    set_bot_logger_flag(bot_logging)
    bot.run(load_bot_token(is_production))

if __name__ == "__main__":
    bot_start(bot_logging=True, is_production=True)