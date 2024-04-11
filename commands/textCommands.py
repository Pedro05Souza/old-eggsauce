# Description: cog that contains administration and fun commands
import asyncio
from discord.ext import commands
import discord
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
        user = ctx.author
        owner = ctx.guild.owner.id
        if amount > 0 and amount <= 25:
            await ctx.channel.purge(limit=amount + 1)
        else:
            await ctx.send("Por favor, insira um número menor ou igual a 25 e maior que 0.")
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
    async def changeNickname(self, ctx, User: discord.Member, *, apelido: str):
        if User.top_role.position <= ctx.guild.me.top_role.position:
            await User.edit(nick=apelido)
            await ctx.send(f"Apelido de {User.mention} foi alterado para {apelido}")   
        else:
            await refund(ctx.author, ctx)
            await ctx.send("Você não pode alterar o apelido de um usuário com cargo maior ou igual ao meu.")

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

    @commands.command()
    async def duelo(self, ctx, User: discord.Member):
        if User.bot:
            await ctx.send("Você não pode desafiar um bot.")
            return
        elif User == ctx.author:
            await ctx.send("Você não pode desafiar a si mesmo.")
            return
        else:
            await ctx.send(f"{ctx.author.mention} desafiou {User.mention} para um duelo!")
            await ctx.send(f"{User.mention} aceita o desafio?")
            await self.bot.wait_for('message', check=lambda message: message.author == User and message.content == "!aceitar", timeout=10)
            try:
                await ctx.send(f"{User.mention} aceitou o desafio!")
                # falta implementar: Ideia cada membro especial do server tem um ataque customizado
                # exemplo: Cruz: bankai
            except Exception as e:
                await ctx.send(f"{User.mention} foi um cabaço e não aceitou o desafio.")


    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Lista de comandos do commands", description="Hey", color=0xeee657)
        embed.add_field(name="mogged", value="Moga outro usuário", inline=False)
        embed.add_field(name="changeNickname", value="Muda o nome", inline=False)
        embed.add_field(name="balls", value="Hey doc", inline=False)
        await ctx.send(embed=embed)
        

async def setup(bot):
    await bot.add_cog(TextCommands(bot))