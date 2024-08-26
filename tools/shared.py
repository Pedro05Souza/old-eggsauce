"""
This module contains shared functions that are used across multiple modules.
"""


from dotenv import load_dotenv
from tools.cache.init import cache_initiator
from typing import Callable, Union
from discord.ext.commands import Context
import os
import discord
import concurrent.futures
import threading
import asyncio
import logging
logger = logging.getLogger('botcore')
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5) # 5 threads to pick from the pool
lock = threading.Lock()
cooldown_tracker = {}

async def send_bot_embed(ctx: Context, ephemeral=False, **kwargs) -> discord.Message:
    """
    Bot embed for modularization. Use this method whenever another command needs to send an embed.
    """
    embed = discord.Embed(**kwargs, color=discord.Color.yellow())
    if isinstance(ctx, discord.Interaction):
        if not ctx.response.is_done():
            message = await ctx.response.send_message(embed=embed, ephemeral=ephemeral)
        else:
            message = await ctx.followup.send(embed=embed, ephemeral=ephemeral)
    else:
        message = await ctx.send(embed=embed)
    return message

async def make_embed_object(**kwargs) -> discord.Embed:
    """
    Create an embed object.
    """
    embed = discord.Embed(**kwargs, color=discord.Color.yellow())
    return embed

def is_dev(ctx: Context) -> bool:
    """
    Check if the user is a developer.
    """
    load_dotenv()
    devs = os.getenv("DEVS").split(",")
    return str(ctx.author.id) in devs

def dev_list() -> list:
    """Return the list of developers."""
    load_dotenv()
    devs = os.getenv("DEVS").split(",")
    return devs

async def get_user_title(user_data: dict) -> str:
        """
        Get the user title.
        """
        userRoles = {
            "T" : "Egg Novice",
            "L" : "Egg Apprentice",
            "M" : "Egg wizard",
            "H" : "Egg King",
        }
        if user_data:
            if user_data["roles"] == "":
                return "Unemployed"
            return userRoles[user_data["roles"][-1]]

async def confirmation_embed(ctx, user: discord.Member, description: str) -> bool:
     """
     Confirmation embed for modularization. Use this method whenenver another command needs confirmation from the user.
     """
     embed = await make_embed_object(title=f":warning: {user.display_name}, you need to confirm this first:", description=description)
     embed.set_footer(text="React with ✅ to confirm or ❌ to cancel.")
     if isinstance(ctx, discord.Interaction):
        if not ctx.response.is_done():
            await ctx.response.send_message(embed=embed)
            msg = await ctx.original_response()
        else:
            msg = await ctx.followup.send(embed=embed)   
     else:
        msg = await ctx.send(embed=embed)
     await msg.add_reaction("✅")
     await msg.add_reaction("❌")
     client = ctx.client if isinstance(ctx, discord.Interaction) else ctx.bot
     try:
        reaction, _ = await client.wait_for("reaction_add", check=lambda reaction, author: reaction.message.id == msg.id and author.id == user.id and reaction.emoji in ["✅", "❌"], timeout=60)
        if reaction.emoji == "✅":
            return True
        else:
            return False
     except asyncio.TimeoutError:
        return False

async def user_cache_retriever(user_id: int) -> dict:
    """
    Retrieve the user cache.
    """
    keys = {"farm_data", "bank_data", "user_data"}
    user_cache = await cache_initiator.get_user_cache(user_id)
    if not user_cache or not all(key in user_cache for key in keys):
        print("db")
        user_cache = await read_and_update_cache(user_id)
        return user_cache    
    print("cache")
    return user_cache

async def read_and_update_cache(user_id: int) -> dict:
    """
    Reads the user data from the database and updates the cache.
    """
    from db.userDB import User # this is like this to avoid circular imports
    from db.bankDB import Bank # its terrible but it works
    from db.farmDB import Farm
    
    user_data = User.read(user_id)
    farm_data = Farm.read(user_id)
    bank_data = Bank.read(user_id)
    await cache_initiator.add_to_user_cache(user_id, user_data=user_data, farm_data=farm_data, bank_data=bank_data)
    user_cache = await cache_initiator.get_user_cache(user_id)
    return user_cache

async def guild_cache_retriever(guild_id: int) -> dict:
    """
    Retrieve the guild cache.
    """
    from db.botConfigDB import BotConfig # same as above
    guild_cache = await cache_initiator.get_guild_cache(guild_id)
    
    if not guild_cache:
        guild_data = BotConfig.read(guild_id)
        if guild_data:
            prefix = guild_data.get('prefix', '!')
            toggled_modules = guild_data.get('toggled_modules', None)
            channel_id = guild_data.get('channel_id', None)
            await cache_initiator.add_to_guild_cache(guild_id, prefix=prefix, toggled_modules=toggled_modules, channel_id=channel_id)
        
        guild_cache = await cache_initiator.get_guild_cache(guild_id)
    return guild_cache

def update_scheduler(func: Callable) -> None:
    """
    Schedules a coroutine to be run in the event loop with top priority.
    This should always be called when performing cache updates.
    """
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.call_soon(asyncio.ensure_future, func())
    else:
        asyncio.run(func())

def request_threading(func: Callable) -> concurrent.futures.Future: 
    """
    Request a function to be run in a separate thread. Mostly used for database operations.
    """
    with lock:
        future = executor.submit(func)
        return future

def retrieve_threads() -> int:
    """
    Retrieve the number of threads for visualization purposes.
    """
    return len(threading.enumerate())

async def return_data(ctx: Context, user=None) -> tuple:
    """
    Return the user data and the user object. This is only used in case of a command that has an user parameter.
    """
    if not user:
        return ctx.data, ctx.author
    elif user.id == ctx.author.id:
        return ctx.data, ctx.author
    else:
        return await user_cache_retriever(user.id), user

async def format_number(number) -> str:
    """
    Format the number with commas.
    """
    return "{:,.0f}".format(number).replace(",", ".")

async def cooldown_user_tracker(user_id: int) -> bool:
    """
    Track the cooldown of the user.
    """
    if user_id in cooldown_tracker:
        if cooldown_tracker[user_id] == 15:
            del cooldown_tracker[user_id]
            return True
        else:
            cooldown_tracker[user_id] += 1
            return False
    else:
        cooldown_tracker[user_id] = 1
        return True


    