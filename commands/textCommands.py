# Description: cog that contains administration and fun commands
from discord.ext import commands
import discord
from db.UserDB import Usuario
from random import randint
import os
import random
from tools.pricing import pricing, refund

class TextCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        bot.remove_command('help')

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
             await ctx.author.add_roles(role)
             await ctx.send(f"{ctx.author.mention} recebeu o cargo de trabalhador.")

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
                    await role.edit(position=9, hoist=True, mentionable=True)
             if ctx.author in role.members:
                    await ctx.send("Você já tem esse cargo.")
                    return
             await ctx.author.add_roles(role)
             await ctx.send(f"{ctx.author.mention} recebeu o cargo de classe baixa.")

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
                    await role.edit(position=9, hoist=True, mentionable=True)
             if ctx.author in role.members:
                    await ctx.send("Você já tem esse cargo.")
                    return
             await ctx.author.add_roles(role)
             await ctx.send(f"{ctx.author.mention} recebeu o cargo de classe magnata.")

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
                    await role.edit(position=9, hoist=True, mentionable=True)
             if ctx.author in role.members:
                    await ctx.send("Você já tem esse cargo.")
                    return
             await ctx.author.add_roles(role)
             await ctx.send(f"{ctx.author.mention} recebeu o cargo de classe baixa.")
         
    @commands.command() 
    async def cassino(self, ctx, amount: int, cor: str):
        cor = cor.upper()
        coresPossiveis = ["RED", "BLACK", "GREEN"]
        corEmoji = {"RED": "🟥", "BLACK": "⬛", "GREEN": "🟩"}
        if Usuario.read(ctx.author.id) and cor in coresPossiveis:
            if Usuario.read(ctx.author.id)["points"] >= amount and amount > 0:
                cassino = randint(0, 35)
                corSorteada = "RED" if cassino < 18 and cassino != 0 else ("GREEN" if cassino == 0 else "BLACK")
                if corSorteada == cor and cor == "GREEN":
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + (amount * 14))
                    await ctx.send(f"{ctx.author.display_name} ganhou!")
                elif corSorteada == cor:
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + amount )
                    await ctx.send(f"{ctx.author.display_name} ganhou!")
                else:
                    await ctx.send(f"{ctx.author.display_name} perdeu, a cor sorteada foi {corSorteada} {corEmoji[corSorteada]}")                        
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] - amount)
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

    @commands.command()
    async def nuke(self, ctx):
         await Usuario.deleteAll()
              
async def setup(bot):
    await bot.add_cog(TextCommands(bot))