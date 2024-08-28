"""
This module contains the core of the bot's points system. It is responsible for handling the prices of the commands, cooldowns and checks.
"""

from db.userDB import User
from discord.ext import commands
from tools.shared import send_bot_embed, make_embed_object, user_cache_retriever, guild_cache_retriever, cooldown_user_tracker
from tools.chickens.chickenshared import update_user_farm, update_player_corn
from tools.settings import user_salary_drop
from tools.prices import Prices
from discord.ext.commands import Context
from tools.listeners import on_user_transaction
import discord
import logging
import math
import time
logger = logging.getLogger('botcore')
join_time = {}
init_time = math.ceil(time.time())

# This class is responsible for handling the prices of the commands.

async def get_points_commands_submodules(ctx: Context, config_data: dict) -> bool:
    """
    Verify if the current command's cog is enabled in the server.
    """
    active_module = config_data['toggled_modules']
    shared_cogs = ["BaseCommands", "BankCommands"]
    friendly_cogs = ["ChickenCore", "ChickenEvents", "ChickenView", "InteractiveCommands", "AICommands", "CornCommands", "PlayerMarket", "ChickenCombat"]
    hostile_cog = ["HostileCommands"]
    destructive_cog = ["DestructiveCommands"]
    module_cogs = {
        "F": set(friendly_cogs + shared_cogs + destructive_cog) if active_module == "TD" else set(friendly_cogs + shared_cogs),
        "H": set(hostile_cog + shared_cogs) if active_module == "TD" else set(hostile_cog + shared_cogs),
    }
    if active_module == "T" or active_module == "TD":
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
    Verify if the user has enough points to use the command.
    """
    price = Prices[command].value
    return user_data["points"] >= price

async def verify_if_farm_command(command: commands.Command) -> bool:
    """
    Verify if the command belongs to a farm-related cog.
    """
    chicken_cogs = {"ChickenCore", "ChickenEvents", "ChickenView", "CornCommands", "PlayerMarket", "ChickenCombat"}
    cog = command.cog

    if cog.qualified_name in chicken_cogs:
        return True
    return False

async def verify_bank_command(command: commands.Command) -> bool:
    """
    Verify if the command belongs to a bank-related cog.
    """
    bank_cogs = {"BankCommands"} 
    cog = command.cog

    if cog.qualified_name in bank_cogs:
        return True
    return False

async def verify_correct_channel(ctx: Context, config_data: dict) -> bool:
        """
        Verify if the command is being used in the correct channel.
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
    Refund the user if the command fails.
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
    """
    is_slash_command = hasattr(ctx, "interaction") and ctx.interaction is not None
    if is_slash_command: # no need to check since slash commands always have the correct amount of arguments and types
        if not await verify_correct_channel(ctx, config_data):
            return False
        if Prices[command].value == 0:
            return True
        new_points = user_data["points"] - Prices[command].value
        data["user_data"]["points"] = new_points
        User.update_points(ctx.author.id, new_points)
        await on_user_transaction(ctx.author.id, Prices[command].value, 1)
        return True
    if not await verify_correct_channel(ctx, config_data):
        return False
    if Prices[command].value == 0:
        return True
    new_points = user_data['points'] - Prices[command].value
    data["user_data"]['points'] = new_points
    User.update_points(ctx.author.id, new_points)
    await on_user_transaction(ctx.author.id, Prices[command].value, 1)
    return True

async def handle_exception(ctx: Context, description: str) -> None:
    """
    Handle the exception that may occur while executing the command.
    """
    if await cooldown_user_tracker(ctx.author.id):
        await send_bot_embed(ctx, description=description)
        await refund(ctx.author, ctx)

async def update_user_points(user: discord.Member, data: dict) -> dict:
    """Updates the user's points when the command is called."""
    user_data = data['user_data']
    if user_data:
        points = await update_points(user)
        if points:
            user_data['points'] = points
        else:
            return user_data
        last_title_drop = time.time() - user_data["salary_time"]
        hours_passed = min(last_title_drop // user_salary_drop, 12)
        hours_passed = int(hours_passed)
        salary = await salary_role(user_data)
        if hours_passed > 0 and user_data["roles"] != "":
            user_data['points'] += salary * hours_passed
            User.update_salary_time(user.id)
            logger.info(f"{user.display_name} has received {salary * hours_passed} eggbux from their title.")
        User.update_points(user.id, user_data['points'])
        return user_data
    
async def update_points(user: discord.Member) -> int:
        """Updates the points of the user every 10 seconds."""
        userId = user.id
        if not user.voice and userId in join_time.keys():
            total_points = await add_points(join_time[userId], userId)
            join_time.pop(userId)
            return total_points
        
        if userId in join_time.keys():
            total_points = await add_points(join_time[userId], userId)
            join_time[userId] = math.ceil(time.time())
            return total_points
        
        if userId not in join_time.keys() and user.voice:
           total_points = await add_points(init_time, userId)
           join_time[userId] = math.ceil(time.time())
           return total_points

async def add_points(type: int, user_id: int) -> int:
    add_points = (math.ceil(time.time()) - type) // 10
    user_data = await user_cache_retriever(user_id)
    user_data = user_data["user_data"]
    total_points = user_data["points"] + add_points
    return total_points

async def salary_role(user_data: dict) -> int:
    """Returns the salary of a user based on their roles."""
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

async def count_points(user: discord.Member) -> None:
    """Counts the points of the user every time he enters a voice channel."""
    userId = user.id
    if user.bot:
        return
    if userId not in join_time.keys():
        join_time[userId] = math.ceil(time.time())
    else:
        return

async def automatic_register(user: discord.Member) -> None:
    """Automatically registers the user in the database."""
    if User.read(user.id) and user.bot:
        return
    else:
        User.create(user.id, 0)
        logger.info(f"{user.display_name} has been registered.")

async def verify_if_server_has_modules(ctx: Context, config_data: dict) -> bool:
    modules = config_data.get('toggled_modules', None)	
    if not modules:
        await send_bot_embed(ctx, description=":warning: The modules aren't configured in this server. Type **!setModule** to configure them. To see the available modules type **!modules**.")
        return False
    return True

async def verify_if_server_has_channel(ctx: Context, config_data: dict) -> bool:
    if not config_data['channel_id']:
        await send_bot_embed(ctx, description=":warning: The commands channel isn't configured in this server. Type **!setChannel** in the desired channel.")
        return False
    return True

def pricing() -> dict:
    """
    Decorator predicate for the points commands. This is the core of the bot's interactive system.
    Always use this when making a points command.
    """
    async def predicate(ctx: Context) -> bool:
        config_data = await guild_cache_retriever(ctx.guild.id)

        if not await verify_if_server_has_modules(ctx, config_data) or not await verify_if_server_has_channel(ctx, config_data):
            return False
        
        if config_data['toggled_modules'] == "N":
            embed = await make_embed_object(description=":warning: The points commands are **disabled** in this server.")
            await ctx.author.send(embed=embed)
            return False
        
        command_name = ctx.command.name
        command_ctx = ctx.command 
        prices_members_set = set(Prices.__members__)
            
        if command_name in prices_members_set:
            
            if not ctx.command.get_cooldown_retry_after(ctx):
                data = await user_cache_retriever(ctx.author.id)
                user_data = data['user_data']

                if not user_data:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} is not registered in the database. Type **!register** to register or join any voice channel to register automatically.")
                    return False

                if not await get_points_commands_submodules(ctx, config_data):
                    return False
                    
                if await verify_if_farm_command(command_ctx):
                    if not data['farm_data']:
                        if await cooldown_user_tracker(ctx.author.id):
                            await send_bot_embed(ctx, description=":no_entry_sign: You don't have a farm. Type **!createfarm** to create one.")
                        result = command_name == "createfarm"
                        if not result:
                            return False
                    
                if await verify_bank_command(command_ctx):
                    if not data['bank_data']:
                        if await cooldown_user_tracker(ctx.author.id):
                            await send_bot_embed(ctx, description=":no_entry_sign: You don't have a bank account. Use any bank command and the bot will create one for you.")
                        result = command_name == "createbank"
                        ctx.predicate_result = result
                        if not result:
                            return False
                
                if await verify_points(command_name, user_data):
                    result = await treat_exceptions(ctx, command_name, user_data, config_data, data)
                    ctx.data = data
                    if result: 
                        ctx.data['user_data'] = await update_user_points(ctx.author, data)
                        if ctx.data['farm_data']:
                            ctx.data['farm_data'] = await update_user_farm(ctx, ctx.author, data)
                            ctx.data['farm_data']['corn'] = await update_player_corn(ctx.author, data['farm_data'])
                    return result
                
                else:
                    if await cooldown_user_tracker(ctx.author.id):
                        await send_bot_embed(ctx, description=":no_entry_sign: You don't have enough points to use this command.")
                    return False
            else:
                return False
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: Unknown points command.")
            return False
    return commands.check(predicate)

@commands.Cog.listener()
async def on_voice_state_update(user: discord.Member, before, after):
    """Listens to the voice state update event."""
    guild_data = await guild_cache_retriever(user.guild.id)
    if not guild_data['toggled_modules'] == "N":
        user_data = await user_cache_retriever(user.id)
        user_data = user_data["user_data"]
        if user.bot:
            return
        if user_data and before.channel is None and after.channel is not None:
            await count_points(user)
        elif not user_data and before.channel is None and after.channel is not None:
            await automatic_register(user)
            await count_points(user)
        elif user_data and before.channel is not None and after.channel is None:
            await update_points(user)
        elif not user_data and before.channel is not None and after.channel is None:
            await automatic_register(user)
            await update_points(user)
