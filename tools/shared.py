"""
This module contains shared functions that are used across multiple modules.
"""


from dotenv import load_dotenv
from tools.cache import cache_initiator
from typing import Callable
from discord.ext.commands import Context
from contextlib import contextmanager
import os
import discord
import concurrent.futures
import threading
import asyncio
import logging
logger = logging.getLogger('botcore')
num_cores = os.cpu_count()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_cores // 2) # half of the cores
global_lock = threading.Lock()
cooldown_tracker = {}
lock_tracker = {}

async def send_bot_embed(ctx: Context, ephemeral=False, **kwargs) -> discord.Message:
    """
    Bot embed for modularization. Use this method whenever another command needs to send an embed.

    Args:
        ctx (Context): The context of the command.
        ephemeral (bool): Whether the message should be ephemeral or not. (This is only used for interactions, will raise an error if used for non-interactions)
        **kwargs: The keyword arguments for the embed.

    Returns:
        discord.Message
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
    Creates an embed object.

    Args:
        **kwargs: The keyword arguments for the embed.

    Returns:
        discord.Embed
    """
    embed = discord.Embed(**kwargs, color=discord.Color.yellow())
    return embed

def is_dev(ctx: Context) -> bool:
    """
    Checks if the user is a developer.

    Args:
        ctx (Context): The context of the command.

    Returns:
        bool
    """
    load_dotenv()
    devs = os.getenv("DEVS").split(",")
    return str(ctx.author.id) in devs

def dev_list() -> list:
    """
    Returns the list of developers.

    Returns:
        list
    """
    load_dotenv()
    devs = os.getenv("DEVS").split(",")
    return devs

async def get_user_title(user_data: dict) -> str:
        """
        Gets the user title.

        Args:
            user_data (dict): The user data.
        
        Returns:
            str
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
    Confirmation embed for modularization. Use this method whenever another command needs confirmation from the user.

    Args:
        ctx (Context): The context of the command.
        user (discord.Member): The user to confirm.
        description (str): The description of the embed.

    Returns:
        bool
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
    Retrieves the user cache.

    Args:
        user_id (int): The user id to get the cache for.

    Returns:
        dict
    """
    keys = {"farm_data", "bank_data", "user_data"}
    user_cache = await cache_initiator.get_user_cache(user_id)
    if not user_cache or not all(key in user_cache for key in keys):
        user_cache = await read_and_update_cache(user_id)
        return user_cache    
    return user_cache

async def read_and_update_cache(user_id: int) -> dict:
    """
    Reads the user data from the database and updates the cache.

    Args:
        user_id (int): The user id to read the data for.

    Returns:
        dict
    """
    from db.userdb import User # this is like this to avoid circular imports
    from db.bankdb import Bank # its terrible but it works
    from db.farmdb import Farm
    
    user_data = User.read(user_id)
    farm_data = Farm.read(user_id)
    bank_data = Bank.read(user_id)
    await cache_initiator.add_to_user_cache(user_id, user_data=user_data, farm_data=farm_data, bank_data=bank_data)
    user_cache = await cache_initiator.get_user_cache(user_id)
    return user_cache

async def guild_cache_retriever(guild_id: int) -> dict:
    """
    Retrieves the guild cache.

    Args:
        guild_id (int): The guild id to get the cache for.

    Returns:
        dict
    """
    from db.botconfigdb import BotConfig # same as above
    guild_cache = await cache_initiator.get_guild_cache(guild_id)
    
    if not guild_cache:
        guild_data = BotConfig.read(guild_id)
        prefix = guild_data['prefix']      
        if prefix is None:
            prefix = "!"
        toggled_modules = guild_data.get('toggled_modules', None)
        channel_id = guild_data.get('channel_id', None)
        await cache_initiator.add_to_guild_cache(guild_id, prefix=prefix, toggled_modules=toggled_modules, channel_id=channel_id)
        return await cache_initiator.get_guild_cache(guild_id)
    return guild_cache

def update_scheduler(callback: Callable) -> None:
    """
    Schedules a coroutine to be run in the event loop with top priority.
    This should always be called when performing cache updates.

    Args:
        callback (Callable): The coroutine to run.

    Returns:
        None
    """
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.call_soon(asyncio.ensure_future, callback())
    else:
        asyncio.run(callback())

def request_threading(callback: Callable, id: int = None) -> concurrent.futures.Future: 
    """
    Requests a function to be run in a separate thread. Mostly used for database operations.
    Obs: All get requests from database are NOT thread safe, while all write requests are.

    Args:
        callback (Callable): The function to run.
        id (int): The id to lock the thread with. If None, the thread will not be locked.

    Returns:
        concurrent.futures.Future
    """
    if id is None:
        lock_context = None
    else:
        lock_context = lock_manager(id)
    
    if lock_context:
        with lock_context:
            future = executor.submit(callback)
    else:
        future = executor.submit(callback)
    
    return future

def retrieve_threads() -> int:
    """
    Retrieves the number of threads for visualization purposes.

    Returns:
        int
    """
    return len(threading.enumerate())

async def return_data(ctx: Context, user=None) -> tuple:
    """
    Returns the user data and the user object. This is only used in case of a command that has an optional user parameter.

    Args:
        ctx (Context): The context of the command.
        user (discord.Member): The user to get the data for.

    Returns:
        tuple
    """
    if not user:
        return ctx.data, ctx.author
    elif user.id == ctx.author.id:
        return ctx.data, ctx.author
    else:
        return await user_cache_retriever(user.id), user

async def format_number(number) -> str:
    """
    Formats the number with commas.

    Args:
        number: The number to format.

    Returns:
        str
    """
    return "{:,.0f}".format(number).replace(",", ".")

async def cooldown_user_tracker(user_id: int) -> bool:
    """
    Tracks the cooldown of the user.

    Args:
        user_id (int): The user id to track the cooldown for.

    Returns:
        bool
    """
    if user_id in cooldown_tracker:
        if cooldown_tracker[user_id] == 5:
            del cooldown_tracker[user_id]
            return True
        else:
            cooldown_tracker[user_id] += 1
            return False
    else:
        cooldown_tracker[user_id] = 1
        return True  
    
@contextmanager
def lock_manager(id: int):
    """
    Locks data to avoid multiple access from different threads with the same user id.

    Args:
        id (int): The id to lock the data with.

    Returns:
        None
    """
    with global_lock:
        if id not in lock_tracker:
            lock_tracker[id] = global_lock
    lock = lock_tracker[id]
    lock.acquire()
    try:
        yield
    finally:
        lock_tracker[id].release()
        lock_tracker.pop(id)