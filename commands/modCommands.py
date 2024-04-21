import os
import discord
from discord.ext import commands
from db.UserDB import Usuario
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
            
    @commands.command()
    async def removerTodosCargos(self, ctx, User: discord.Member):
        if str(ctx.author.id) in self.devs:
            user_data = Usuario.read(User.id)
            if user_data:
                roles = user_data["roles"]
                for role in roles:
                    roleRemove = discord.utils.get(ctx.guild.roles, name=role)
                    if roleRemove:
                        await User.remove_roles(roleRemove)
                Usuario.update(User.id, Usuario.read(User.id)["points"], "")
                await ctx.send(f"{User.mention} perdeu todos os cargos")
            else:
                await ctx.send(f"{User.mention} não está registrado no Banco de Dados!")
        else:
            await ctx.send("Você não tem permissão para fazer isso")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            roles = ""
            role_order = ["trabalhador assalariado", "Plebeu", "pobretão com um gol 1.0", "magnata"]
            role_letters = {"trabalhador assalariado": "T", "Plebeu": "B", "pobretão com um gol 1.0": "M", "magnata": "A"}
            lost_role = None
            for role in before.roles:
                if role not in after.roles:
                    lost_role = role
                    break
            if lost_role:
                if lost_role.name in role_order:
                    Usuario.update(after.id, Usuario.read(after.id)["points"], Usuario.read(after.id)["roles"].replace(role_letters[lost_role.name], ""))
                    print("rola removida: " + lost_role.name)
                for role_name in role_order[role_order.index(lost_role.name):]:
                    role = discord.utils.get(after.guild.roles, name=role_name)
                    if role in after.roles:
                        await after.remove_roles(role)
                        if role_letters[role_name] in Usuario.read(after.id)["roles"]:
                            Usuario.update(after.id, Usuario.read(after.id)["points"], Usuario.read(after.id)["roles"].replace(role_letters[role_name], ""))
                            print("rola removida: " + role_name)
            else:
                for role_name in role_order:
                    if any(role.name == role_name for role in after.roles):
                        roles += role_letters[role_name]
                Usuario.update(after.id, Usuario.read(after.id)["points"], roles)
                print("rolas adicionadas: " + roles)    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if Usuario.read(member.id):
            Usuario.update(member.id, Usuario.read(member.id)["roles"], "")
        else:
            print("Usuário não registrado no Banco de Dados")

async def setup(bot):
     await bot.add_cog(ModCommands(bot))