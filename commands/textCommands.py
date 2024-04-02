# Description: cog that contains administration and fun commands
from discord.ext import commands
import discord

class TextCommands(commands.Cog):

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


    async def help(self, ctx):
        embed = discord.Embed(title="Lista de comandos do commands", description="Hey", color=0xeee657)
        embed.add_field(name="mogged", value="Moga outro usuário", inline=False)
        embed.add_field(name="changeNickname", value="Muda o nome", inline=False)
        embed.add_field(name="balls", value="Hey doc", inline=False)
        await ctx.send(embed=embed)
        

async def setup(bot):
    await bot.add_cog(TextCommands(bot))