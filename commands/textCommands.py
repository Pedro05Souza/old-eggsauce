# Description: cog that contains administration and fun commands
from discord.ext import commands
import discord
import os

class textCommands(commands.cog):

    def __init__(self, bot):
        self.bot = bot
        bot.remove_command('help')

    
    @commands.command()
    async def balls(self, ctx):
        await ctx.send("Hey doc")


    @commands.command()
    async def mogged(self, ctx, User: discord.Member):
            File = discord.File("mogged.png", filename="mogged.png")
            await ctx.send(file=File)
            await ctx.send(ctx.author.mention + " moggou " + User.mention + "!")
