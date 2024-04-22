from enum import Enum
from db.userDB import Usuario
import discord
import inspect
from discord.ext import commands
from db.channelDB import ChannelDB

# This class is responsible for handling the prices of the commands.

class Prices(Enum):
    donatePoints = 0
    shop = 0
    salario = 0
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
    stealPoints = 350
    pardon = 500
    tirarRadinho = 500
    momentOfSilence = 500
    lowWageRole = 650
    implode = 750
    explode = 850
    kick = 850
    detonate = 880
    prision = 900
    lowClassRole = 920
    ban = 950
    god = 1000
    middleClassRole = 1200
    highClassRole = 1600
    nuke = 50000

def verificar_pontos(User: discord.Member, comando):
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
        await ctx.send("Insufficient amount of arguments.")
        return False
    elif len(command_args) > len(parameters) and varargs_index is None:
        await ctx.send("Excessive amount of arguments.")
        return False
    
    channel_list = ChannelDB.readAll() 
    channels = []
    for channel_dic in channel_list:
        channel = ctx.bot.get_channel(channel_dic["channel_id"])
        channels.append(channel)
    
    if ctx.channel not in channels:
        await ctx.send("You are not allowed to use commands in this channel.")
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
        except ValueError:
            await ctx.send("Invalid arguments.")
            return False
        except commands.MemberNotFound:
            await ctx.send("Member not found.")
            return False
        except commands.errors.BadArgument:
            await ctx.send("Invalid arguments.")
            return False

        if arg is not None and not isinstance(arg, param_type):
            await ctx.send("Invalid arguments.")
            return False
        if '*' not in str(param) and index not in optional_params_indices:
            i += 1


    new_points = Usuario.read(ctx.author.id)["points"] - Prices[comando].value
    Usuario.update(ctx.author.id, new_points, Usuario.read(ctx.author.id)["roles"])
    return True

def pricing():
    async def predicate(ctx):
        comando = ctx.command.name        
        if comando in Prices.__members__:
            if verificar_pontos(ctx.author, comando):
                return await treat_exceptions(ctx,comando)
            else:
                await ctx.send("You dont have enough points to use this command.")
                return False 
        else:
            await ctx.send("Unknown command.")
            return False
    return commands.check(predicate)
