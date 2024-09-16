"""
This module contains the core of the bot, performing essential functions.
"""

from discord.ext import commands, tasks
from tools.shared import *
from db.botconfigdb import BotConfig
from tools.cache import cache_initiator
from tools.pointscore import refund
from tools.prices import Prices
from tools.listeners import listener_manager
from discord.ext.commands import Context
import discord.ext.commands.errors
import logging
import asyncio
import discord
import sys
import os
logger = logging.getLogger('botcore')


class BotCore(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cache_task.start()
        self.listener_task.start()

    async def restart_client(self) -> None:
        """
        Restarts the bot.

        Returns:
            None
        """
        try:
            logger.info("Restarting bot...")
            await self.cancel_all_async_tasks()
            await self.close_aiohttp_sessions()
            await self.bot.close()
            await asyncio.sleep(4)
            logger.info("Bot has been restarted.")
            command = [sys.executable, 'main.py'] + sys.argv[1:]
            os.execv(sys.executable, command)
        except Exception as e:
            logger.critical(f"Error restarting bot: {e}")

    async def close_aiohttp_sessions(self) -> None:
        """
        Close all aiohttp ClientSession instances.

        Returns:
            None
        """
        if hasattr(self.bot, "http_session") and self.bot.http_session:
            try:
                await self.bot.http_session.close()
                logger.info("Aiohttp session has been closed.")
            except Exception as e:
                logger.error(f"Error closing aiohttp session: {e}")

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
                logger.error(f"Error cancelling async task: {e}")
        logger.info("All async tasks have been cancelled.")

    @commands.command("r", aliases=["restart"])
    async def force_restart(self, ctx: Context) -> None:
        """
        Force restarts the bot.

        Args:
            ctx (Context): The context of the command.
        """
        if is_dev(ctx):
            await send_bot_embed(ctx, description=":warning: Restarting...")
            logger.info(f"{ctx.author.name}, user id: {ctx.author.id} has attempted to restart the bot.")
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
        logger.error(f"Error in command: {ctx.command.name}\n In server: {ctx.guild.name}\n In channel: {ctx.channel.name}\n By user: {ctx.author.name}\n Error: {error} \n Type: {type(error)}")
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
        description = f":no_entry_sign: Oops! Something went wrong."
        if await cooldown_user_tracker(ctx.author.id):
            await send_bot_embed(ctx, description=description)
            return
        return
    
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
        BotConfig.create(guild.id)
        logger.info(f"Joined guild {guild.name}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        BotConfig.delete(guild.id)
        logger.info(f"Left guild {guild.name}")
    
    @commands.Cog.listener()
    async def guild_channel_delete(self, channel: discord.TextChannel) -> None:
        guild_cache = await guild_cache_retriever(channel.guild.id)
        channel_cache = guild_cache.get('channel_id')
        if channel_cache and channel_cache == channel.id:
            BotConfig.update_channel_id(channel.guild.id, None)
            logger.info(f"Channel {channel.name} has been deleted. Commands channel has been reset.")

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
                          
    @tasks.loop(hours=1)
    async def cache_task(self) -> None:
        """
        Periodically clears the cache.

        Returns:
            None
        """
        await cache_initiator.start_cache_clearing_for_users()
        await cache_initiator.start_cache_clearing_for_guilds()

    @cache_task.before_loop
    async def before_cache_task(self) -> None:
        """
        Before the cache task starts.

        Returns:
            None
        """
        await self.bot.wait_until_ready()

    @tasks.loop(hours=2)
    async def listener_task(self) -> None:
        """
        Periodically clears the listeners.

        Returns:
            None
        """
        await listener_manager.clear_listeners()

    @listener_task.before_loop
    async def before_listener_task(self) -> None:
        """
        Before the listener task starts.

        Returns:
            None
        """
        await self.bot.wait_until_ready()
    
async def setup(bot):
    await bot.add_cog(BotCore(bot))