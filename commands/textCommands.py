# Description: cog that contains administration and fun commands
import asyncio
from discord.ext import commands
import discord
import os
import random
from tools.pricing import pricing

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
    async def duelo(self, ctx, User: discord.Member):
        await ctx.send(f"{ctx.author.mention} desafiou {User.mention} para um duelo!")
        await ctx.send(f"{User.mention} aceita o desafio?")
        self.bot.wait_for('message', check=lambda message: message.author == User, timeout=60)
        try:
            await ctx.send(f"{User.mention} aceitou o desafio!")
            # falta implementar: Ideia cada membro especial do server tem um ataque customizado
            # exemplo: Cruz: bankai
        except asyncio.TimeoutError:
            await ctx.send(f"{User.mention} foi um cabaço e não aceitou o desafio.")


    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Lista de comandos do commands", description="Hey", color=0xeee657)
        embed.add_field(name="mogged", value="Moga outro usuário", inline=False)
        embed.add_field(name="changeNickname", value="Muda o nome", inline=False)
        embed.add_field(name="balls", value="Hey doc", inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_join(self, member):
        await member.send("Bem vindo ao ovomaltine!")

    @commands.Cog.listener()
    async def on_leave(self, member):
        await member.send("Tchau!") 
        

async def setup(bot):
    await bot.add_cog(TextCommands(bot))