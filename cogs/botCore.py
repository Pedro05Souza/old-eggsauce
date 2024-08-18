from discord.ext import commands
from dotenv import load_dotenv
from tools.shared import send_bot_embed, make_embed_object, is_dev, make_embed_object, dev_list, guild_cache_retriever
from db.botConfigDB import BotConfig
from tools.cache.init import cache_initiator
from tools.pointscore import refund
from tools.prices import Prices
from tools.helpSelect import SelectModule, ShowPointsModules
from colorlog import ColoredFormatter
import logging
import asyncio
import sys
import os
logger = logging.getLogger('botcore')
monitor_mode = False

class BotCore(commands.Cog):
    def __init__(self, bot):
        load_dotenv()
        self.bot = bot
        self.logger = self.setup_logging()
        self.last_cooldown_message_time = {}

    def setup_logging(self):
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

    async def restart_client(self):
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

    async def close_aiohttp_sessions(self):
        """Close all aiohttp ClientSession instances."""
        if hasattr(self.bot, "http_session") and self.bot.http_session:
            try:
                await self.bot.http_session.close()
                logger.info("Aiohttp session has been closed.")
            except Exception as e:
                logger.error(f"Error closing aiohttp session: {e}")

    async def cancel_all_async_tasks(self):
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
    async def force_restart(self, ctx):
        """Restart the bot."""
        if is_dev(ctx):
            await send_bot_embed(ctx, description=":warning: Restarting...")
            logger.info(f"{ctx.author.name}, user id: {ctx.author.id} has attempted to restart the bot.")
            await self.restart_client()

    async def restart_every_day(self):
        while True:
            await asyncio.sleep(86400)
            await self.restart_client()
    
    async def tutorial(self, target):
        """Sends a tutorial message to the user."""
        embed = await make_embed_object(title=":wave: Thanks for inviting me!", description="I'm a bot with multiple commands and customizations options. Type **!help** to visualize every command i have to offer. \nTo configure me in your server, you have to follow these steps:\n1. Type **!setChannel** in the channel where you want me to listen for commands.\n2. Type **!modules** to visualize the modules available. \n3. Type **!setmodule** to select a module you desire.\n4. Type **!setPrefix** to select the prefix of the bot.\n5. Have fun! :tada:")
        for channel in target.text_channels:
            if channel.permissions_for(target.me).send_messages:
                await channel.send(embed=embed)
                break
            
    @commands.hybrid_command("modules", brief="Displays the modules available to the user.", usage="modules")
    async def modules(self, ctx):
        """Displays a list of commands available to the user."""
        if ctx.author.id == ctx.guild.owner_id:
            Embed = await make_embed_object(title="**:gear: BOT MODULES:**", description=":egg: **Points**: Fun and unique economy system, has sub-Modules.\n:tools: **Utility**: Useful commands for everyday use.\nSelect one of the modules to see a better description.")
            view = SelectModule(ctx.author.id)
            await ctx.send(embed=Embed, view=view)
        else:
            embed = await make_embed_object(description=":no_entry_sign: You don't have the necessary permissions to use this command.")
            await ctx.author.send(embed=embed)
    
    @commands.command("setModule", aliases=["setM"])
    async def set_module(self, ctx):
        """Set the module where the bot will pick commands from."""
        guild_data = await guild_cache_retriever(ctx.guild.id)
        if guild_data:
            if ctx.author.id == ctx.guild.owner_id:
                embed = await make_embed_object(title="**:gear: MODULES:**", description="1. :infinity: **Total**\n2. :star: **Friendly**\n3. :gun: **Hostiles**\n4. :x: **None**\n\n**Important note**: \n**Friendly module:** contains Chicken commands, bank commands, interactive commands, AI commands and friendly commands and activates users gaining one currency every 10 seconds during call-time.\n**Hostile module:** contains hostile commands, bank commands and activates users gaining one currency every 10 seconds during call-time.\n\nSelect one of the modules to enable/disable it.")
                view = ShowPointsModules(ctx.author.id)
                await ctx.send(embed=embed, view=view)
            else:
                embed = await make_embed_object(description=":no_entry_sign: You don't have the necessary permissions to use this command.")
                await ctx.author.send(embed=embed)
        else:
            BotConfig.create(ctx.guild.id)
            await send_bot_embed(ctx, description=":warning: The bot wasn't registered in this server. Try again.")

    @commands.command("setPrefix", aliases=["setP"])
    async def set_prefix(self, ctx, prefix: str):
        """Set the prefix for the bot."""
        guild_data = await guild_cache_retriever(ctx.guild.id)
        if guild_data:
            if ctx.author.guild_permissions.administrator:
                if len(prefix) > 1:
                    await send_bot_embed(ctx, description=":no_entry_sign: The prefix can't have more than one character.")
                    return
                BotConfig.update_prefix(ctx.guild.id, prefix)
                await send_bot_embed(ctx, description=f":white_check_mark: Prefix has been set to **{prefix}**.")
            else:
                embed = await make_embed_object(description=":no_entry_sign: You don't have the necessary permissions to use this command.")
                await ctx.author.send(embed=embed)
        else:
            BotConfig.create(ctx.guild.id, prefix=prefix)
            await send_bot_embed(ctx, description=f":white_check_mark: Prefix has been set to **{prefix}**.")
    
    @staticmethod
    async def get_prefix_for_guild(bot, message):
     """Get the prefix for the guild."""
     if message:
        guild_id = message.guild.id
        guild_data = await guild_cache_retriever(guild_id)
        if guild_data:
            if not guild_data['prefix']:
                return "!"
            return guild_data['prefix']
            
    @commands.command("setChannel", alias=["setC"])
    async def set_channel(self, ctx):
        """Set the channel where the bot will listen for commands."""
        guild_data = await guild_cache_retriever(ctx.guild.id)
        if guild_data:
            if ctx.author.guild_permissions.administrator:
                BotConfig.update_channel_id(ctx.guild.id, ctx.channel.id)
                await send_bot_embed(ctx, description=":white_check_mark: Commands channel has been set.")
            else:
                embed = await make_embed_object(description=":no_entry_sign: You don't have the necessary permissions to use this command.")
                await ctx.author.send(embed=embed)
        else:
            BotConfig.create(ctx.guild.id, None, ctx.channel.id)
            await send_bot_embed(ctx, description=":white_check_mark: Commands channel has been set.")

    async def log_and_raise_error(self, ctx, error):
        logger.error(f"Error in command: {ctx.command.name}\n In server: {ctx.guild.name}\n In channel: {ctx.channel.name}\n By user: {ctx.author.name}\n Error: {error} \n Type: {type(error)}")
        devs = dev_list()
        user = self.bot.get_user(int(devs[1]))
        if user:
            msg = await make_embed_object(description=f":no_entry_sign: **{error}** a command has failed. The developers have been notified.")
            await user.send(embed=msg)
        raise error

    async def refund_price_command_on_error(self, ctx, error):
        if ctx.command.name in Prices.__members__ and ctx.command.name != ("stealpoints") and Prices.__members__[ctx.command.name].value > 0:
            await send_bot_embed(ctx, description=f":no_entry_sign: {error} The {ctx.command.name} command has been cancelled and refunded.")
            await refund(ctx.author, ctx)
            return
        
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.tutorial(guild)
        BotConfig.create(guild.id)
        logger.info(f"Joined guild {guild.name}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        BotConfig.delete(guild.id)
        logger.info(f"Left guild {guild.name}")
    
    @commands.Cog.listener()
    async def guild_channel_delete(self, channel):
        if BotConfig.read(channel.guild.id)['channel_id'] == channel.id:
            BotConfig.update_channel_id(channel.guild.id, 0)
            logger.info(f"Channel {channel.name} has been deleted. Commands channel has been reset.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        config_data = await guild_cache_retriever(ctx.guild.id)
        if config_data and config_data['toggled_modules'] == "N":
            return
        if isinstance(error, commands.CommandError) and not isinstance(error, commands.CommandNotFound):
            if ctx is not None and ctx.command is not None:
                if isinstance(error, commands.CheckFailure):
                    if hasattr(ctx, "predicate_result") and ctx.predicate_result:
                        await self.refund_price_command_on_error(ctx, error)
                        return
                elif isinstance(error, commands.CommandOnCooldown):
                     pass
                else:
                    await self.log_and_raise_error(ctx, error)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if monitor_mode:
            logger.info(f"Command {ctx.command.name} has been executed by {ctx.author.name} in {ctx.guild.name} in {ctx.channel.name}")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync() # only sync if code modified
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await cache_initiator.start_cache_clearing_for_users()
            await cache_initiator.start_cache_clearing_for_guilds()
            await self.restart_every_day()

async def setup(bot):
    await bot.add_cog(BotCore(bot))