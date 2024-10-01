"""
This module contains shared functions that are used across multiple modules.
"""
from datetime import datetime
from dotenv import load_dotenv
from temp import cache_initiator, cooldown_tracker
from typing import Union
from discord.ext.commands import Context
from discord import Interaction
from discord.utils import format_dt
from discord.ui import View
from copy import deepcopy
import os
import discord
import threading
import asyncio
import logging

logger = logging.getLogger("bot_logger")

__all__ = [
    'send_bot_embed',
    'make_embed_object',
    'is_dev',
    'dev_list',
    'confirmation_embed',
    'user_cache_retriever',
    'read_and_update_cache',
    'user_cache_retriever_copy',
    'guild_cache_retriever',
    'retrieve_threads',
    'return_data',
    'format_number',
    'cooldown_user_tracker',
    'update_user_param',
    'get_user_title',
    'format_date',
    "button_builder",
    "button_view_builder",
    "can_listener_run",
]

async def send_bot_embed(ctx: Context | Interaction , ephemeral=False, **kwargs) -> discord.Message:
    """
    Bot embed for modularization. Use this method whenever another command needs to send an embed.

    Args:
        ctx (Context | Interaction): The context of the command.
        ephemeral (bool): Whether the message should be ephemeral or not. 
        (This is only used for interactions, will raise an error if used for non-interactions)
        **kwargs: The keyword arguments for the embed.

    Returns:
        discord.Message
    """
    embed = discord.Embed(**kwargs, color=discord.Color.yellow())

    if isinstance(ctx, Interaction):
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
    devs = dev_list()
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

async def confirmation_embed(ctx: Context | Interaction , user: discord.Member, description: str) -> bool:
    """
    Confirmation embed for modularization. Use this method whenever another command needs confirmation from the user.

    Args:
        ctx (Context | Interaction): The context of the command.
        user (discord.Member): The user to confirm.
        description (str): The description of the embed.

    Returns:
        bool
    """
    embed = await make_embed_object(title=f":warning: {user.display_name}, you need to confirm this first:", description=description)
    embed.set_footer(text="Press ✅ to confirm or ❌ to cancel.")

    if isinstance(ctx, discord.Interaction):
        if not ctx.response.is_done():
            await ctx.response.send_message(embed=embed)
            msg = await ctx.original_response()
        else:
            msg = await ctx.followup.send(embed=embed)   
    else:
        msg = await ctx.send(embed=embed)

    confirmation_button = await button_builder(label="Accept", style=discord.ButtonStyle.green, custom_id="confirm")
    cancel_button = await button_builder(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel")
    view = await button_view_builder(confirmation_button, cancel_button)
    await msg.edit(view=view)
    client = ctx.client if isinstance(ctx, discord.Interaction) else ctx.bot

    try:
        interaction = await client.wait_for("interaction", check=lambda i: i.message.id == msg.id and i.user.id == user.id, timeout=30)
        await interaction.response.defer()
        if interaction.data["custom_id"] == "confirm":
            return True
        else:
            return False
    except asyncio.TimeoutError:
        return False

async def user_cache_retriever(user_id: int) -> Union[dict, None]:
    """
    Retrieves the user cache.

    Args:
        user_id (int): The user id to get the cache for.

    Returns:
        dict
    """
    keys = {"farm_data", "bank_data", "user_data"}
    user_cache = await cache_initiator.get(user_id)
    
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
    from db import User, Farm, Bank # this is like this to avoid circular imports its terrible but it works
    
    user_data = await User.read(user_id)

    if not user_data:
        return None
    
    farm_data = await Farm.read(user_id)
    bank_data = await Bank.read(user_id)
    await cache_initiator.put_user(user_id, user_data=user_data, farm_data=farm_data, bank_data=bank_data)
    user_cache = await cache_initiator.get(user_id)
    return user_cache

async def user_cache_retriever_copy(user_id: int) -> Union[dict, None]:
    """
    Retrieves a copy of the user cache. This is used in case you don't want the cache to be updated during runtime.

    Args:
        user_id (int): The user id to get the cache for.

    Returns:
        dict
    """
    cache = await user_cache_retriever(user_id)

    if cache:
        return deepcopy(cache)
    
    return None

async def guild_cache_retriever(guild_id: int) -> dict:
    """
    Retrieves the guild cache.

    Args:
        guild_id (int): The guild id to get the cache for.

    Returns:
        dict
    """
    from db import BotConfig # same as above
    
    guild_cache = await cache_initiator.get(guild_id)
    
    if not guild_cache:
        guild_data = await BotConfig.read(guild_id)
        prefix = guild_data['prefix']  

        if prefix is None:
            prefix = "!"
        
        toggled_modules = guild_data.get('toggled_modules', None)
        channel_id = guild_data.get('channel_id', None)
        await cache_initiator.put_guild(guild_id, prefix=prefix, toggled_modules=toggled_modules, channel_id=channel_id)
        return await cache_initiator.get(guild_id)
    return guild_cache

def retrieve_threads() -> int:
    """
    Retrieves the number of threads for visualization purposes.

    Returns:
        int
    """
    return len(threading.enumerate())

async def return_data(ctx: Context, user= None) -> tuple:
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
    
async def format_date(date: datetime) -> str:
    """
    Format the date.

    Args:
        date (datetime): The date to format.

    Returns:
        str
    """
    return format_dt(date, "R")

async def update_user_param(ctx: Context, user_data: dict, data: dict, user: discord.Member) -> None:
    """
    Updates the user that the author of the command pinged.

    Args:
        ctx (Context): The context of the command.
        user_data (dict): The user data.
        data (dict): The data to update.
        user (discord.Member): The user to update the data for.

    Returns:
        None
    """
    from tools import update_user_farm_on_command, update_user_points_in_voice
    
    await update_user_farm_on_command(ctx, user_data, data, user)
    await update_user_points_in_voice(ctx, user_data, user)

async def button_builder(**kwargs) -> discord.Button:
    """
    Builds a button.

    Args:
        label (str): The label of the button.
        style (discord.ButtonStyle): The style of the button.
        custom_id (str): The custom id of the button.

    Returns:
        discord.Button
    """
    return discord.ui.Button(**kwargs)

async def button_view_builder(*buttons) -> discord.ui.View:
    """
    Builds a view with buttons.

    Args:
        *buttons: The buttons to add to the view.

    Returns:
        discord.ui.View
    """
    view = View()
    for button in buttons:
        view.add_item(button)
    return view

async def can_listener_run(guild_id: int) -> bool:
    """
    Checks if the listener can happen based on the guild and the bot's configuration.
    """
    guild_data = await guild_cache_retriever(guild_id)

    if guild_data['toggled_modules'] == 'N':
        return False
    return True