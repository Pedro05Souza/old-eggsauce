from discord.ext import commands
from tools.pointscore import pricing, refund
from tools.shared import send_bot_embed
from tools.settings import regular_command_cooldown
from db.userDB import User
from random import choice
from discord.ext.commands import Context
import discord
import asyncio

class HostileCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prisioner = {}
        self.gods = []

    @commands.command("momentofsilence" , aliases=["mos"])
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def moment_of_silence(self, ctx: Context) -> None:
        """Mutes all users in the voice channel of the author of the command."""
        user = ctx.author
        if user.voice.channel is not None:
            for membro in user.voice.channel.members:
                await membro.edit(mute = True)
        else:
            await send_bot_embed(ctx, description=f":no_entry:sign: {ctx.author.display_name}is not in a voice channel.")
            await refund(user, ctx)

    @commands.command("radio")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def radio(self, ctx: Context) -> None:
        """Sets the voice channel to radio quality."""
        user = ctx.author
        channel = user.voice.channel
        if user.voice.channel is not None: 
            await channel.edit(bitrate = 8000)
        else:
            await send_bot_embed(ctx, description=f":no_entry:sign: {ctx.author.display_name} is not in a voice channel.")
            await refund(user, ctx)

    @commands.command(name="explode")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def explode(self, ctx: Context) -> None:
        """Disconnects all users from their voice channels."""
        user = ctx.author
        channel = user.voice.channel if user.voice else None
        if channel is not None:
            await channel.delete()
        else:
            await send_bot_embed(ctx, description=f":no_entry:sign: {ctx.author.display_name} is not in a voice channel.")
            await refund(user, ctx)

    @commands.command(name="mute")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def mute(self, ctx: Context, user: discord.Member = None) -> None:
        """Mutes a user."""
        user = ctx.author
        if user is None:
            user = ctx.author
        if user.voice is not None:
            channel = user.voice.channel
        else:
            channel = None
            await send_bot_embed(ctx, description=f":no_entry:sign: this user is not in a voice channel.")
            await refund(user,ctx)
        if channel is not None and user.voice.mute == False:
            await user.edit(mute=True)
            await send_bot_embed(ctx, description=f"{user.display_name} has been muted.")
        elif user.voice.mute == True:
            await send_bot_embed(ctx, description=f"{user.display_name} is already muted.")
            await refund(user, ctx)
        else:
            await send_bot_embed(ctx, description=f":no_entry:sign: this user is not in a voice channel.")
            await refund(user, ctx)

    @commands.command(name="unmute")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def unmute(self, ctx: Context, user: discord.Member = None) -> None:
        """Unmutes a user."""
        if user is None:
            user = ctx.author
        if user.voice.channel is not None and user.voice.mute == True:
            await user.edit(mute=False)
            await send_bot_embed(ctx, description=f"{user.display_name} has been unmuted.")
        elif user.voice.mute == False:
            await send_bot_embed(ctx, description=f"{user.display_name} is already unmuted.")
            await refund(ctx.author, ctx)
        else:
            await send_bot_embed(ctx, description=f":no_entry:sign: this user is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.command(name="implode")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def implode(self, ctx: Context) -> None:
        """Disconnects all users from their voice channels."""
        user = ctx.author
        channel = user.voice.channel if user.voice else None
        if channel is not None:
            for member in channel.members:
                await member.move_to(None)
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} is not in a voice channel.")
            await refund(user, ctx)

    @commands.command(name="removeradio")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def remove_radio(self, ctx: Context) -> None:
        """Removes the radio effect from the voice channel."""
        user = ctx.author
        channel = user.voice.channel
        if user.voice.channel is not None:
            await channel.edit(bitrate = 64000)
        else:
            await send_bot_embed(ctx, description=f":no_entry:sign: {ctx.author.display_name} is not in a voice channel.")
            await refund(user, ctx)

    @commands.command(name="deafen")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def deafen(self, ctx: Context, user: discord.Member=None) -> None:
        """Deafens a user."""
        if user is None:
            user = ctx.author
        if user.voice.channel is not None and user.voice.deaf == False:
            await user.edit(deafen=True)
            await send_bot_embed(ctx, description=f"{user.display_name} has been deafened.")
        elif user.voice.deaf == True:
            await send_bot_embed(ctx, description=f"{user.display_name} is already deafened.")
            await refund(ctx.author, ctx)
        else:
            await send_bot_embed(ctx, description=f":no_entry:sign: this user is not in a voice channel.")
            await refund(ctx.author, ctx)
    
    @commands.command(name="pardon")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def pardon(self, ctx: Context, user_id: int) -> None:
        """Pardons a user from prison."""
        try:
            ban_entry = await ctx.guild.fetch_ban(discord.Object(id=user_id))
            await ctx.guild.unban(ban_entry.user)
            await send_bot_embed(ctx, description=f"{ban_entry.user.display_name} has been pardoned.")
        except discord.NotFound:
            await send_bot_embed(ctx, description=":no_entry_sign: This user is not banned.")
        except Exception as e:
            await send_bot_embed(ctx, description="Failed to pardon the user.")
            await refund(ctx.author, ctx)

    @commands.command(name="undeafen")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def undeafen(self, ctx: Context, user: discord.Member = None) -> None:
        """Undeafens a user."""
        if user is None:
            user = ctx.author
        if user.voice.channel is not None and user.voice.deaf == True:
            await user.edit(deafen=False)
            await send_bot_embed(ctx, description=f"{user.display_name} has been undeafened.")
        elif user.voice.deaf == False:
            await send_bot_embed(ctx, description=f"{user.display_name} is already undeafened.")
            await refund(ctx.author, ctx)
        else:
            await send_bot_embed(ctx, description=f":no_entry:sign: this user is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.command(name="disconnect", aliases=['dc'])
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def disconnect(self, ctx: Context, user: discord.Member) -> None:
        """Disconnects a user from their voice channel."""
        if user.voice.channel is not None:
            await user.move_to(None)
            await send_bot_embed(ctx, description=f"{user.display_name} has been disconnected.")
        else:
            await send_bot_embed(ctx, description=f":no_entry:sign: this user is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.command(name="prison", aliases=["jail"])
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def prison(self, ctx: Context, user:discord.Member) -> None:
        """Imprisons a user for 60 seconds."""
        if user.voice is None or user.voice.channel is None:
            await send_bot_embed(ctx, description=f":no_entry:sign: {user.display_name} is not in a voice channel.")
            await refund(ctx.author, ctx)
            return
        await send_bot_embed(ctx, description=f":chains: {user.display_name} has been imprisoned for 60 seconds.")
        self.prisioner[user.id] = 60
        await self.prision_counter(ctx, user, 60)
            
    async def prision_counter(self, ctx: Context, user: discord.Member, time: int) -> None:
        """Counts down the time a user is in prison."""
        server = ctx.guild
        channel_name = "Prison"
        channels = ctx.guild.channels
        prison_channel = discord.utils.get(channels, name=channel_name)
        if prison_channel is None:
            prison_channel = await server.create_voice_channel(channel_name)
        if user.voice and user.voice.channel:
            await user.move_to(prison_channel)
            if time > 0:
                await asyncio.sleep(1)
                self.prisioner[user.id] = time - 1
                await self.prision_counter(ctx, user, time - 1)
            else:
                await prison_channel.delete()
                
    @commands.command(name="fling")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def fling(self, ctx: Context, user: discord.Member) -> None:
        """Throws a user to a random voice channel."""
        if user.voice is not None:
            channelVet = [channel for channel in user.guild.voice_channels if channel != user.voice.channel]
            if not channelVet:
                await send_bot_embed(ctx, description=f":no_entry:sign: There are no voice channels to throw the user to.")
            else:
                channel = choice(channelVet)
                if channel == user.voice.channel:
                    self.fling(ctx, user)
                else:
                    await user.move_to(channel)
                    await send_bot_embed(ctx, description=f"{user.display_name} has been thrown to {channel.name}.")
        else:
            await send_bot_embed(ctx, description=f":no_entry:sign: {user.display_name} is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.command(name="detonate")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def detonate(self, ctx: Context) -> None:
        """Disconnects all users from their voice channels."""
        for vc in ctx.author.guild.voice_channels:
            for membros in vc.members:
                await membros.move_to(None)
        await send_bot_embed(ctx, description=f"All users have been disconnected from their voice channels.")

    @commands.command(name="shuffle")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def shuffle(self, ctx: Context) -> None:
        """Throws all users to random voice channels."""
        channelVet = [channel for channel in ctx.author.guild.voice_channels]
        if not channelVet:
            await send_bot_embed(ctx, description=f":no_entry:sign: There are no voice channels to throw the users to.")
        else:
            for vc in channelVet:
                for membros in vc.members:
                    await membros.move_to(choice(channelVet))
        await send_bot_embed(ctx, description=f"All users have been thrown to random voice channels.")
    
    @commands.command(name="emergency")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def emergency(self, ctx: Context) -> None:
        """Throws all users to the voice channel of the author of the command."""
        for vc in ctx.author.guild.voice_channels:
            for membros in vc.members:
                authorchannel = ctx.author.voice.channel
                if authorchannel is not None:
                    await membros.move_to(authorchannel)
                else:
                    refund(ctx.author, ctx)
                    await send_bot_embed(ctx, description=f":no_entry:sign: {ctx.author.display_name} is not in a voice channel.")
        await send_bot_embed(ctx, description=f"All users have been thrown to {ctx.author.voice.channel.name}.")
    
    @commands.command(name="fish")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def fish(self, ctx: Context, user: discord.Member) -> None:
        """Throws a user to the voice channel of the author of the command."""
        if user.voice is not None and ctx.author.voice is not None:
            await user.move_to(ctx.author.voice.channel)
            await send_bot_embed(ctx, description=f"{user.display_name} has been thrown to {ctx.author.voice.channel.name}.")
        else:
            await send_bot_embed(ctx, description=f":no_entry:sign: {user.display_name} or {ctx.author.display_name} is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.command(name="kick")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def kick(self, ctx: Context, user: discord.Member) -> None:
        """Kicks a user."""
        if user.id == ctx.author.id:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't kick yourself.")
                await refund(ctx.author, ctx) 
                return
        await user.kick()
        await send_bot_embed(ctx, description=f"{user.display_name} was kicked.")
     
    @commands.command(name="ban")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def ban(self, ctx: Context, user: discord.Member) -> None:
        """Bans a user."""
        if user.id == ctx.author.id:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't ban yourself.")
                await refund(ctx.author, ctx)
                return
        await user.ban()
        await send_bot_embed(ctx, description=f"{user.display_name} was banned.")

    @commands.command(name="changenickname", aliases=["nick"])
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def change_nickname(self, ctx: Context, user: discord.Member, *nickname: str) -> None:
        """Changes a user's nickname."""
        if user.id == ctx.me.id:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, i can't change my own nickname.")
            await refund(ctx.author, ctx)
            return
        else:
            nickname = " ".join(nickname)
            await user.edit(nick=nickname)
            await send_bot_embed(ctx, description=f"{user.display_name}'s nickname has been changed to {nickname}.")

    @commands.command(name="nuke")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def nuke(self, ctx: Context) -> None:
        """Nuke the database."""
        User.resetAll()
        await send_bot_embed(ctx, description=":radioactive: All users have been set back to 0 eggbux and have lost their titles.")  

    @commands.command(name="antimute")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def antimute(self, ctx: Context) -> None:
        """Makes the user never being able to get muted and deafened."""
        user = ctx.author
        if user not in self.gods:
            self.gods.append(ctx.author)
            await send_bot_embed(ctx, description=f"{ctx.author.display_name} has been added to the divine beings.")
        elif user in self.gods:
            await send_bot_embed(ctx, description=f"{ctx.author.display_name} is already a divine being.")
            await refund(user, ctx)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if self.prisioner.get(member.id, 0) > 0:
            if after.channel is None or after.channel.name != "Prison":
                prison_channel = discord.utils.get(member.guild.channels, name="Prison")
                if prison_channel is not None:
                    await member.move_to(prison_channel)       
        if member in self.gods and not before.mute and after.mute:
            await member.edit(mute=False)
        if member in self.gods and not before.deaf and after.deaf:
            await member.edit(deafen=False)

async def setup(bot):
    await bot.add_cog(HostileCommands(bot))