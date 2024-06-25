from discord.ext import commands
from tools.pricing import pricing, refund
from tools.embed import create_embed_without_title
import discord
from db.userDB import Usuario
from random import choice
import asyncio

class HostileCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prisioner = {}
        self.gods = []

    @commands.command("momentOfSilence")
    @commands.bot_has_permissions(mute_members=True)
    @pricing()
    async def moment_of_silence(self, ctx):
        """Mutes all users in the voice channel of the author of the command."""
        user = ctx.author
        if user.voice.channel is not None:
            for membro in user.voice.channel.members:
                await membro.edit(mute = True)
        else:
            await create_embed_without_title(ctx, f":no_entry:sign: {ctx.author.display_name}is not in a voice channel.")
            await refund(user, ctx)

    @commands.command()
    @commands.bot_has_permissions(manage_channels=True)
    @pricing()
    async def radinho(self, ctx):
        """Sets the voice channel to radio quality."""
        user = ctx.author
        channel = user.voice.channel
        if user.voice.channel is not None: 
            await channel.edit(bitrate = 8000)
        else:
            await create_embed_without_title(ctx, f":no_entry:sign: {ctx.author.display_name} is not in a voice channel.")
            await refund(user, ctx)

    @commands.command()
    @commands.bot_has_permissions(manage_channels=True)
    @pricing()
    async def explode(self, ctx):
        """Disconnects all users from their voice channels."""
        user = ctx.author
        channel = user.voice.channel if user.voice else None
        if channel is not None:
            await channel.delete()
        else:
            await create_embed_without_title(ctx, f":no_entry:sign: {ctx.author.display_name} is not in a voice channel.")
            await refund(user, ctx)

    @commands.command()
    @commands.bot_has_permissions(mute_members=True)
    @pricing()
    async def mute(self, ctx, User: discord.Member = None):
        """Mutes a user."""
        user = ctx.author
        if User is None:
            User = ctx.author
        if User.voice is not None:
            channel = User.voice.channel
        else:
            channel = None
            await create_embed_without_title(ctx, f":no_entry:sign: this user is not in a voice channel.")
            await refund(user,ctx)
        if channel is not None and User.voice.mute == False:
            await User.edit(mute=True)
            await create_embed_without_title(ctx, f"{User.display_name} has been muted.")
        elif User.voice.mute == True:
            await create_embed_without_title(ctx, f"{User.display_name} is already muted.")
            await refund(user, ctx)
        else:
            await create_embed_without_title(ctx, f":no_entry:sign: this user is not in a voice channel.")
            await refund(user, ctx)

    @commands.command()
    @commands.bot_has_permissions(mute_members=True)
    @pricing()
    async def unmute(self, ctx, User: discord.Member = None):
        """Unmutes a user."""
        if User is None:
            User = ctx.author
        if User.voice.channel is not None and User.voice.mute == True:
            await User.edit(mute=False)
            await create_embed_without_title(ctx, f"{User.display_name} has been unmuted.")
        elif User.voice.mute == False:
            await create_embed_without_title(ctx, f"{User.display_name} is already unmuted.")
            await refund(ctx.author, ctx)
        else:
            await create_embed_without_title(ctx, f":no_entry:sign: this user is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.hybrid_command(name="implode", aliases=["disconnectAll", "dcAll", "dcall"], brief="Disconnects all users from their voice channels.", usage="implode", description="Disconnects all users from their voice channels.")
    @commands.bot_has_permissions(move_members=True)
    @pricing()
    async def implode(self, ctx):
        """Disconnects all users from their voice channels."""
        user = ctx.author
        channel = user.voice.channel if user.voice else None
        if channel is not None:
            for member in channel.members:
                await member.move_to(None)
        else:
            await create_embed_without_title(ctx, f":no_entry:sign: {ctx.author.display_name} is not in a voice channel.")
            await refund(user, ctx)

    @commands.command()
    @commands.bot_has_permissions(manage_channels=True)
    @pricing()
    async def tirarRadinho(self, ctx):
        """Removes the radio effect from the voice channel."""
        user = ctx.author
        channel = user.voice.channel
        if user.voice.channel is not None:
            await channel.edit(bitrate = 64000)
        else:
            await create_embed_without_title(ctx, f":no_entry:sign: {ctx.author.display_name} is not in a voice channel.")
            await refund(user, ctx)

    @commands.hybrid_command(name="deafen", brief="Deafens the specified user.", usage="[user]", description="Unmutes all users in the voice channel of the author of the command.")
    @commands.bot_has_permissions(deafen_members=True)
    @pricing()
    async def deafen(self, ctx, user: discord.Member=None):
        """Deafens a user."""
        if user is None:
            user = ctx.author
        if user.voice.channel is not None and user.voice.deaf == False:
            await user.edit(deafen=True)
            await create_embed_without_title(ctx, f"{user.display_name} has been deafened.")
        elif user.voice.deaf == True:
            await create_embed_without_title(ctx, f"{user.display_name} is already deafened.")
            await refund(ctx.author, ctx)
        else:
            await create_embed_without_title(ctx, f":no_entry:sign: this user is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.command()
    @commands.bot_has_permissions(deafen_members=True)
    @pricing()
    async def undeafen(self, ctx, User: discord.Member = None):
        """Undeafens a user."""
        if User is None:
            User = ctx.author
        if User.voice.channel is not None and User.voice.deaf == True:
            await User.edit(deafen=False)
            await create_embed_without_title(ctx, f"{User.display_name} has been undeafened.")
        elif User.voice.deaf == False:
            await create_embed_without_title(ctx, f"{User.display_name} is already undeafened.")
            await refund(ctx.author, ctx)
        else:
            await create_embed_without_title(ctx, f":no_entry:sign: this user is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.command()
    @commands.bot_has_permissions(move_members=True)
    @pricing()
    async def disconnect(self, ctx, User: discord.Member):
        """Disconnects a user from their voice channel."""
        if User.voice.channel is not None:
            await User.move_to(None)
            await create_embed_without_title(ctx, f"{User.display_name} has been disconnected.")
        else:
            await create_embed_without_title(ctx, f":no_entry:sign: this user is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.command()
    @commands.bot_has_permissions(move_members=True)
    @pricing()
    async def prison(self, ctx, User:discord.Member):
        """Imprisons a user for 60 seconds."""
        if User.voice is None or User.voice.channel is None:
            await create_embed_without_title(ctx, f":no_entry:sign: {User.display_name} is not in a voice channel.")
            await refund(ctx.author, ctx)
            return
        await create_embed_without_title(ctx, f":chains: {User.display_name} has been imprisoned for 60 seconds.")
        self.prisioner[User.id] = 60
        await self.prision_counter(ctx, User, 60)
            
    async def prision_counter(self, ctx, User: discord.Member, time: int):
        """Counts down the time a user is in prison."""
        server = ctx.guild
        channel_name = "Prisão"
        channels = ctx.guild.channels
        prison_channel = discord.utils.get(channels, name=channel_name)
        if prison_channel is None:
            prison_channel = await server.create_voice_channel(channel_name)
        if User.voice and User.voice.channel:
            await User.move_to(prison_channel)
            if time > 0:
                await asyncio.sleep(1)
                self.prisioner[User.id] = time - 1
                await self.prision_counter(ctx, User, time - 1)
            else:
                await prison_channel.delete()
                
    @commands.command()
    @commands.bot_has_permissions(move_members=True)
    @pricing()
    async def fling(self, ctx, User: discord.Member):
        """Throws a user to a random voice channel."""
        if User.voice is not None:
            channelVet = [channel for channel in User.guild.voice_channels if channel != User.voice.channel]
            if not channelVet:
                await create_embed_without_title(ctx, f":no_entry:sign: There are no voice channels to throw the user to.")
            else:
                channel = choice(channelVet)
                if channel == User.voice.channel:
                    self.fling(ctx, User)
                else:
                    await User.move_to(channel)
                    await create_embed_without_title(ctx, f"{User.display_name} has been thrown to {channel.name}.")
        else:
            await create_embed_without_title(ctx, f":no_entry:sign: {User.display_name} is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.command()
    @commands.bot_has_permissions(move_members=True)
    @pricing()
    async def detonate(self, ctx):
        """Disconnects all users from their voice channels."""
        for vc in ctx.author.guild.voice_channels:
            for membros in vc.members:
                await membros.move_to(None)
        await create_embed_without_title(ctx, f"All users have been disconnected from their voice channels.")

    @commands.command("shuffle")
    @commands.bot_has_permissions(move_members=True)
    @pricing()
    async def shuffle(self, ctx):
        """Throws all users to random voice channels."""
        channelVet = [channel for channel in ctx.author.guild.voice_channels]
        if not channelVet:
            await create_embed_without_title(ctx, f":no_entry:sign: There are no voice channels to throw the users to.")
        else:
            for vc in channelVet:
                for membros in vc.members:
                    await membros.move_to(choice(channelVet))
        await create_embed_without_title(ctx, f"All users have been thrown to random voice channels.")
    
    @commands.command("emergency")
    @commands.bot_has_permissions(move_members=True)
    @pricing()
    async def emergency(self, ctx):
        """Throws all users to the voice channel of the author of the command."""
        for vc in ctx.author.guild.voice_channels:
            for membros in vc.members:
                authorchannel = ctx.author.voice.channel
                if authorchannel is not None:
                    await membros.move_to(authorchannel)
                else:
                    refund(ctx.author, ctx)
                    await create_embed_without_title(ctx, f":no_entry:sign: {ctx.author.display_name} is not in a voice channel.")
        await create_embed_without_title(ctx, f"All users have been thrown to {ctx.author.voice.channel.name}.")
    
    @commands.command("fish")
    @commands.bot_has_permissions(move_members=True)
    @pricing()
    async def fish(self, ctx, User: discord.Member):
        """Throws a user to the voice channel of the author of the command."""
        if User.voice is not None and ctx.author.voice is not None:
            await User.move_to(ctx.author.voice.channel)
            await create_embed_without_title(ctx, f"{User.display_name} has been thrown to {ctx.author.voice.channel.name}.")
        else:
            await create_embed_without_title(ctx, f":no_entry:sign: {User.display_name} or {ctx.author.display_name} is not in a voice channel.")
            await refund(ctx.author, ctx)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @pricing()
    async def kick(self, ctx, User: discord.Member):
        """Kicks a user."""
        if User.id == ctx.author.id:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't kick yourself.")
                await refund(ctx.author, ctx) 
                return
        await User.kick()
        await create_embed_without_title(ctx, f"{User.display_name} was kicked.")
     
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @pricing()
    async def ban(self, ctx, User: discord.Member):
        """Bans a user."""
        if User.id == ctx.author.id:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't ban yourself.")
                await refund(ctx.author, ctx)
                return
        await User.ban()
        await create_embed_without_title(ctx, f"{User.display_name} was banned.")

    @commands.command("changeNickname")
    @commands.has_permissions(manage_nicknames=True)
    @pricing()
    async def change_nickname(self, ctx, User: discord.Member, *nickname: str):
        """Changes a user's nickname."""
        if User.id == ctx.me.id:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, i can't change my own nickname.")
            await refund(ctx.author, ctx)
            return
        else:
            nickname = " ".join(nickname)
            await User.edit(nick=nickname)
            await create_embed_without_title(ctx, f"{User.display_name}'s nickname has been changed to {nickname}.")

    @commands.command()
    @pricing()
    async def nuke(self, ctx):
        """Nuke the database."""
        Usuario.resetAll()
        await create_embed_without_title(ctx, ":radioactive: All users have been set back to 0 eggbux and have lost their titles.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @pricing()
    async def purge(self, ctx, amount: int):
        """Deletes a certain amount of messages."""
        if amount > 0 and amount <= 25:
            await ctx.channel.purge(limit=amount + 1)
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, please enter a number between 1 and 25.", "")
            await refund(ctx.author, ctx)  

    @commands.command()
    @commands.bot_has_permissions(mute_members=True, deafen_members=True)
    @pricing()
    async def god(self, ctx):
        """Makes the user never being able to get muted and deafened."""
        user = ctx.author
        if user not in self.gods:
            self.gods.append(ctx.author)
            await create_embed_without_title(ctx, f"{ctx.author.display_name} has been added to the divine beings.")
        elif user in self.gods:
            await create_embed_without_title(ctx, f"{ctx.author.display_name} is already a divine being.")
            await refund(user, ctx)

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
            
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()
        print("Hostile commands are ready!")

async def setup(bot):
    await bot.add_cog(HostileCommands(bot))