from discord.ext import commands
import discord
from db.Usuario import Usuario
import os
from dotenv import load_dotenv

class ModCommands(commands.Cog):
    
    def __init__(self, bot):
        load_dotenv()
        self.devs = os.getenv("DEVS").split(",")
        self.bot = bot

    @commands.command()
    async def addPontos(self, ctx, amount: int, User: discord.Member = None):
        if User is None:
            User = ctx.author
            if str(User.id) in self.devs:
                Usuario.update(User.id, Usuario.read(User.id)["points"] + amount)
                await ctx.send(f"{User.mention} recebeu {amount} eggbux")
            else:
                await ctx.send("Você não tem permissão para fazer isso")
        else:
            if Usuario.read(User.id):
                if str(ctx.author.id) in self.devs:
                    Usuario.update(User.id, Usuario.read(User.id)["points"] + amount)
                    await ctx.send(f"{User.mention} recebeu {amount} eggbux")
                else:
                    await ctx.send("Você não tem permissão para fazer isso")
            else:
                await ctx.send("Usuario não registrado no Banco de Dados!")

    @commands.command()
    async def removePontos(self, ctx, amount: int, User: discord.Member = None):
        if User is None:
            User = ctx.author
            if str(User.id) in self.devs:
                Usuario.update(User.id, Usuario.read(User.id)["points"] - amount)
                await ctx.send(f"{User.mention} perdeu {amount} eggbux")
            else:
                await ctx.send("Você não tem permissão para fazer isso")
        else:
            if Usuario.read(User.id):
                if str(ctx.author.id) in self.devs:
                    Usuario.update(User.id, Usuario.read(User.id)["points"] - amount)
                    await ctx.send(f"{User.mention} perdeu {amount} eggbux")
                else:
                    await ctx.send("Você não tem permissão para fazer isso")
            else:
                await ctx.send("Você não tem permissão para fazer isso")

    @commands.command()
    async def deleteDB(self, ctx,  User: discord.Member):
        User = User.id
        if Usuario.read(User):
            if str(ctx.author.id) in self.devs:
                Usuario.delete(User)
                await ctx.send(f"{User} foi deletado do Banco de Dados")
            else:
                await ctx.send("Você não tem permissão para fazer isso")
        else:
            await ctx.send(f"{User} não está registrado no Banco de Dados!")
       

async def setup(bot):
     await bot.add_cog(ModCommands(bot))