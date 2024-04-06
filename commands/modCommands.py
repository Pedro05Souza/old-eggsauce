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
        user = ctx.author
        owner = ctx.guild.owner.id
        if user.id == owner or str(user.id) in self.devs:
            await ctx.channel.purge(limit=amount + 1)
    

    @commands.command()
    async def implode(self, ctx):
        user = ctx.author
        guild = ctx.me.guild
        channel = user.voice.channel
        if (user.id == guild.owner.id or str(user.id) in self.devs) and channel is not None:
            for member in channel.members:
                await member.move_to(None)

    @commands.command()
    async def mute(self, ctx, User: discord.Member):
        channel = User.voice.channel
        if (ctx.author.top_role.position <= ctx.guild.me.top_role.position or str(ctx.author.id) in self.devs) and channel is not None:
            await User.edit(mute=True)
            await ctx.send(f"{User.mention} foi mutado")

    @commands.command()
    async def kick(self, ctx, User: discord.Member):
        user = ctx.author
        owner = ctx.guild.owner.id
        if user.id == owner or str(user.id) in self.devs:
            await User.kick()
            await ctx.send(f"{User.mention} foi kickado")
        else:
            try:
                await ctx.me.guild.fetch_ban(User)
            except(discord.ext.commands.errors.MemberNotFound):
                await ctx.send(f"{User} não foi encontrado")
            except(discord.HTTPException):
                await ctx.send(f"Erro de resposta do servidor")
            except(discord.Forbidden):
                await ctx.send(f"{ctx.author} não tem permissões para fazer isso")
    
    @commands.command()
    async def ban(self, ctx, User: discord.Member):
        user = ctx.author
        owner = ctx.guild.owner.id
        if user.id == owner or str(user.id) in self.devs:
            await User.ban()
            await ctx.send(f"{User.mention} foi banido")
        else:
            try:
                await ctx.me.guild.fetch_ban(User)
            except(discord.ext.commands.errors.MemberNotFound):
                await ctx.send(f"{User} não foi encontrado")
            except(discord.HTTPException):
                await ctx.send(f"Erro de resposta do servidor")
            except(discord.Forbidden):
                await ctx.send(f"{ctx.author} não tem permissões para fazer isso")

async def setup(bot):
     await bot.add_cog(ModCommands(bot))