"""
This module contains core functionalities of the bot.
"""
from discord.ext import commands
from lib import *
from db import BotConfig
from tools import refund
from logs import log_info, log_critical, log_error
from resources import Prices
from discord.ext.commands import Context
import discord.ext.commands.errors
import asyncio
import discord
import sys
import os

__all__ = ['BotCore']

class BotCore(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def restart_client(self) -> None:
        """
        Restarts the bot.

        Returns:
            None
        """
        try:
            log_info("Restarting bot...")
            await self.cancel_all_async_tasks()
            await self.bot.close()
            log_info("Bot has been restarted.")
            command = [sys.executable, 'main.py'] + sys.argv[1:]
            os.execv(sys.executable, command)
        except Exception as e:
            log_critical(f"Error restarting bot: {e}")

    async def cancel_all_async_tasks(self) -> None:
        """
        Cancel all running async tasks.

        Returns:
            None
        """
        tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                log_error(f"Error cancelling async task: {e}")
        log_info("All async tasks have been cancelled.")

    @commands.command("r", aliases=["restart"])
    async def force_restart(self, ctx: Context) -> None:
        """
        Force restarts the bot.

        Args:
            ctx (Context): The context of the command.
        """
        if await is_dev(ctx.author.id):
            await send_bot_embed(ctx, description=":warning: Restarting...")
            log_info(f"{ctx.author.name}, user id: {ctx.author.id} has attempted to restart the bot.")
            await self.restart_client()
    
    async def tutorial(self, target: discord.Guild) -> None:
        """
        Sends a tutorial message to the user. This function is called whenever the bot joins a new guild.

        Args:
            target (discord.Guild): The guild to send the tutorial to.

        Returns:
            None
        """
        embed = await make_embed_object(title=":wave: Thanks for inviting me!", description="I'm a bot with multiple commands and customizations options. Type **!help** for a documentation link for a more detailed description. \nTo configure me in your server, you have to follow these steps:\n1. Type **!setChannel** in the channel where you want me to listen for commands.\n2. Type **!modules** to visualize the modules available. \n3. Type **!setmodule** to select a module you desire.\n4. Type **!setPrefix** to select the prefix of the bot. My default prefix is **!**.\n5. Have fun! :tada:")
        owner = target.owner
        if owner:
            try:
                await owner.send(embed=embed)
            except discord.Forbidden:
                for channel in target.text_channels:
                    if channel.permissions_for(target.me).send_messages:
                        await channel.send(embed=embed)
        else:
            pass
        
    async def log_and_raise_error(self, ctx: Context, error: Exception) -> None:
        """
        Logs the error, raises it and notifies the developers.

        Args:
            ctx (Context): The context of the command.
            error (Exception): The error that occurred.

        Returns:
            None
        """
        log_error(f"Error in command: {ctx.command.name}\n In server: {ctx.guild.name}\n In channel: {ctx.channel.name}\n By user: {ctx.author.name}\n", error)
        devs = dev_list()
        await self.handle_exception(ctx, error)
        user = self.bot.get_user(int(devs[0]))
        if user:
            msg = await make_embed_object(description=f":no_entry_sign: **{error}** a command has failed. The developers have been notified.")
            await user.send(embed=msg)
        raise error
    
    async def handle_exception(self, ctx: Context, error: Exception) -> None:
        """
        Handles the exception and sends a message to the user.

        Args:
            ctx (Context): The context of the command.
            error (Exception): The error that occurred.
        
        Returns:
            None
        """
        emoji_name = ":no_entry_sign:"
        description = await self.get_exception_message(error)
        error_message = f"{emoji_name} {description}"
        if await cooldown_user_tracker(ctx.author.id):
            await send_bot_embed(ctx, description=error_message)
            return
        return
    
    async def get_exception_message(self, error: Exception) -> str:
        """
        Gets the exception message.

        Args:
            error (Exception): The error that occurred.

        Returns:
            str
        """
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if isinstance(error, commands.CommandNotFound):
            return "Command not found."
        
        if isinstance(error, (commands.MemberNotFound, commands.UserNotFound)):
            return "Member not found."
        
        if isinstance(error, commands.MissingRequiredArgument):
            return "Missing required argument."
        
        if isinstance(error, commands.BadArgument):
            return "Bad argument."
        
        if isinstance(error, commands.TooManyArguments):
            return "Too many arguments."
    
        return "Oops! Something went wrong."

    async def refund_price_command_on_error(self, ctx) -> None:
        """
        Refunds the user if the command has a price and the command has failed.

        Args:
            ctx (Context): The context of the command.

        Returns:
            None
        """
        if ctx.command.name in Prices.__members__ and ctx.command.name != ("stealpoints") and Prices.__members__[ctx.command.name].value > 0:
            await refund(ctx.author, ctx)
            return
        
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self.tutorial(guild)
        await BotConfig.create(guild.id)
        log_info(f"Joined guild {guild.name}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        await BotConfig.delete(guild.id)
        log_info(f"Left guild {guild.name}")
    
    @commands.Cog.listener()
    async def guild_channel_delete(self, channel: discord.TextChannel) -> None:
        guild_cache = await guild_cache_retriever(channel.guild.id)
        channel_cache = guild_cache.get('channel_id')
        if channel_cache and channel_cache == channel.id:
            await BotConfig.update_channel_id(channel.guild.id, None)
            log_info(f"Channel {channel.name} has been deleted. Commands channel has been reset.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: Exception) -> None:
        config_data = await guild_cache_retriever(ctx.guild.id)
        if config_data and config_data['toggled_modules'] == "N":
            return
        if isinstance(error, commands.CommandError) and not isinstance(error, commands.CommandNotFound):
            if ctx is not None and ctx.command is not None:
                if not isinstance(error, (commands.CommandOnCooldown, commands.CheckFailure)):
                    await self.refund_price_command_on_error(ctx)
                    await self.log_and_raise_error(ctx, error)
                    return
                        
async def setup(bot):
    await bot.add_cog(BotCore(bot))