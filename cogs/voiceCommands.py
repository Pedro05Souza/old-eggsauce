# Description: Cog that contains commands that affect in some way the voice channels
from discord.ext import commands
import asyncio
import discord
import os
import random
from dotenv import load_dotenv
from cogs.textCommands import TextCommands
from tools.pricing import pricing, refund

# This class is responsible for handling the voice commands.
class VoipCommands(commands.Cog):
    def __init__(self, bot):
        load_dotenv()
        self.bot = bot
        self.gods = []
        self.devs = os.getenv("DEVS").split(",")
        self.prisioner = {}

    
    @commands.command()
    @pricing()
    async def momentOfSilence(self, ctx):
        user = ctx.author
        if user.voice.channel is not None:
            for membro in user.voice.channel.members:
                await membro.edit(mute = True)
        else:
            await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: {ctx.author.display_name}is not in a voice channel.")
            await refund(user, ctx)
            

    @commands.command()
    @pricing()
    async def god(self, ctx):
        user = ctx.author
        if user not in self.gods:
            self.gods.append(ctx.author)
            await TextCommands.create_embed_without_title(ctx, f"{ctx.author.display_name} has been added to the divine beings.")
        elif user in self.gods:
            await TextCommands.create_embed_without_title(ctx, f"{ctx.author.display_name} is already a divine being.")
            await refund(user, ctx)
            
    @commands.command()
    @pricing()
    async def radinho(self, ctx):
        servidor = ctx.me.guild
        user = ctx.author
        channel = user.voice.channel
        if user.voice.channel is not None: 
            await channel.edit(bitrate = 8000)
        else:
            await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: {ctx.author.display_name} is not in a voice channel.")
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
            await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: {ctx.author.display_name} is not in a voice channel.")
            await refund(user, ctx)

    @commands.command()
    @pricing()
    async def mute(self, ctx, User: discord.Member = None):
        user = ctx.author
        if User is None:
            User = ctx.author
        if User.voice is not None:
            channel = User.voice.channel
        else:
            channel = None
            await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: this user is not in a voice channel.")
            await refund(user,ctx)
        if channel is not None and User.voice.mute == False:
            await User.edit(mute=True)
            await TextCommands.create_embed_without_title(ctx, f"{User.display_name} has been muted.")
        elif User.voice.mute == True:
            await TextCommands.create_embed_without_title(ctx, f"{User.display_name} is already muted.")
            await refund(user, ctx)
        else:
            await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: this user is not in a voice channel.")
            await refund(user, ctx)

    @commands.command()
    @pricing()
    async def unmute(self, ctx, User: discord.Member = None):
        if User is None:
            User = ctx.author
        if User.voice.channel is not None and User.voice.mute == True:
            await User.edit(mute=False)
            await TextCommands.create_embed_without_title(ctx, f"{User.display_name} has been unmuted.")
        elif User.voice.mute == False:
            await TextCommands.create_embed_without_title(ctx, f"{User.display_name} is already unmuted.")
            await refund(ctx.author, ctx)
        else:
            await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: this user is not in a voice channel.")
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
            await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: {ctx.author.display_name} is not in a voice channel.")
            await refund(user, ctx)

    @commands.command()
    @pricing()
    async def tirarRadinho(self, ctx):
        user = ctx.author
        channel = user.voice.channel
        if user.voice.channel is not None:
            await channel.edit(bitrate = 64000)
        else:
            await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: {ctx.author.display_name} is not in a voice channel.")
            await refund(user, ctx)

    @commands.command()
    @pricing()
    async def deafen(self, ctx, User: discord.Member=None):
        if User is None:
            User = ctx.author
        if User.voice.channel is not None and User.voice.deaf == False:
            await User.edit(deafen=True)
            await TextCommands.create_embed_without_title(ctx, f"{User.display_name} has been deafened.")
        elif User.voice.deaf == True:
            await TextCommands.create_embed_without_title(ctx, f"{User.display_name} is already deafened.")
            await refund(ctx.author, ctx)
        else:
            await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: this user is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def undeafen(self, ctx, User: discord.Member = None):
        if User is None:
            User = ctx.author
        if User.voice.channel is not None and User.voice.deaf == True:
            await User.edit(deafen=False)
            await TextCommands.create_embed_without_title(ctx, f"{User.display_name} has been undeafened.")
        elif User.voice.deaf == False:
            await TextCommands.create_embed_without_title(ctx, f"{User.display_name} is already undeafened.")
            await refund(ctx.author, ctx)
        else:
            await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: this user is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def disconnect(self, ctx, User: discord.Member):
        if User.voice.channel is not None:
            await User.move_to(None)
            await TextCommands.create_embed_without_title(ctx, f"{User.display_name} has been disconnected.")
        else:
            await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: this user is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def prison(self, ctx, User:discord.Member):
        if User.voice is None or User.voice.channel is None:
            await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: {User.display_name} is not in a voice channel.")
            await refund(ctx.author, ctx)
            return
        await TextCommands.create_embed_without_title(ctx, f":chains: {User.display_name} has been imprisoned for 60 seconds.")
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
                await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: There are no voice channels to throw the user to.")
            else:
                channel = random.choice(channelVet)
                if channel == User.voice.channel:
                    self.fling(ctx, User)
                else:
                    await User.move_to(channel)
                    await TextCommands.create_embed_without_title(ctx, f"{User.display_name} has been thrown to {channel.name}.")
        else:
            await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: {User.display_name} is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def detonate(self, ctx):
        for vc in ctx.author.guild.voice_channels:
            for membros in vc.members:
                await membros.move_to(None)
        await TextCommands.create_embed_without_title(ctx, f"All users have been disconnected from their voice channels.")

    @commands.command("shuffle")
    @pricing()
    async def shuffle(self, ctx):
        channelVet = [channel for channel in ctx.author.guild.voice_channels]
        if not channelVet:
            await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: There are no voice channels to throw the users to.")
        else:
            for vc in channelVet:
                for membros in vc.members:
                    await membros.move_to(random.choice(channelVet))
        await TextCommands.create_embed_without_title(ctx, f"All users have been thrown to random voice channels.")
    
    @commands.command("emergency")
    @pricing()
    async def emergency(self, ctx):
        for vc in ctx.author.guild.voice_channels:
            for membros in vc.members:
                authorchannel = ctx.author.voice.channel
                if authorchannel is not None:
                    await membros.move_to(authorchannel)
                else:
                    refund(ctx.author, ctx)
                    await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: {ctx.author.display_name} is not in a voice channel.")
        await TextCommands.create_embed_without_title(ctx, f"All users have been thrown to {ctx.author.voice.channel.name}.")
    
    @commands.command("fish")
    @pricing()
    async def fish(self, ctx, User: discord.Member):
        if User.voice is not None and ctx.author.voice is not None:
            await User.move_to(ctx.author.voice.channel)
            await TextCommands.create_embed_without_title(ctx, f"{User.display_name} has been thrown to {ctx.author.voice.channel.name}.")
        else:
            await TextCommands.create_embed_without_title(ctx, f":no_entry:sign: {User.display_name} or {ctx.author.display_name} is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if self.prisioner.get(member.id, 0) > 0:
            if after.channel is None or after.channel.name != "Prisão":
                prison_channel = discord.utils.get(member.guild.channels, name="Prisão")
                if prison_channel is not None:
                    await member.move_to(prison_channel)       
        if member in self.gods and not before.mute and after.mute:
            await member.edit(mute=False)
            print(f"{member.name} was muted, but was an unmutter and was unmuted")
        if member in self.gods and not before.deaf and after.deaf:
            await member.edit(deafen=False)
            print(f"{member.name} was deafened, but was an undeafener and was undeafened")
        

async def setup(bot):
    await bot.add_cog(VoipCommands(bot))