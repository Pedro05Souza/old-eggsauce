from discord.ext import commands
import discord
from db.Usuario import Usuario
from tools.pricing import pricing, Prices, refund
import os
from dotenv import load_dotenv

class ModCommands(commands.Cog):
    
    def __init__(self, bot):
        load_dotenv()
        self.devs = os.getenv("DEVS").split(",")
        self.bot = bot

    @commands.command()
    @pricing()
    async def changeNickname(self, ctx, User: discord.Member, *, apelido: str):
        if User.top_role.position <= ctx.guild.me.top_role.position:
            await User.edit(nick=apelido)
            await ctx.send(f"Apelido de {User.mention} foi alterado para {apelido}")   
        else:
            await refund(ctx.author, ctx)
            await ctx.send("Você não pode alterar o apelido de um usuário com cargo maior ou igual ao meu.")
            

    @commands.command()
    @pricing()
    async def purge(self, ctx, amount: int):
        user = ctx.author
        owner = ctx.guild.owner.id
        if amount <= 25 and amount > 0:
            await ctx.channel.purge(limit=amount + 1)
        else:
            await ctx.send("Por favor, insira um número menor ou igual a 25 e maior que 0.")
            await refund(user, ctx)

    @commands.command()
    @pricing()
    async def implode(self, ctx):
        user = ctx.author
        guild = ctx.me.guild
        channel = user.voice.channel if user.voice else None
        if channel is not None:
            for member in channel.members:
                await member.move_to(None)
        else:
            await ctx.send("Você não está em um canal de voz.")
            await refund(user, ctx)

    @commands.command()
    @pricing()
    async def explode(self, ctx):
        user = ctx.author
        guild = ctx.me.guild
        channel = user.voice.channel if user.voice else None
        if channel is not None:
            await channel.delete()
        else:
            await ctx.send("Você não está em um canal de voz.")
            await refund(user, ctx)

    @commands.command()
    @pricing()
    async def mute(self, ctx, User: discord.Member):
        user = ctx.author
        channel = User.voice.channel
        if channel is not None:
            await User.edit(mute=True)
            await ctx.send(f"{User.mention} foi mutado")
        else:
            await ctx.send("Este usuário não está em um canal de voz.")
            await refund(user, ctx)

    @commands.command()
    @pricing()
    async def deafen(self, ctx, User: discord.Member):
        user = ctx.author
        channel = User.voice.channel
        if channel is not None:
            await User.edit(deafen=True)
            await ctx.send(f"{User.mention} foi surdo")
        else:
            await ctx.send("Este usuário não está em um canal de voz.")
            await refund(user, ctx)


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
            await ctx.send("Você não tem permissão para fazer isso.")
            await refund(ctx.author, ctx)
        

    @commands.command()
    @pricing()
    async def pardon(self, ctx, id: str):
        User = await self.bot.fetch_user(id)
        user = ctx.author
        if await ctx.guild.fetch_ban(User):
            await ctx.guild.unban(User)
            await ctx.send(f"{User.mention} foi perdoado")
        else:
            await ctx.send("Este usuário não está banido")
            await refund(user, ctx)

async def setup(bot):
     await bot.add_cog(ModCommands(bot))