from db.userDB import User
from discord.ext import commands
from tools.shared import send_bot_embed, make_embed_object, is_dev, user_cache_retriever, guild_cache_retriever
from tools.chickens.chickenshared import update_user_farm, update_player_corn
from tools.cache.init import cache_initiator
from tools.prices import Prices
import inspect
import discord
import logging
logger = logging.getLogger('botcore')
dev_mode = False
cooldown_tracker = {}

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

async def verify_points(comando, user_data):
    price = Prices[comando].value
    return user_data["points"] >= price

async def verify_if_farm_command(command):
    chicken_cogs = ["ChickenCore", "ChickenEvents", "ChickenView", "CornCommands", "PlayerMarket", "ChickenCombat"]
    cog = command.cog

    if cog.qualified_name in chicken_cogs:
        return True
    return False

async def verify_bank_command(command):
    bank_cogs = ["BankCommands"]
    cog = command.cog

    if cog.qualified_name in bank_cogs:
        return True
    return False

async def cooldown_user_tracker(user_id):
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

async def verify_correct_channel(ctx, config_data):
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
        if not await verify_correct_channel(ctx, config_data):
            return False
        if Prices[comando].value == 0:
            return True
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
    
    if not config_data['channel_id']:
        await send_bot_embed(ctx, description=":no_entry_sign: The bot has not been configured properly. Type **!setChannel** in the desired channel.")
        return False
    
    if not await verify_correct_channel(ctx, config_data):
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
        """Decorator predicate for the points commands. This is the core of the bot's interactive system."""
        global dev_mode

        if dev_mode and not is_dev(ctx):
            await send_bot_embed(ctx, description=":warning: The bot is currently in development mode.")
            result = False
            ctx.predicate_result = result
            return result

        result = False
        command_name = ctx.command.name
        command_ctx = ctx.command 
        config_data = await guild_cache_retriever(ctx.guild.id)
            
        if config_data['toggled_modules'] == "N":
            embed = await make_embed_object(description=":warning: The points commands are **disabled** in this server.")
            await ctx.author.send(embed=embed)
            result = False
            return result
            
        if command_name in Prices.__members__:
            if not ctx.command.get_cooldown_retry_after(ctx):
                data = await user_cache_retriever(ctx.author.id)
                all_keys = ["user_data", "farm_data", "bank_data"]

                if not all(key in data for key in all_keys): # cache properties can be nullable
                    await send_bot_embed(ctx, description=":warning: Your data is missing core properties and likely is not synchronized. Please try again later. This should be fixed automatically.")
                    data_copy = data.copy()
                    await cache_initiator.delete_from_user_cache(ctx.author.id)
                    raise MissingCacheProperty(f"The user cache is missing core properties and likely is not synchronized. Here are the following keys: {data_copy.keys()}")
                else:
                    user_data = data["user_data"]

                if not user_data:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} is not registered in the database. Type **!register** to register or join any voice channel to register automatically.")
                    result = False
                    ctx.predicate_result = result
                    return result
                
                if not await set_points_commands_submodules(ctx, config_data):
                    ctx.predicate_result = result
                    if not result:
                        return result
                    
                if await verify_if_farm_command(command_ctx):
                    if not data['farm_data']:
                        if await cooldown_user_tracker(ctx.author.id):
                            await send_bot_embed(ctx, description=":no_entry_sign: You don't have a farm. Type **!createfarm** to create one.")
                        result = command_name == "createfarm"
                        ctx.predicate_result = result
                        if not result:
                            return result
                    
                if await verify_bank_command(command_ctx):
                    if not data['bank_data']:
                        if await cooldown_user_tracker(ctx.author.id):
                            await send_bot_embed(ctx, description=":no_entry_sign: You don't have a bank account. Use any bank command and the bot will create one for you.")
                        result = command_name == "createbank"
                        ctx.predicate_result = result
                        return result
                
                if await verify_points(command_name, user_data):
                    result = await treat_exceptions(ctx, command_name, user_data, config_data, data)
                    ctx.data = data
                    ctx.predicate_result = result
                    if result and ctx.data['farm_data']:
                        ctx.data['farm_data'] = await update_user_farm(ctx, ctx.author, data)
                        ctx.data['farm_data']['corn'] = await update_player_corn(ctx.author, data['farm_data'])
                    return result
                else:
                    if await cooldown_user_tracker(ctx.author.id):
                        await send_bot_embed(ctx, description=":no_entry_sign: You don't have enough points to use this command.")
                    result = False
                    ctx.predicate_result = result
                    return result
                
            else:
                ctx.predicate_result = result
                return result
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: Unknown points command.")
            result = False
            ctx.predicate_result = result
            return result
    
    try:
        return commands.check(predicate)
    except Exception as e:
        logger.error(f"An error occurred while checking the predicate: {e}")
        return False
    
class MissingCacheProperty(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

