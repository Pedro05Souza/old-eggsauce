from discord.ext import commands
import discord
from db.UserDB import Usuario
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
                Usuario.update(User.id, Usuario.read(User.id)["points"] + amount, Usuario.read(User.id)["roles"])
                await ctx.send(f"{User.mention} recebeu {amount} eggbux")
            else:
                await ctx.send("Você não tem permissão para fazer isso")
        else:
            if Usuario.read(User.id):
                if str(ctx.author.id) in self.devs:
                    Usuario.update(User.id, Usuario.read(User.id)["points"] + amount, Usuario.read(User.id)["roles"])
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
                Usuario.update(User.id, Usuario.read(User.id)["points"] - amount, Usuario.read(User.id)["roles"])
                await ctx.send(f"{User.mention} perdeu {amount} eggbux")
            else:
                await ctx.send("Você não tem permissão para fazer isso")
        else:
            if Usuario.read(User.id):
                if str(ctx.author.id) in self.devs:
                    Usuario.update(User.id, Usuario.read(User.id)["points"] - amount, Usuario.read(User.id)["roles"])
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


    @commands.command()
    async def removerCargo(self, ctx ,User:discord.Member, role: str):
        possibleRoles = {"T": "trabalhador assalariado", "B" : "Plebeu", "M" : "pobretão com um gol 1.0", "A" : "magnata"}
        if str(ctx.author.id) in self.devs:
            user_data = Usuario.read(User.id)
            if user_data:
                if len(user_data["roles"]) > 0 and role in possibleRoles.keys():
                    if role in user_data["roles"]:
                        roles = Usuario.read(User.id)["roles"]
                        roles = roles.replace(role, "")
                        roleRemove = discord.utils.get(ctx.guild.roles, name=possibleRoles[role])
                        if roleRemove:
                            await User.remove_roles(roleRemove)
                            Usuario.update(User.id, Usuario.read(User.id)["points"], roles)
                            await ctx.send(f"{User.mention} perdeu o cargo {possibleRoles[role]}")
                    else:
                        await ctx.send(f"{User.mention} não tem o cargo {role}")
            else:
                await ctx.send(f"{User.mention} não está registrado no Banco de Dados!")
        else:
            await ctx.send("Você não tem permissão para fazer isso")


       

async def setup(bot):
     await bot.add_cog(ModCommands(bot))