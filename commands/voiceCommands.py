# Description: Cog that contains commands that affect in some way the voice channels

from discord.ext import commands
from db.Usuario import Usuario
import discord
import os
from dotenv import load_dotenv
from tools.pricing import pricing, refund

class VoipCommands(commands.Cog):
    
    def __init__(self, bot):
        load_dotenv()
        self.bot = bot
        self.gods = []
        self.devs = os.getenv("DEVS").split(",")

    
    @commands.command()
    @pricing()
    async def momentoDeSilencio(self, ctx):
        servidor = ctx.me.guild
        user = ctx.author
        if user.voice.channel is not None:
            for membro in user.voice.channel.members:
                await membro.edit(mute = True)
        else:
            await ctx.send("Você não está em um canal de voz.")
            await refund(user, ctx)

    @commands.command()
    @pricing()
    async def god(self, ctx):
        user = ctx.author
        if user not in self.gods:
            self.gods.append(ctx.author)
            await ctx.send(f"{ctx.author.mention} foi adicionado a lista de deuses", ephemeral=True)
        elif user in self.gods:
            await ctx.send(f"{user.mention} já é um deus", ephemeral=True)
            await refund(user, ctx)
            

    @commands.command()
    @pricing()
    async def radinho(self, ctx):
        servidor = ctx.me.guild
        user = ctx.author
        channel = user.voice.channel #channel
        if user.voice.channel is not None: 
            await channel.edit(bitrate = 8000)
        else:
            await ctx.send("Você não está em um canal de voz.")
            await refund(user, ctx)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member in self.gods and not before.mute and after.mute:
            await member.edit(mute=False)
            print(f"{member.name} foi mutado, mas era um Deus e foi desmutado")
        if member in self.gods and not before.deaf and after.deaf:
            await member.edit(deafen=False)
            print(f"{member.name} foi ensurdecido, mas era um Deus e foi desensurdecido")

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
    async def tirarRadinho(self, ctx):
        servidor = ctx.me.guild
        user = ctx.author
        channel = user.voice.channel
        if user.voice.channel is not None:
            await channel.edit(bitrate = 64000)
        else:
            await ctx.send("Você não está em um canal de voz.")
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
    async def disconnect(self, ctx, User: discord.Member):
        user = ctx.author
        channel = User.voice.channel
        if channel is not None:
            await User.move_to(None)
            await ctx.send(f"{User.mention} foi desconectado")
        else:
            await ctx.send("Este usuário não está em um canal de voz.")
            await refund(user, ctx)

    @commands.command()
    @pricing()
    async def unmute(self, ctx, User: discord.Member):
        user = ctx.author
        channel = User.voice.channel
        if channel is not None:
            await User.edit(mute=False)
            await ctx.send(f"{User.mention} foi desmutado")
        else:
            await ctx.send("Este usuário não está em um canal de voz.")
            await refund(user, ctx)

    @commands.command()
    @pricing()
    async def undeafen(self, ctx, User: discord.Member):
        user = ctx.author
        channel = User.voice.channel
        if channel is not None:
            await User.edit(deafen=False)
            await ctx.send(f"{User.mention} foi dessurdo")
        else:
            await ctx.send("Este usuário não está em um canal de voz.")
            await refund(user, ctx)

    #@commands.command()
    #async def prisao(self, ctx, User:discord.Member):



async def setup(bot):
    await bot.add_cog(VoipCommands(bot))