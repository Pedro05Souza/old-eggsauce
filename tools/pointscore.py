"""
This module contains functions that are used in the decorator predicates of the points commands.
"""
from typing import Optional
from db.userdb import User
from db.bankdb import Bank
from discord.ext import commands
from lib.shared import *
from lib.chickenlib import update_user_farm, update_player_corn
from resources import Prices, USER_SALARY_DROP
from discord.ext.commands import Context
from tools.listeners import on_user_transaction
import logging
import discord
import time

logger = logging.getLogger('bot_logger')

__all__ = ["refund"]

async def get_points_commands_submodules(ctx: Context, config_data: dict) -> bool:
    """
    Verify if the current command's cog is enabled in the server.

    Args:
        ctx (Context): The context of the command.
        config_data (dict): The server's configuration data.

    Returns:
        bool
    """
    active_module = config_data['toggled_modules']
    shared_cogs = ["BaseCommands", "BankCommands"]
    chicken_cogs = ["ChickenCore", "ChickenEvents", "ChickenView", "CornCommands", "PlayerMarket", "ChickenCombat"]
    interactive_cogs = ["InteractiveCommands"]
    module_cogs = {
        "C": set(chicken_cogs + shared_cogs),
        "I": set(interactive_cogs + shared_cogs)
    }
    
    if active_module == "T":
        return True
    
    if active_module == "N":
        await send_bot_embed(ctx, description=":warning: The points commands are **disabled** in this server.")
        return False
    
    cogs_to_check = module_cogs.get(active_module, [])
    if ctx.cog.qualified_name in cogs_to_check:
        return True 
    else:
        await send_bot_embed(ctx, description=":warning: This module is not enabled in this server.")
        return False

async def verify_points(command: str, user_data: dict) -> bool:
    """
    Verifies if the user has enough points to use the command.

    Args:
        command (str): The command to verify.
        user_data (dict): The user data.

    Returns:
        bool
    """
    price = Prices[command].value
    return user_data["points"] >= price

async def verify_if_farm_command(command: commands.Command) -> bool:
    """
    Verifies if the command belongs to a farm-related cog.

    Args:
        command (commands.Command): The command to verify.

    Returns:
        bool
    """
    chicken_cogs = {"ChickenCore", "ChickenEvents", "ChickenView", "CornCommands", "PlayerMarket", "ChickenCombat"}
    cog = command.cog

    if cog.qualified_name in chicken_cogs:
        return True
    return False

async def verify_correct_channel(ctx: Context, config_data: dict) -> bool:
        """
        Verifies if the command is being used in the correct channel.

        Args:
            ctx (Context): The context of the command.
            config_data (dict): The server's configuration data.

        Returns:
            bool
        """
        if ctx.channel.id != config_data['channel_id']:
            commands_object = ctx.bot.get_channel(config_data['channel_id'])
            channel_mention = commands_object.mention
            embed = await make_embed_object(title=":no_entry_sign: Invalid channel", description=f"Please use the right commands channel: **{channel_mention}**")
            if ctx.interaction is not None:
                await ctx.interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await ctx.author.send(embed=embed)
            return False
        return True
            
async def refund(user: discord.Member, ctx: Context) -> None:
    """
    Refunds the user if the command fails.

    Args:
        user (discord.Member): The user to refund.
        ctx (Context): The context of the command.
    
    Returns:
        None
    """
    try:
        price = Prices[ctx.command.name].value
        user_data = await user_cache_retriever(user.id)
        user_data = user_data["user_data"]
        await User.update_points(user.id, user_data["points"] + price)
    except Exception as e:
        logger.error(f"An error occurred while refunding the user: {e}")

async def treat_exceptions(ctx: Context, command: str, user_data: dict, config_data: dict, data: dict) -> bool:
    """
    Treat the exceptions that may occur while executing the command.

    Args:
        ctx (Context): The context of the command.
        command (str): The command name.
        user_data (dict): The user data.
        config_data (dict): The server's configuration data.
        data (dict): The cache data.

    Returns:
        bool
    """
    is_slash_command = hasattr(ctx, "interaction") and ctx.interaction is not None
    if is_slash_command:

        if not await verify_correct_channel(ctx, config_data):
            return False
        
        if Prices[command].value == 0:
            return True
        
        new_points = user_data["points"] - Prices[command].value

        await User.update_points(ctx.author.id, new_points)
        await on_user_transaction(ctx, Prices[command].value, 1)
        return True
    
    if not await verify_correct_channel(ctx, config_data):
        return False
    
    if Prices[command].value == 0:
        return True
    
    new_points = user_data['points'] - Prices[command].value
    await User.update_points(ctx.author.id, new_points)
    await on_user_transaction(ctx, Prices[command].value, 1)
    return True

async def handle_exception(ctx: Context, description: str) -> None:
    """
    Handle the exception that may occur while executing the command.

    Args:
        ctx (Context): The context of the command.
        description (str): The description of the embed.

    Returns:
        None
    """
    if await cooldown_user_tracker(ctx.author.id):
        await send_bot_embed(ctx, description=description)
        await refund(ctx.author, ctx)
    
async def automatic_register(user: discord.Member) -> None:
    """
    Automatically registers the user in the database.

    Args:
        user (discord.Member): The user to register.
    
    Returns:
        None
    """
    user_data = await user_cache_retriever(user.id)
    if user_data:
        return
    elif user.bot:
        return
    else:
        await User.create(user.id, 0)
        await Bank.create(user.id, 0, 1)
        logger.info(f"{user.display_name} has been registered.")

async def verify_if_server_has_modules(ctx: Context, config_data: dict) -> bool:
    """
    Check if the server has the necessary requirements to use the points commands

    Args:
        ctx (Context): The context of the command.
        config_data (dict): The server's configuration

    Returns:
        bool
    """
    modules = config_data.get('toggled_modules', None)	
    if not modules:
        await send_bot_embed(ctx, description=":warning: The modules aren't configured in this server. Type **!setModule** to configure them. To see the available modules type **!modules**.")
        return False
    return True

async def verify_if_server_has_channel(ctx: Context, config_data: dict) -> bool:
    """
    Check if the server has the necessary requirements to use the points commands

    Args:
        ctx (Context): The context of the command.
        config_data (dict): The server's configuration data.
    """
    if not config_data['channel_id']:
        await send_bot_embed(ctx, description=":warning: The commands channel isn't configured in this server. Type **!setChannel** in the desired channel.")
        return False
    return True

async def check_server_requirements(ctx: Context, config_data: dict) -> bool:
    """
    Check if the server has the necessary requirements to use the points commands

    Args:
        ctx (Context): The context of the command.
        config_data (dict): The server's configuration data.
    """
    if not await verify_if_server_has_modules(ctx, config_data):
            return False
        
    if not await verify_if_server_has_channel(ctx, config_data):
        return False
    
    if config_data['toggled_modules'] == "N":
        embed = await make_embed_object(description=":warning: The points commands are **disabled** in this server.")
        await ctx.author.send(embed=embed)
        return False
    return True

async def send_away_user_rewards(ctx: Context, salary_gained: int, total_profit: int, corn_produced: int, user: discord.Member) -> None:
    """
    Sends a message to the user to see how many he gained during his time away.

    Args:
        ctx (Context): The context of the command.
        salary_gained (int): The amount of salary the user gained.
        total_profit (int): The total profit the user gained.
        corn_produced (int): The amount of corn the user produced.
        user (discord.Member): The user to send the message.

    Returns:
        None
    """
    description = f":tada: while **{user.display_name}** was away, they gained:\n"

    if salary_gained > 0:
        description += f":money_with_wings: **{await format_number(salary_gained)}** eggbux from their salary.\n"
    if total_profit > 0:
        description += f":wood: **{await format_number(total_profit)}** eggbux from their farm.\n"
    if corn_produced > 0:
        description += f":corn: **{await format_number(corn_produced)}** corn from their farm."
    if salary_gained > 0 or total_profit > 0 or corn_produced > 0:
        await send_bot_embed(ctx, description=description)

async def get_salary_points(user: discord.Member, user_data: dict) -> int:
    """
    Calculates the salary of the user based on their roles.

    Args:
        user (discord.Member): The user to calculate the salary.
        user_data (dict): The data of the user.

    Returns:
        int
    """
    last_title_drop = time.time() - user_data["salary_time"]
    hours_passed = min(last_title_drop // USER_SALARY_DROP, 12)
    hours_passed = int(hours_passed)
    salary = await salary_role(user_data)
    if hours_passed > 0 and user_data["roles"] != "":
        points_gained = salary * hours_passed
        await User.update_points(user.id, user_data["points"] + points_gained)
        await User.update_salary_time(user.id)
        return points_gained
    return 0

async def salary_role(user_data: dict) -> int:
    """
    Returns the salary of a user based on their roles.

    Args:
        user_data (dict): The data of the user.

    Returns:
        int
    """
    salarios = {
        "T": 20,
        "L": 40,
        "M": 60,
        "H": 80
    }
    if user_data['roles'] != "":
        return salarios[user_data["roles"][-1]]
    else:
        return 0
    
async def update_user_farm_on_command(ctx: Context, user_data: dict, data: dict, user: discord.Member)  -> None:
    """
    Updates the user's farm data if the user uses any command.

    Args:
        ctx (Context): The context of the command.
        user_data (dict): The data of the user.
        farm_data (dict): The data of the farm.
        user (discord.Member): The user to update the farm.

    Returns:
        None
    """
    salary_gained = await get_salary_points(user, user_data)

    if data['farm_data']:     
        data['farm_data'], total_profit = await update_user_farm(ctx, user, data)
        corn_to_cache, corn_produced = await update_player_corn(user, data['farm_data'])
        data['farm_data']['corn'] = corn_to_cache
        await send_away_user_rewards(ctx, salary_gained, total_profit, corn_produced, user)

async def update_user_points_in_voice(ctx: Context, user_data: dict, author: discord.Member) -> None:
    """
    Updates the user's points if they are in a voice channel.

    Args:
        ctx (Context): The context of the command.
        user_data (dict): The data of the user.
        author_id (discord.Member): The user to update the points.

    Returns:
        None
    """
    points_manager = ctx.bot.get_cog("PointsManager")
    await points_manager.update_user_points_in_voice(author, user_data)

async def get_config_data(ctx: Context) -> Optional[dict]:
    """
    Retrieves the configuration data of the server 
    and checks if the user has the necessary requirements to use the points commands.

    Args:
        ctx (Context): The context of the command.

    Returns:
        dict
    """
    config_data = await guild_cache_retriever(ctx.guild.id)
    if not await check_server_requirements(ctx, config_data):
        return None
    return config_data

async def validate_command(ctx: Context) -> bool:
    """
    Validates the command before executing it.

    Args:
        ctx (Context): The context of the command.
        config_data (dict): The server's configuration data.

    Returns:
        bool
    """
    command_name = ctx.command.name
    prices_members_set = set(Prices.__members__)

    if command_name not in prices_members_set:
        await send_bot_embed(ctx, description=":no_entry_sign: Unknown points command.")
        return False
    
    if ctx.command.get_cooldown_retry_after(ctx):
        return False
    
    return True

async def retrieve_user_data(ctx: Context, cache_copy: bool) -> Optional[dict]:

    if cache_copy:
        data = await user_cache_retriever_copy(ctx.author.id)
    else:
        data = await user_cache_retriever(ctx.author.id)

    if not data:
        await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} is not registered in the bot. Try the command again.")
        await automatic_register(ctx.author)
        return None
    return data

async def verify_farm_command(ctx: Context, data: dict) -> bool:
    if await verify_if_farm_command(ctx.command):
        if not data['farm_data']:
            await send_bot_embed(ctx, description=":no_entry_sign: You don't have a farm. Type **!createfarm** to create one.")
            result = ctx.command.name == "createfarm"
            if not result:
                return False
    return True

async def verify_and_handle_points(ctx: Context, command_name: str, user_data: dict, config_data: dict, data: dict) -> bool:
    if await verify_points(command_name, user_data):
        result = await treat_exceptions(ctx, command_name, user_data, config_data, data)
        ctx.data = data
        if result:
            await update_user_points_in_voice(ctx, user_data, ctx.author)
            await update_user_farm_on_command(ctx, user_data, data, ctx.author)
        return result
    else:
        await send_bot_embed(ctx, description=":no_entry_sign: You don't have enough points to use this command.")
        return False