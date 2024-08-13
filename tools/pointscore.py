from db.userDB import User
from discord.ext import commands
from tools.shared import send_bot_embed, make_embed_object, is_dev, user_cache_retriever, guild_cache_retriever
from tools.prices import Prices
from tools.cache.init import cache_initiator
import inspect
import discord
import logging
logger = logging.getLogger('botcore')
cooldown_tracker = {}
dev_mode = False

# This class is responsible for handling the prices of the commands.

async def set_points_commands_submodules(ctx, config_data):
    active_module = config_data['toggled_modules']
    if not active_module:
        await send_bot_embed(ctx, description=":warning: The modules aren't configured in this server. Type **!setModule** to configure them. To see the available modules type **!modules**.")
        return False
    shared_cogs = ["PointsConfig", "BankCommands"]
    friendly_cogs = ["FriendlyCommands", "ChickenCore", "ChickenEvents", "ChickenView", "InteractiveCommands", "AICommands", "CornCommands", "PlayerMarket", "ChickenCombat"]
    hostile_cog = ["HostileCommands"]
    module_cogs = {
        "F": friendly_cogs + shared_cogs,
        "H": hostile_cog + shared_cogs,
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
        await send_bot_embed(ctx, description=":warning: The module is not enabled in this server.")
        return False

def verify_points(comando, user_data):
    price = Prices[comando].value
    return user_data["points"] >= price

async def refund(user: discord.Member, ctx):
    try:
        price = Prices[ctx.command.name].value
        user_data = await user_cache_retriever(user.id)
        user_data = user_data["user_data"]
        await User.update_points(user.id, user_data["points"] + price)
    except Exception as e:
        logger.error(f"An error occurred while refunding the user: {e}")

async def treat_exceptions(ctx, comando, user_data, config_data, data):
    is_slash_command = hasattr(ctx, "interaction") and ctx.interaction is not None
    if is_slash_command:
        new_points = user_data["points"] - Prices[comando].value
        data["user_data"]["points"] = new_points
        User.update_points(ctx.author.id, new_points)
        return True
    
    message_content = ctx.message.content
    command_args = message_content.split()[1:] 
        
    command_func = ctx.command.callback
    parameters = list(inspect.signature(command_func).parameters.values())
    parameters = parameters[2:]
    
    optional_params_indices = [i for i, param in enumerate(parameters) if param.default != inspect.Parameter.empty]
    varargs_index = next((i for i, param in enumerate(parameters) if param.kind == param.VAR_POSITIONAL), None)
    
    expected_args_count = len(parameters) - len(optional_params_indices)
    if varargs_index is not None:
        expected_args_count -= 1

    if len(command_args) < expected_args_count:
        await send_bot_embed(ctx, description=":no_entry_sign: Insufficient amount of arguments.")
        return False
    
    elif len(command_args) > len(parameters) and varargs_index is None:
        await send_bot_embed(ctx, description=":no_entry_sign: Excessive amount of arguments.")
        return False
    
    channel = config_data
    if not channel['channel_id']:
        await send_bot_embed(ctx, description=":no_entry_sign: The bot has not been configured properly. Type **!setChannel** in the desired channel.")
        return False
    
    if ctx.channel.id != channel['channel_id']:
        commands_object = ctx.bot.get_channel(channel['channel_id'])
        channel_mention = commands_object.mention
        embed = await make_embed_object(title=":no_entry_sign: Invalid channel", description=f"Please use the commands channel: **{channel_mention}**")
        await ctx.author.send(embed=embed)
        return False
    
    i = 0
    for index, param in enumerate(parameters):
        param_type = param.annotation
        if param_type is inspect.Parameter.empty:
            continue
        try:
            if varargs_index is not None and index >= varargs_index:
                arg = ' '.join(command_args[i:])
                command_args = command_args[:i]
            else:
                arg = command_args[i] if i < len(command_args) else param.default 
            if arg is not None: 
                if param_type == discord.Member:
                    arg = await commands.MemberConverter().convert(ctx, arg)
                else:
                    arg = param_type(arg)
            if arg is not None and not isinstance(arg, param_type):
                await send_bot_embed(ctx, description=f":no_entry_sign: Invalid argument type. Expected {param_type.__name__}.")
                return False
            if '*' not in str(param) and index not in optional_params_indices:
                i += 1
        except ValueError:
            await send_bot_embed(ctx, description=":no_entry_sign: Invalid arguments.")
            return False
        except commands.MemberNotFound:
            await send_bot_embed(ctx, description=":no_entry_sign: Member not found.")
            return False
        except commands.errors.BadArgument:
            await send_bot_embed(ctx, description=":no_entry_sign: Invalid arguments.")
            return False
        except commands.errors.CommandInvokeError:
            await send_bot_embed(ctx, description=":no_entry_sign: An error occurred while executing the command.")
            return False
    if Prices[comando].value == 0:
        return True
    new_points = user_data['points'] - Prices[comando].value
    data["user_data"]['points'] = new_points
    User.update_points(ctx.author.id, new_points)
    return True

def pricing():
    async def predicate(ctx):
        """Check if the user is able to use any of the points commands."""
        global dev_mode
        command = ctx.command.name 
        result = True
        ctx.predicate_result = result
        config_data = await guild_cache_retriever(ctx.guild.id)
        if dev_mode:
            if not is_dev(ctx):
                await send_bot_embed(ctx, description=":warning: The bot is currently in development mode.")
                result = False
                return result
            
        if config_data['toggled_modules'] == "N":
            embed = await make_embed_object(description=":warning: The points commands are **disabled** in this server.")
            await ctx.author.send(embed=embed)
            result = False
            return result
            
        if command in Prices.__members__:
            data = await user_cache_retriever(ctx.author.id)
            all_keys = ["user_data", "farm_data", "bank_data"]
            if not data:
                await send_bot_embed(ctx, description=":no_entry_sign: Your data has not been synchronized. Please try again later.")
                raise CacheNotFound(f"The user cache is not found. {data}", ctx.author.id)
            if not all(key in data for key in all_keys): # cache properties can be nullable
                await send_bot_embed(ctx, description=":no_entry_sign: Your data is not synchronized. Please try again later.")
                raise MissingCacheProperty(f"The user cache is missing properties and likely is not synchronized. {data}", ctx.author.id)
            else:
                user_data = data["user_data"]

            if not user_data:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} is not registered in the database. Type **!register** to register or join any voice channel to register automatically.")
                result = False
                ctx.predicate_result = result
                return result
            
            if not await set_points_commands_submodules(ctx, config_data):
                result = False
                ctx.predicate_result = result
                return result
            
            if verify_points(command, user_data):
                result = await treat_exceptions(ctx,command, user_data, config_data, data)
                ctx.data = data
                ctx.predicate_result = result
                return result
            
            else:
                await send_bot_embed(ctx, description=":no_entry_sign: You do not have enough points to use this command.")
                result = False
                ctx.predicate_result = result
                return result
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: Unknown points command.")
            result = False
        return result
    
    try:
        return commands.check(predicate)
    except Exception as e:
        logger.error(f"An error occurred while checking the predicate: {e}")
        return False
    

class MissingCacheProperty(Exception):
    def __init__(self, message, user_id):
        self.message = message
        cache_initiator.delete_from_user_cache(user_id)
        super().__init__(self.message)

class CacheNotFound(Exception):
    def __init__(self, message, user_id):
        self.message = message
        cache_initiator.delete_from_user_cache(user_id)
        super().__init__(self.message)

