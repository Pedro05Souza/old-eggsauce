from enum import Enum
from db.Usuario import Usuario
import discord
from discord.ext import commands

class Prices(Enum):
    balls = 50
    mog = 100
    mute = 150
    changeNickname = 200
    purge = 250
    kick = 350
    ban = 450
    pardon = 500
    momentoDeSilencio = 500
    implode = 750
    explode = 850
    god = 1000
    roubarPontos = 500

def verificar_pontos(User: discord.Member, comando):
    price = Prices[comando].value
    if Usuario.read(User.id):
        return Usuario.read(User.id)["points"] >= price
    else:
        return False


def pricing():
    async def predicate(ctx):
        comando = ctx.command.name
        if comando in Prices.__members__:
            if verificar_pontos(ctx.author, comando):
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