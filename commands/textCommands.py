# Description: cog that contains administration and fun commands
import asyncio
from discord.ext import commands
import discord
from db.UserDB import Usuario
from random import randint
from dotenv import load_dotenv
import os
import random
from tools.pricing import pricing, refund

class TextCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        bot.remove_command('help')

    @commands.Cog.listener()
    async def on_ready(self):
        asyncio.create_task(self.work_periodically())


    @commands.command()
    @pricing()
    async def balls(self, ctx):
        await ctx.send("balls")

    @commands.command()
    @pricing()
    async def mog(self, ctx, User: discord.Member):
            path = random.choice(os.listdir("images/mogged/"))
            await ctx.send(file=discord.File("images/mogged/"+path))
            await ctx.send(f"{User.mention} bye bye 🤫🧏‍♂️")

    @commands.command()
    @pricing()
    async def purge(self, ctx, amount: int):
        if amount > 0 and amount <= 25:
            await ctx.channel.purge(limit=amount + 1)
        else:
            await ctx.send("Por favor, insira um número menor ou igual a 25 e maior que 0.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def kick(self, ctx, User: discord.Member):
        if User.id == ctx.author.id:
                await ctx.send("Você não pode se kickar.")
                await refund(ctx.author, ctx) 
                return
        if User.top_role.position <= ctx.guild.me.top_role.position:
            await User.kick()
            await ctx.send(f"{User.mention} foi kickado")
        else:
            await ctx.send("Você não tem permissão para fazer isso.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def ban(self, ctx, User: discord.Member):
        if User.id == ctx.author.id:
                await ctx.send("Você não pode se banir.")
                await refund(ctx.author, ctx)
                return
        if User.top_role.position <= ctx.guild.me.top_role.position:
            await User.kick()
            await ctx.send(f"{User.mention} foi kickado")
        else:
            await ctx.send("não tenho permissão para fazer isso.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def mudarApelido(self, ctx, User: discord.Member, *, apelido: str):
        if User.top_role.position <= ctx.guild.me.top_role.position:
            if User.id == ctx.me.id:
                await ctx.send("Eu não posso mudar meu próprio apelido.")
                await refund(ctx.author, ctx)
                return
            else:
                await User.edit(nick=apelido)
                await ctx.send(f"Apelido de {User.mention} foi alterado para {apelido}")   
        else:
            await refund(ctx.author, ctx)
            await ctx.send("Você não pode alterar o apelido de um usuário com cargo maior ou igual ao meu.")

    @commands.command()
    @pricing()
    async def perdoar(self, ctx, id: str):
        User = await self.bot.fetch_user(id)
        if await ctx.guild.fetch_ban(User):
            await ctx.guild.unban(User)
            await ctx.send(f"{User.mention} foi perdoado")
        else:
            await ctx.send("Este usuário não está banido")
            await refund(ctx.author, ctx)
            
    @commands.command()
    @pricing()
    async def cargoTrabalhador(self, ctx):
         if Usuario.read(ctx.author.id):    
            permissions = discord.Permissions(
                move_members = True,
            )
            role = discord.utils.get(ctx.guild.roles, name="trabalhador assalariado")
            if role is None:
                role = await ctx.guild.create_role(name="trabalhador assalariado", permissions=permissions, color=discord.Color.from_rgb(165, 42, 42))
                await role.edit(position=9, hoist=True, mentionable=True)
            if ctx.author in role.members:
                await ctx.send("Você já tem esse cargo.")
                return
            if Usuario.read(ctx.author.id)["roles"] == "":
                await ctx.author.add_roles(role)
                await ctx.send(f"{ctx.author.mention} recebeu o cargo de trabalhador.")
                Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"], Usuario.read(ctx.author.id)["roles"] + "T")


    @commands.command()
    @pricing()
    async def cargoClasseBaixa(self, ctx):
        if Usuario.read(ctx.author.id):    
             permissions = discord.Permissions(
                 move_members = True,
                 mute_members = True,
                 deafen_members = True
             )
             role = discord.utils.get(ctx.guild.roles, name="Plebeu")
             if role is None:
                    role = await ctx.guild.create_role(name="Plebeu", permissions=permissions, color=discord.Color.from_rgb(255, 0, 0))
                    await role.edit(position=8, hoist=True, mentionable=True)
             if ctx.author in role.members:
                    await ctx.send("Você já tem esse cargo.")
                    await refund(ctx.author, ctx)
                    return
             if Usuario.read(ctx.author.id)["roles"] == "T":
                await ctx.author.add_roles(role)
                await ctx.send(f"{ctx.author.mention} recebeu o cargo de classe baixa.")
                Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"], Usuario.read(ctx.author.id)["roles"] + "B")
             else:
                await ctx.send("Você não tem algum ou alguns dos cargos necessários.")
                await refund(ctx.author, ctx)   

    @commands.command()
    @pricing()
    async def cargoClasseMedia(self, ctx):
        if Usuario.read(ctx.author.id):    
             permissions = discord.Permissions(
                 move_members = True,
                 mute_members = True,
                 deafen_members = True,
                 manage_messages = True
             )
             role = discord.utils.get(ctx.guild.roles, name="pobretão com um gol 1.0")
             if role is None:
                    role = await ctx.guild.create_role(name="pobretão com um gol 1.0", permissions=permissions, color=discord.Color.from_rgb(0, 0, 255))
                    await role.edit(position=7, hoist=True, mentionable=True)
             if ctx.author in role.members:
                    await ctx.send("Você já tem esse cargo.")
                    await refund(ctx.author, ctx)
                    return
             if Usuario.read(ctx.author.id)["roles"] == "TB":
                await ctx.author.add_roles(role)
                await ctx.send(f"{ctx.author.mention} recebeu o cargo de classe média.")
                Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"], Usuario.read(ctx.author.id)["roles"] + "M")
             else:
                    await ctx.send("Você não tem algum ou alguns dos cargos necessários.")
                    await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def cargoClasseAlta(self, ctx):
         if Usuario.read(ctx.author.id):    
             permissions = discord.Permissions(
                 move_members = True,
                 mute_members = True,
                 deafen_members = True,
                 manage_messages = True,
                 manage_channels = True
             )
             role = discord.utils.get(ctx.guild.roles, name="magnata")
             if role is None:
                    role = await ctx.guild.create_role(name="magnata", permissions=permissions, color=discord.Color.from_rgb(0, 0, 0))
                    await role.edit(position=6, hoist=True, mentionable=True)
             if ctx.author in role.members:
                    await ctx.send("Você já tem esse cargo.")
                    await refund(ctx.author, ctx)
                    return
             if Usuario.read(ctx.author.id)["roles"] == "TBM":
                await ctx.author.add_roles(role)
                await ctx.send(f"{ctx.author.mention} recebeu o cargo de classe alta.")
                Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"], Usuario.read(ctx.author.id)["roles"] + "A")
             else:
                  await ctx.send("Você não tem algum ou alguns dos cargos necessários.")
                  await refund(ctx.author, ctx)
         
    @commands.command() 
    async def cassino(self, ctx, amount: int, cor: str):
        cor = cor.upper()
        coresPossiveis = ["RED", "BLACK", "GREEN"]
        corEmoji = {"RED": "🟥", "BLACK": "⬛", "GREEN": "🟩"}
        vermelhos = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        roleta = {i : "RED" if i in vermelhos else ("BLACK" if i != 0 else "GREEN") for i in range(0, 37)}

        if Usuario.read(ctx.author.id) and cor in coresPossiveis:
            if Usuario.read(ctx.author.id)["points"] >= amount and amount > 0:
                cassino = randint(0, 36)
                corSorteada = roleta[cassino]
                if corSorteada == "GREEN" and cor == "GREEN":
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + (amount * 14), Usuario.read(ctx.author.id)["roles"])
                    await ctx.send(f"{ctx.author.display_name} ganhou!")
                elif corSorteada == cor:
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + amount, Usuario.read(ctx.author.id)["roles"])
                    await ctx.send(f"{ctx.author.display_name} ganhou!")
                else:
                    await ctx.send(f"{ctx.author.display_name} perdeu, a cor sorteada foi {corSorteada} {corEmoji[corSorteada]}")                        
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] - amount, Usuario.read(ctx.author.id)["roles"])
                    return
            else:
                await ctx.send(f"{ctx.author.display_name} não tem pontos suficientes")
                return  
        else:
            await ctx.send("Selecione uma cor válida.")

    @cassino.error
    async def cassino_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Por favor, insira um valor e uma cor.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Por favor, insira um valor válido.")
        else:
            await ctx.send("Ocorreu um erro inesperado.")

    def salarios(self, User:discord.Member):
        salarios = {
            "T": 50,
            "B": 100,
            "M": 200,
            "A": 300
        }
        if Usuario.read(User.id):
             return salarios[Usuario.read(User.id)["roles"] [-1]]
        else:
            return 0
        
    async def work_periodically(self):
        load_dotenv()
        guild_id = int(os.getenv("GUILD_ID"))
        channel = self.bot.get_channel(int(os.getenv("CHANNEL_ID")))
        guild = self.bot.get_guild(guild_id)
        while True:
              for member in guild.members:
                   user_data = Usuario.read(member.id)
                   if user_data:
                        if user_data["roles"] != "":
                            Usuario.update(member.id, Usuario.read(member.id)["points"] + self.salarios(member), Usuario.read(member.id)["roles"])
                            await asyncio.sleep(1600)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
         if Usuario.read(member.id):
             Usuario.update(member.id, Usuario.read(member.id)["roles"], "")
         else:
              print("Usuário não registrado no Banco de Dados")

    @commands.command()
    async def nuke(self, ctx):
         await Usuario.deleteAll()
              
async def setup(bot):
    await bot.add_cog(TextCommands(bot))