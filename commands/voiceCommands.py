# Description: Cog that contains commands that affect in some way the voice channels
from discord.ext import commands
import asyncio
import discord
import os
import random
from dotenv import load_dotenv
from tools.pricing import pricing, refund

class VoipCommands(commands.Cog):
    def __init__(self, bot):
        load_dotenv()
        self.bot = bot
        self.gods = []
        self.devs = os.getenv("DEVS").split(",")
        self.prisioner = {}

    
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
    async def mute(self, ctx, User: discord.Member = None):
        user = ctx.author
        channel = User.voice.channel
        if User is None:
            User = ctx.author
        if channel is not None and User.voice.mute == False:
            await User.edit(mute=True)
            await ctx.send(f"{User.mention} foi mutado")
        elif User.voice.mute == True:
            await ctx.send(f"{User.mention} já está mutado")
            await refund(user, ctx)
        else:
            await ctx.send("Este usuário não está em um canal de voz.")
            await refund(user, ctx)

    @commands.command()
    @pricing()
    async def unmute(self, ctx, User: discord.Member = None):
        if User is None:
            User = ctx.author
        if User.voice.channel is not None and User.voice.mute == True:
            await User.edit(mute=False)
            await ctx.send(f"{User.mention} foi desmutado")
        elif User.voice.mute == False:
            await ctx.send(f"{User.mention} já está desmutado")
            await refund(ctx.author, ctx)
        else:
            await ctx.send("Este usuário não está em um canal de voz.")
            await refund(ctx.author, ctx)

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
        user = ctx.author
        channel = user.voice.channel
        if user.voice.channel is not None:
            await channel.edit(bitrate = 64000)
        else:
            await ctx.send("Você não está em um canal de voz.")
            await refund(user, ctx)

    @commands.command()
    @pricing()
    async def deafen(self, ctx, User: discord.Member=None):
        if User is None:
            User = ctx.author
        if User.voice.channel is not None and User.voice.deaf == False:
            await User.edit(deafen=True)
            await ctx.send(f"{User.mention} foi ensurdecido")
        elif User.voice.deaf == True:
            await ctx.send(f"{User.mention} já está ensurdecido")
            await refund(ctx.author, ctx)
        else:
            await ctx.send("Este usuário não está em um canal de voz.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def undeafen(self, ctx, User: discord.Member = None):
        if User is None:
            User = ctx.author
        if User.voice.channel is not None and User.voice.deaf == True:
            await User.edit(deafen=False)
            await ctx.send(f"{User.mention} foi desensurdecido")
        elif User.voice.deaf == False:
            await ctx.send(f"{User.mention} já está desensurdecido")
            await refund(ctx.author, ctx)
        else:
            await ctx.send("Este usuário não está em um canal de voz.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def disconnect(self, ctx, User: discord.Member):
        if User.voice.channel is not None:
            await User.move_to(None)
            await ctx.send(f"{User.mention} foi desconectado")
        else:
            await ctx.send("Este usuário não está em um canal de voz.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def prisao(self, ctx, User:discord.Member):
        if User.voice is None or User.voice.channel is None:
            await ctx.send("Este usuário não está em um canal de voz.")
            await refund(ctx.author, ctx)
            return
        await ctx.send(f"{User.mention} foi preso")
        self.prisioner[User.id] = 60
        await self.prision_counter(ctx, User, 60)
            
    async def prision_counter(self, ctx, User: discord.Member, time: int):
        servidor = ctx.guild
        channel_name = "Prisão"
        channels = ctx.guild.channels
        prison_channel = discord.utils.get(channels, name=channel_name)
        if prison_channel is None:
            prison_channel = await servidor.create_voice_channel(channel_name)
        if User.voice and User.voice.channel:
            await User.move_to(prison_channel)
            if time > 0:
                await asyncio.sleep(1)
                self.prisioner[User.id] = time - 1
                await self.prision_counter(ctx, User, time - 1)
            else:
                await prison_channel.delete()
                
    @commands.command()
    @pricing()
    async def fling(self, ctx, User: discord.Member):
        if User.voice is not None:
            channelVet = [channel for channel in User.guild.voice_channels if channel != User.voice.channel]
            if not channelVet:
                await ctx.send("Não há outros canais de voz disponíveis")
            else:
                await User.move_to(random.choice(channelVet))
                await ctx.send(f"{User.mention} foi movido")
        else:
            await ctx.send("Usuário não está em um canal de voz.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def detonate(self, ctx):
        for vc in ctx.author.guild.voice_channels:
            for membros in vc.members:
                await membros.move_to(None)
        await ctx.send("Todos os usuários foram desconectados dos canais de voz.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if self.prisioner.get(member.id, 0) > 0:
            if after.channel is None or after.channel.name != "Prisão":
                prison_channel = discord.utils.get(member.guild.channels, name="Prisão")
                if prison_channel is not None:
                    await member.move_to(prison_channel)       
        if member in self.gods and not before.mute and after.mute:
            await member.edit(mute=False)
            print(f"{member.name} foi mutado, mas era um Deus e foi desmutado")
        if member in self.gods and not before.deaf and after.deaf:
            await member.edit(deafen=False)
            print(f"{member.name} foi ensurdecido, mas era um Deus e foi desensurdecido")
        

async def setup(bot):
    await bot.add_cog(VoipCommands(bot))