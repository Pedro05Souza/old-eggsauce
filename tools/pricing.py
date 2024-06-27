from enum import Enum
from multiprocessing.context import BaseContext
from db.userDB import Usuario
import discord
from db.botConfigDB import BotConfig
import inspect
from discord.ext import commands
from tools.embed import create_embed_without_title, make_embed_object
import time

# This class is responsible for handling the prices of the commands.
cooldown_tracker = {}
class Prices(Enum):
    points = 0
    leaderboard = 0
    casino = 0
    title = 0
    market = 0
    createfarm = 0
    farmprofit = 0
    sellchicken = 0
    farm = 0
    renamefarm = 0
    checkTitle = 0
    withdraw = 0
    balance = 0
    deposit = 0
    donatepoints = 0
    buytitles = 0
    shop = 0
    salary = 0
    hungergames = 0
    tradechicken = 0
    renamechicken = 0
    balls = 50
    feedchicken = 0
    increaserarity = 0
    feedallchickens = 0
    love = 75
    mog = 100
    mute = 150
    unmute = 150
    deafen = 150
    undeafen = 150
    disconnect = 175
    changenickname = 200
    fling = 200
    purge = 250
    radio = 325
    fish = 325
    stealpoints = 350
    pardon = 500
    emergency = 500
    tirarRadinho = 500
    momentofsilence = 500
    implode = 750
    explode = 850
    kick = 850
    detonate = 880
    shuffle = 900
    prison = 900
    ban = 950
    god = 1000
    nuke = 50000

async def set_points_commands_submodules(ctx, command):
    if not BotConfig.read(ctx.guild.id)['toggled_modules']:
        await create_embed_without_title(ctx, ":warning: The modules aren't configured in this server. Type **!setModule** to configure them. To see the available modules type **!modules**.")
        return False
    activate_module = BotConfig.read(ctx.guild.id)['toggled_modules']
    shared_cogs = ["PointsConfig", "BankCommands"]
    friendly_cogs = ["FriendlyCommands", "ChickenCommands", "InteractiveCommands", "AICommands"]
    hostile_cog = ["HostileCommands"]
    if activate_module == "F":
        friendly_cogs.extend(shared_cogs)
        for cog_name in friendly_cogs or shared_cogs:
            cog = ctx.bot.get_cog(cog_name)
            if cog:
                for cmd in cog.get_commands():
                    if cmd.name == command:
                        return True            
        await create_embed_without_title(ctx, ":no_entry_sign: The command is not available in the current module.")
        return False
    elif activate_module == "H":
        hostile_cog.extend(shared_cogs)
        for cog_name in hostile_cog:
            cog = ctx.bot.get_cog(cog_name)
            if cog:
                for cmd in cog.get_commands():
                    if cmd.name == command:
                        return True
                    
        await create_embed_without_title(ctx, ":no_entry_sign: The command is not available in the current module.")
        return False
    elif activate_module == "T":
        return True
    else:
        await create_embed_without_title(ctx, ":no_entry_sign: The command is not available in the current module.")
        return False

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
    is_slash_command = hasattr(ctx, "interaction") and ctx.interaction is not None
    if is_slash_command:
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
        await create_embed_without_title(ctx, ":no_entry_sign: Insufficient amount of arguments.")
        return False
    elif len(command_args) > len(parameters) and varargs_index is None:
        await create_embed_without_title(ctx, ":no_entry_sign: Excessive amount of arguments.")
        return False
    
    channel = BotConfig.read(ctx.guild.id)
    if not channel['channel_id']:
        await create_embed_without_title(ctx, ":no_entry_sign: The bot has not been configured properly. Type **!setChannel** in the desired channel.")
        return False
    if ctx.channel.id != channel['channel_id']:
        commands_object = ctx.bot.get_channel(BotConfig.read(ctx.guild.id)['channel_id'])
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
        except commands.errors.CommandInvokeError:
            await create_embed_without_title(ctx, ":no_entry_sign: An error occurred while executing the command.")
            return False


    new_points = Usuario.read(ctx.author.id)["points"] - Prices[comando].value
    Usuario.update(ctx.author.id, new_points, Usuario.read(ctx.author.id)["roles"])
    return True

async def command_cooldown(ctx, command, cooldown_period):

    user_command_key = f"{ctx.author.id}_{command}"

    current_time = time.time()

    if user_command_key in cooldown_tracker:
        last_used_time = cooldown_tracker[user_command_key]
        if current_time - last_used_time < cooldown_period:
            return False

    cooldown_tracker[user_command_key] = current_time
    return True


def pricing():
    async def predicate(ctx):
        """Check if the user has enough points to use the command."""
        command = ctx.command.name 
        cooldown_period = 3 
        result = True
        if BotConfig.read(ctx.guild.id)['toggled_modules'] == "N":
            embed = await make_embed_object(description=":warning: The points commands are **disabled** in this server.")
            await ctx.author.send(embed=embed)
            result = False
            return result    
        if command in Prices.__members__:
            if not Usuario.read(ctx.author.id):
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} is not registered in the database. Type **!register** to register or join any voice channel to register automatically.")
                result = False
                return result
            if not await command_cooldown(ctx, command, cooldown_period):
                result = False
                return result
            if not await set_points_commands_submodules(ctx, command):
                result = False
                return result
            if verify_points(ctx.author, command):
                result = await treat_exceptions(ctx,command)
                return result
            if not await command_cooldown(ctx, "points", cooldown_period):
                result = False
                return result 
            else:
                await create_embed_without_title(ctx, ":no_entry_sign: You do not have enough points to use this command.")
                result = False
                return result
        else:
            await create_embed_without_title(ctx, ":no_entry_sign: Unknown points command.")
        ctx.predicate_result = result
        return result
    try:
        return commands.check(predicate)
    except Exception as e:
        print("Error encountered while checking the predicate.", e)
        return False
