import discord
from discord.ext import commands
from discord.ext.commands import Context
from random import choice
from tools.settings import regular_command_cooldown
from tools.pointscore import refund, pricing
from tools.shared import send_bot_embed

class DestructiveHostiles(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

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

async def setup(bot):
    await bot.add_cog(DestructiveHostiles(bot))
