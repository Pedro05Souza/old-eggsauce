"""
This module contains the core of the bot's points system. It is responsible for handling the prices of the commands, cooldowns and checks.
"""

from db.userdb import User
from db.bankdb import Bank
from discord.ext import commands
from tools.shared import send_bot_embed, make_embed_object, user_cache_retriever, guild_cache_retriever, cooldown_user_tracker, format_number
from tools.chickens.chickenshared import update_user_farm, update_player_corn
from tools.prices import Prices
from discord.ext.commands import Context
from tools.listeners import on_user_transaction
import discord
import logging
logger = logging.getLogger('botcore')

# This class is responsible for handling the prices of the commands.

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
    if is_slash_command: # no need to check since slash commands always have the correct amount of arguments and types
        if not await verify_correct_channel(ctx, config_data):
            return False
        if Prices[command].value == 0:
            return True
        new_points = user_data["points"] - Prices[command].value
        data["user_data"]["points"] = new_points
        User.update_points(ctx.author.id, new_points)
        await on_user_transaction(ctx, Prices[command].value, 1)
        return True
    if not await verify_correct_channel(ctx, config_data):
        return False
    if Prices[command].value == 0:
        return True
    new_points = user_data['points'] - Prices[command].value
    data["user_data"]['points'] = new_points
    User.update_points(ctx.author.id, new_points)
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
    user_data = user_data["user_data"]
    if user_data:
        return
    elif user.bot:
        return
    else:
        User.create(user.id, 0)
        Bank.create(user.id, 0, 1)
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

async def send_away_user_rewards(ctx: Context, salary_gained: int, total_profit: int, corn_produced: int) -> None:
    """
    Sends a message to the user to see how many he gained during his time away.

    Args:
        ctx (Context): The context of the command.
        salary_gained (int): The amount of salary the user gained.
        total_profit (int): The total profit the user gained.
        corn_produced (int): The amount of corn the user produced.

    Returns:
        None
    """
    description = f":tada: **{ctx.author.display_name}** While you were away, you gained:\n"

    if salary_gained > 0:
        description += f":money_with_wings: **{await format_number(salary_gained)}** eggbux from your salary.\n"
    if total_profit > 0:
        description += f":wood: **{await format_number(total_profit)}** eggbux from your farm.\n"
    if corn_produced > 0:
        description += f":corn: **{await format_number(corn_produced)}** corn from your farm."
    if salary_gained > 0 or total_profit > 0 or corn_produced > 0:
        await send_bot_embed(ctx, description=description)

def pricing() -> dict:
    """
    Decorator predicate for the points commands. This is the core of the bot's interactive system.
    Always use this when making a points command.
    """
    async def predicate(ctx: Context) -> bool:
        config_data = await guild_cache_retriever(ctx.guild.id)

        if not await check_server_requirements(ctx, config_data):
            return False

        command_name = ctx.command.name
        command_ctx = ctx.command 
        prices_members_set = set(Prices.__members__)
            
        if command_name in prices_members_set:
            
            if not ctx.command.get_cooldown_retry_after(ctx):

                data = await user_cache_retriever(ctx.author.id)
                user_data = data['user_data']

                if not user_data:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} is not registered in the bot. Try the command again.")
                    await automatic_register(ctx.author)
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
                    
                if await verify_points(command_name, user_data):
                    result = await treat_exceptions(ctx, command_name, user_data, config_data, data)
                    ctx.data = data
                    if result:
                        points_manager = ctx.bot.get_cog("PointsManager")
                        ctx.data['user_data'], salary_gained = await points_manager.update_user_points(ctx.author, data)
                        if ctx.data['farm_data']:
                            ctx.data['farm_data'], total_profit = await update_user_farm(ctx, ctx.author, data)
                            corn_to_cache, corn_produced = await update_player_corn(ctx.author, data['farm_data'])
                            ctx.data['farm_data']['corn'] = corn_to_cache
                            await send_away_user_rewards(ctx, salary_gained, total_profit, corn_produced)
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