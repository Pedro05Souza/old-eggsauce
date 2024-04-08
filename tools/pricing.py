from enum import Enum
from db.Usuario import Usuario
import discord
from discord.ext import commands

class Prices(Enum):
    BALLS = 50
    MOGGED = 100
    MUTE = 150
    CHANGENICKNAME = 200
    PURGE = 250
    KICK = 350
    BAN = 450
    PARDON = 500
    MOMENTODESILENCIO = 500
    IMPLODE = 750
    EXPLODE = 850
    GOD = 1000
    ROUBARPONTOS = 500

def verificar_pontos(User: discord.Member, comando):
    price = Prices[comando.upper()].value
    if Usuario.read(User.id):
        return Usuario.read(User.id)["points"] >= price
    else:
        return False


def pricing():
    async def predicate(ctx):
        comando = ctx.command.name.upper()
        if comando in Prices.__members__:
            if verificar_pontos(ctx.author, comando):
                new_points = Usuario.read(ctx.author.id)["points"] - Prices[comando.upper()].value
                Usuario.update(ctx.author.id, new_points)
                return True
            else:
                await ctx.send("Você não tem créditos suficientes para executar este comando.")
                return False 
        else:
            await ctx.send("Comando não identificado.")
            return False
    return commands.check(predicate)
