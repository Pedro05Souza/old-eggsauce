import os
from discord.ext import commands
from dotenv import load_dotenv
import discord
import asyncio
import sys
from tools.embed import create_embed_without_title
from db.botConfigDB import BotConfig
from tools.helpSelect import SelectModule

class BotSys(commands.Cog):
    def __init__(self, bot):
        load_dotenv()
        self.bot = bot
        self.devs = os.getenv("DEVS").split(",")

    async def restart_client(self):
        try:
            print("Attempting to restart the bot...")
            await self.close_aiohttp_sessions()
            await self.cancel_all_async_tasks()
            await self.bot.close()
            command = [sys.executable, 'main.py'] + sys.argv[1:]
            await asyncio.sleep(2)
            print("Bot has been restarted.")
            os.execv(sys.executable, command)
        except Exception as e:
            print(e)

    async def close_aiohttp_sessions(self):
        """Close all aiohttp ClientSession instances."""
        if hasattr(self.bot, "http_session"):
            await self.bot.http_session.close()

    async def cancel_all_async_tasks(self):
        """Cancel all running async tasks."""
        for task in asyncio.all_tasks():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    @commands.command("r", aliases=["restart"])
    async def force_restart(self, ctx):
        """Restart the bot."""
        if str(ctx.author.id) in self.devs:
            await create_embed_without_title(ctx, ":warning: Restarting...")
            await self.restart_client()

    async def restart_every_day(self):
        while True:
            await asyncio.sleep(86400)
            await self.restart_client()
    
    async def tutorial(self, target):
        """Sends a tutorial message to the user."""
        message = "Hello! I'm Eggsauce, a bot that has multiple functionalities and is highly customizable. I come with different modules that can be enabled or disabled according to your needs. To get started, type **!modules** to see the list of commands available."
        for channel in target.text_channels:
            if channel.permissions_for(target.me).send_messages:
                await channel.send(message)
                break

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if not BotConfig.read(guild.id):
            await self.tutorial(guild) 
        BotConfig.create(guild.id, True, None)
        self.bot.remove_command("ignore")
        print(f"Joined guild {guild.name}")

    @commands.command("modules")
    async def modules(self, ctx):
        """Displays a list of commands available to the user."""
        Embed = discord.Embed(title="**MODULES:**", description=":egg: **Points**: Fun and interactive economy system, has sub-Modules.\n:tools: **Utility**: Useful commands for everyday use.\nSelect one of the modules to see the commands available and a better explanation of each one.")
        view = SelectModule()
        await ctx.send(embed=Embed, view=view)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if not BotConfig.read(guild.id):
            await self.tutorial(guild)
            BotConfig.create(guild.id, True, None)
            self.bot.remove_command("ignore")
        print(f"Joined guild {guild.name}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        BotConfig.delete(guild.id)
        print(f"Left guild {guild.name}")
    
    @commands.Cog.listener()
    async def guild_channel_delete(self, channel):
        if BotConfig.read(channel.guild.id)['channel_id'] == channel.id:
            BotConfig.update(channel.guild.id, BotConfig.read(channel.guild.id)['toggle'], 0)
            print(f"Channel {channel.name} has been deleted")

    @commands.command("setChannel", alias=["setC"])
    async def set_channel(self, ctx):
        """Set the channel where the bot will listen for commands."""
        if BotConfig.read(ctx.guild.id):
            if ctx.guild.owner_id == ctx.author.id:
                if BotConfig.read(ctx.guild.id)['channel_id']:
                    BotConfig.update_channel_id(ctx.guild.id, ctx.channel.id)
                    await create_embed_without_title(ctx, ":white_check_mark: Commands channel has been set.")
                else:
                    BotConfig.create_channel(ctx.guild.id, ctx.channel.id)
                    await create_embed_without_title(ctx, ":white_check_mark: Commands channel has been set.")
        else:
            BotConfig.create(ctx.guild.id, True, ctx.channel.id)
            await create_embed_without_title(ctx, ":white_check_mark: Commands channel has been set.")
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("bot sys commands are ready!")
        self.bot.loop.create_task(self.restart_every_day())

    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    #     if ToggleDB.read(ctx.guild.id) and not ToggleDB.read(ctx.guild.id)['toggle']:
    #         return
    #     if isinstance(error, commands.CommandError):
    #         if ctx is not None:
    #             if hasattr(ctx, "predicate_result") and ctx.predicate_result:
    #                 enumPricing = Prices.__members__
    #                 if ctx.command.name in enumPricing:
    #                     if enumPricing[ctx.command.name].value > 0:
    #                         await create_embed_without_title(ctx, f":no_entry_sign: {error} The {ctx.command.name} command has been cancelled and refunded.")
    #                         await refund(ctx.author, ctx)
    #     print(error)
async def setup(bot):
    await bot.add_cog(BotSys(bot))