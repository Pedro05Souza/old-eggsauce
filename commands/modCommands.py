from discord.ext import commands
import discord
import os
from dotenv import load_dotenv

class ModCommands(commands.Cog):
    
    def __init__(self, bot):
        load_dotenv()
        self.devs = os.getenv("DEVS").split(",")
        self.bot = bot
    
    @commands.command()
    async def changeNickname(self, ctx, User: discord.Member, *, apelido: str):
        if ctx.author.top_role.postion <= ctx.guild.me.top_role.position or str(ctx.author.id) in self.devs:
            await User.edit(nick=apelido)
            await ctx.send(f"Nickname changed to {apelido} for {User}")

        else:
            await ctx.send(f"Failed to change {User}'s nickname to {apelido}")

    @commands.command()
    async def purge(self, ctx, amount: int):
        if ctx.author.top_role.position <= ctx.guild.me.top_role.position or str(ctx.author.id) in self.devs:
            await ctx.channel.purge(limit=amount)

    @commands.command()
    async def implode(self, ctx):
        user = ctx.author
        guild = ctx.me.guild
        channel = user.voice.channel
        if user.id == guild.owner.id or str(user.id) in self.devs and channel is not None:
            for member in channel.members:
                await member.move_to(None)

async def setup(bot):
     await bot.add_cog(ModCommands(bot))