from enum import Enum
from db.UserDB import Usuario
import discord
import inspect
from discord.ext import commands

class Prices(Enum):
    doarPontos = 0
    balls = 50
    mog = 100
    mute = 150
    unmute = 150
    deafen = 150
    undeafen = 150
    disconnect = 175
    mudarApelido = 200
    purge = 250
    radinho = 325
    roubarPontos = 350
    perdoar = 500
    tirarRadinho = 500
    momentoDeSilencio = 500
    #giveRole3 = 500
    implode = 750
    explode = 850
    kick = 850
    ban = 950
    god = 1000

def verificar_pontos(User: discord.Member, comando):
    price = Prices[comando].value
    if Usuario.read(User.id):
        return Usuario.read(User.id)["points"] >= price
    else:
        return False

async def refund(User: discord.Member, ctx):
    try:
        price = Prices[ctx.command.name].value
        await Usuario.update(User.id, Usuario.read(User.id)["points"] + price)
    except Exception as e:
        print("Erro ao devolver os pontos", e)

def pricing():
    async def predicate(ctx):
        comando = ctx.command.name
        
        message_content = ctx.message.content
        command_args = message_content.split()[1:]  
        
        if comando in Prices.__members__:
            if verificar_pontos(ctx.author, comando):
                command_func = ctx.command.callback
                parameters = list(inspect.signature(command_func).parameters.values())
                
                if list(parameters)[0].name == 'self':
                    parameters = parameters[1:]

                if list(parameters)[0].name == 'ctx':
                    parameters = parameters[1:]

                if len(command_args) != len(parameters):
                    await ctx.send("Número incorreto de argumentos.")
                    return False

                for arg, param in zip(command_args, parameters):
                    param_type = param.annotation
                    if param_type is inspect.Parameter.empty:
                        continue
                    try:
                        if param_type == discord.Member:
                            arg = await commands.MemberConverter().convert(ctx, arg)
                        else:
                            arg = param_type(arg)
                    except ValueError:
                        await ctx.send("Argumentos inválidos.")
                        return False
                    except commands.MemberNotFound:
                        await ctx.send("Membro não encontrado.")
                        return False
                    except commands.BadArgument:
                        await ctx.send("Argumentos inválidos.")
                        return False
                        
                    if not isinstance(arg, param_type):
                        await ctx.send("Argumentos inválidos.")
                        return False

                        
                new_points = Usuario.read(ctx.author.id)["points"] - Prices[comando].value
                Usuario.update(ctx.author.id, new_points)
                return True
            else:
                await ctx.send("Você não tem créditos suficientes para executar este comando.")
                return False 
        else:
            await ctx.send("Comando não identificado.")
            return False
    return commands.check(predicate)
