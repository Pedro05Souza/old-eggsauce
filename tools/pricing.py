from enum import Enum
from db.userDB import Usuario
import discord
import inspect
from discord.ext import commands
from tools.embed import create_embed_without_title
from db.channelDB import ChannelDB
import time

# This class is responsible for handling the prices of the commands.
cooldown_tracker = {}
class Prices(Enum):
    points = 0
    leaderboard = 0
    cassino = 0
    speak = 0
    donatePoints = 0
    shop = 0
    salary = 0
    hungergames = 0
    balls = 50
    love = 75
    mog = 100
    mute = 150
    unmute = 150
    deafen = 150
    undeafen = 150
    disconnect = 175
    changeNickname = 200
    fling = 200
    purge = 250
    radinho = 325
    fish = 325
    stealPoints = 350
    pardon = 500
    emergency = 500
    tirarRadinho = 500
    momentOfSilence = 500
    lowWageRole = 650
    implode = 750
    explode = 850
    kick = 850
    detonate = 880
    shuffle = 900
    prison = 900
    lowClassRole = 920
    ban = 950
    god = 1000
    middleClassRole = 1200
    highClassRole = 1600
    nuke = 50000

def verify_points(User: discord.Member, comando):
    price = Prices[comando].value
    user_data = Usuario.read(User.id)
    if user_data:
        return user_data["points"] >= price
    else:
        return False

async def refund(User: discord.Member, ctx):
    try:
        price = Prices[ctx.command.name].value
        await Usuario.update(User.id, Usuario.read(User.id)["points"] + price, Usuario.read(User.id)["roles"])
    except Exception as e:
        print("Error encountered while refunding the money.", e)

async def treat_exceptions(ctx, comando):
        
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
        await create_embed_without_title(ctx, ":no_entry_sign: Insufficient amount of arguments.")
        return False
    elif len(command_args) > len(parameters) and varargs_index is None:
        await create_embed_without_title(ctx, ":no_entry_sign: Excessive amount of arguments.")
        return False
    
    channel_list = ChannelDB.readAll() 
    channels = []
    for channel_dic in channel_list:
        channel = ctx.bot.get_channel(channel_dic["channel_id"])
        channels.append(channel)
    
    if ctx.channel not in channels:
        await create_embed_without_title(ctx, ":no_entry_sign: This command can only be used in the commands channel.")
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
                await create_embed_without_title(ctx, f":no_entry_sign: Invalid argument type. Expected {param_type.__name__}.")
                return False
            if '*' not in str(param) and index not in optional_params_indices:
                i += 1
        except ValueError:
            await create_embed_without_title(ctx, ":no_entry_sign: Invalid arguments.")
            return False
        except commands.MemberNotFound:
            await create_embed_without_title(ctx, ":no_entry_sign: Member not found.")
            return False
        except commands.errors.BadArgument:
            await create_embed_without_title(ctx, ":no_entry_sign: Invalid arguments.")
            return False
        except commands.errors.MissingPermissions:
            await create_embed_without_title(ctx, ":no_entry_sign: insufficient permissions.")
            return False
        except commands.errors.BotMissingPermissions:
            await create_embed_without_title(ctx, ":no_entry_sign: insufficient permissions.")
            return False
        except commands.errors.CommandInvokeError:
            await create_embed_without_title(ctx, ":no_entry_sign: An error occurred while executing the command.")
            return False


    new_points = Usuario.read(ctx.author.id)["points"] - Prices[comando].value
    Usuario.update(ctx.author.id, new_points, Usuario.read(ctx.author.id)["roles"])
    return True

async def command_cooldown(ctx, command, cooldown_period):

    user_command_key = f"{ctx.author.id}_{command}"
    print(f"user_command_key: {user_command_key}")

    current_time = time.time()

    if user_command_key in cooldown_tracker:
        print(f"current_time: {current_time}")
        last_used_time = cooldown_tracker[user_command_key]
        if current_time - last_used_time < cooldown_period:
            print(f"cooldown period: {current_time - last_used_time}")
            return False

    cooldown_tracker[user_command_key] = current_time
    print(f"cooldown tracker: {cooldown_tracker}")
    return True


def pricing():
    async def predicate(ctx):
        command = ctx.command.name
        cooldown_period = 3        
        if command in Prices.__members__:
            if not await command_cooldown(ctx, command, cooldown_period):
                return False
            if verify_points(ctx.author, command):
                return await treat_exceptions(ctx,command)
            else:
                await create_embed_without_title(ctx, ":no_entry_sign: You do not have enough points to use this command.")
                return False 
        else:
            await create_embed_without_title(ctx, ":no_entry_sign: Unknown command.")
            return False
    return commands.check(predicate)
