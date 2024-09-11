from discord.ext import commands
from dotenv import load_dotenv
from tools.shared import send_bot_embed, make_embed_object, is_dev, make_embed_object, dev_list, guild_cache_retriever, cooldown_user_tracker
from db.botConfigDB import BotConfig
from tools.cache import cache_initiator
from tools.pointscore import refund
from tools.prices import Prices
from tools.helpSelect import ShowPointsModules
from colorlog import ColoredFormatter
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
        load_dotenv()
        self.bot = bot
        self.logger = self.setup_logging()
        self.last_cooldown_message_time = {}

    def setup_logging(self) -> logging.Logger:
        logger = logging.getLogger('botcore')
        logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)-8s%(reset)s - %(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "purple",
            },
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    async def restart_client(self) -> None:
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
        """Close all aiohttp ClientSession instances."""
        if hasattr(self.bot, "http_session") and self.bot.http_session:
            try:
                await self.bot.http_session.close()
                logger.info("Aiohttp session has been closed.")
            except Exception as e:
                logger.error(f"Error closing aiohttp session: {e}")

    async def cancel_all_async_tasks(self) -> None:
        """Cancel all running async tasks."""
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
        """Restart the bot."""
        if is_dev(ctx):
            await send_bot_embed(ctx, description=":warning: Restarting...")
            logger.info(f"{ctx.author.name}, user id: {ctx.author.id} has attempted to restart the bot.")
            await self.restart_client()

    async def restart_every_day(self) -> None:
        while True:
            await asyncio.sleep(86400)
            await self.restart_client()
    
    async def tutorial(self, target: discord.Guild) -> None:
        """Sends a tutorial message to the user."""
        embed = await make_embed_object(title=":wave: Thanks for inviting me!", description="I'm a bot with multiple commands and customizations options. Type **!help** to visualize every command i have to offer. \nTo configure me in your server, you have to follow these steps:\n1. Type **!setChannel** in the channel where you want me to listen for commands.\n2. Type **!modules** to visualize the modules available. \n3. Type **!setmodule** to select a module you desire.\n4. Type **!setPrefix** to select the prefix of the bot. My default prefix is **!**.\n5. Have fun! :tada:")
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
        
    @commands.command("setModule", aliases=["setM"])
    async def set_module(self, ctx: Context) -> None:
        """Set the module where the bot will pick commands from."""
        guild_data = await guild_cache_retriever(ctx.guild.id)
        if ctx.author.id == ctx.guild.owner_id:
            embed = await make_embed_object(title="**:gear: MODULES:**", description="1. :infinity: **Total**\n2. :star: **Friendly**\n3. :gun: **Hostiles**\n4. :x: **None**\n\n**Important note**: \n**Friendly module:** contains Chicken commands, bank commands, interactive commands, AI commands and friendly commands and activates users gaining one currency every 10 seconds during call-time.\n**Hostile module:** contains hostile commands, bank commands and activates users gaining one currency every 10 seconds during call-time.\n\nSelect one of the modules to enable/disable it.")
            view = ShowPointsModules(ctx.author.id, guild_data)
            await ctx.send(embed=embed, view=view)
        else:
            embed = await make_embed_object(description=":no_entry_sign: You don't have the necessary permissions to use this command.")
            await ctx.author.send(embed=embed)

    @commands.command("setPrefix", aliases=["setP"])
    async def set_prefix(self, ctx: Context, prefix: str) -> None:
        """Set the prefix for the bot."""
        if ctx.author.guild_permissions.administrator:
            if len(prefix) > 1:
                await send_bot_embed(ctx, description=":no_entry_sign: The prefix can't have more than one character.")
                return
            BotConfig.update_prefix(ctx.guild.id, prefix)
            await send_bot_embed(ctx, description=f":white_check_mark: Prefix has been set to **{prefix}**.")
        else:
            embed = await make_embed_object(description=":no_entry_sign: You don't have the necessary permissions to use this command.")
            await ctx.author.send(embed=embed)
    
    @staticmethod
    async def get_prefix_for_guild(_, message: discord.Message = None) -> str:
     """Get the prefix for the guild."""
     if message:
        if not message.guild:
            return "!"
        guild_id = message.guild.id
        guild_data = await guild_cache_retriever(guild_id)
        return guild_data['prefix']
            
    @commands.command("setChannel", alias=["setC"])
    async def set_channel(self, ctx: Context) -> None:
        """Set the channel where the bot will listen for commands."""
        if ctx.author.guild_permissions.administrator:
            BotConfig.update_channel_id(ctx.guild.id, ctx.channel.id)
            await send_bot_embed(ctx, description=":white_check_mark: Commands channel has been set.")
        else:
            embed = await make_embed_object(description=":no_entry_sign: You don't have the necessary permissions to use this command.")
            await ctx.author.send(embed=embed)

    async def log_and_raise_error(self, ctx: Context, error: Exception) -> None:
        logger.error(f"Error in command: {ctx.command.name}\n In server: {ctx.guild.name}\n In channel: {ctx.channel.name}\n By user: {ctx.author.name}\n Error: {error} \n Type: {type(error)}")
        devs = dev_list()
        await self.handle_exception(ctx, error)
        user = self.bot.get_user(int(devs[0]))
        if user:
            msg = await make_embed_object(description=f":no_entry_sign: **{error}** a command has failed. The developers have been notified.")
            await user.send(embed=msg)
        raise error
    
    async def handle_exception(self, ctx: Context, error: Exception) -> None:
        description = f":no_entry_sign: An error has occured while executing the command. {error}"
        if await cooldown_user_tracker(ctx.author.id):
            await send_bot_embed(ctx, description=description)
            return
        return
    
    async def verify_error_type(self, error):
        if isinstance(error, error.MissingPermissions):
            return True

    async def refund_price_command_on_error(self, ctx) -> None:
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
                
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await cache_initiator.start_cache_clearing_for_users()
            await cache_initiator.start_cache_clearing_for_guilds()
            await self.restart_every_day()
    
async def setup(bot):
    await bot.add_cog(BotCore(bot))