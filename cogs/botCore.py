import os
from discord.ext import commands
from dotenv import load_dotenv
import discord
import asyncio
import sys
from tools.embed import create_embed_without_title, create_embed_with_title, make_embed_object
from db.botConfigDB import BotConfig
from tools.helpSelect import SelectModule, ShowPointsModules

class BotCore(commands.Cog):
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
        tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)

    @commands.command("r", aliases=["restart"])
    async def force_restart(self, ctx):
        """Restart the bot."""
        if str(ctx.author.id) in self.devs:
            await create_embed_without_title(ctx, ":warning: Restarting...")
            await self.restart_client()
        else:
            await create_embed_without_title(ctx, ":skull: Hell naw.")

    async def restart_every_day(self):
        while True:
            await asyncio.sleep(86400)
            await self.restart_client()
    
    async def tutorial(self, target):
        """Sends a tutorial message to the user."""
        embed = await make_embed_object(title=":wave: Thanks for inviting me!", description="I'm a bot with multiple commands and customizations options. To configure me in your server, you have to follow these steps:\n1. Type **!setChannel** in the channel where you want me to listen for commands.\n2. Type **!modules** to visualize the modules available. \n3. Type **!setmodule** to select a module you desire.\n4. Have fun! :tada:")
        for channel in target.text_channels:
            if channel.permissions_for(target.me).send_messages:
                await channel.send(embed=embed)
                break

    @commands.command("cfg")
    async def config(self, ctx):
        """Configures the bot for the server."""
        if not BotConfig.read(ctx.guild.id)['channel_id'] or not BotConfig.read(ctx.guild.id)['toggled_modules']:
            await create_embed_with_title(ctx, title=":gear: Bot config:", description="To configure me, you have to follow these steps:\n1. Type **!setChannel** in the channel where you want me to listen for commands.\n2. Type **!modules** to visualize the modules available.\n3.Type **!setmodule** to pick the option that most fits you. \n4. Have fun! :tada:")
        return

    @commands.hybrid_command("modules", brief="Displays the modules available to the user.", usage="modules")
    async def modules(self, ctx):
        """Displays a list of commands available to the user."""
        if ctx.author.guild_permissions.administrator:
            Embed = await make_embed_object(title="**:gear: BOT MODULES:**", description=":egg: **Points**: Fun and unique economy system, has sub-Modules.\n:tools: **Utility**: Useful commands for everyday use.\nSelect one of the modules to see a better description.")
            view = SelectModule(ctx.author.id)
            await ctx.send(embed=Embed, view=view)
        else:
            embed = await make_embed_object(":no_entry_sign: You don't have the necessary permissions to use this command.")
            await ctx.author.send(embed=embed)
    
    @commands.command("setModule", aliases=["setM"])
    async def set_module(self, ctx):
        """Set the module where the bot will pick commands from."""
        if BotConfig.read(ctx.guild.id):
            if ctx.author.guild_permissions.administrator:
                embed = await make_embed_object(title="**:gear: MODULES:**", description="1. :infinity: **Total**\n2. :star: **Friendly**\n3. :gun: **Hostiles**\n4. :x: **None**\n\nSelect one of the modules to enable/disable it.")
                view = ShowPointsModules(ctx.author.id)
                await ctx.send(embed=embed, view=view)
            else:
                embed = await make_embed_object(description=":no_entry_sign: You don't have the necessary permissions to use this command.")
                await ctx.author.send(embed=embed)
        else:
            BotConfig.create(ctx.guild.id)
            
    @commands.command("setChannel", alias=["setC"])
    async def set_channel(self, ctx):
        """Set the channel where the bot will listen for commands."""
        if BotConfig.read(ctx.guild.id):
            if ctx.author.guild_permissions.administrator:
                BotConfig.update_channel_id(ctx.guild.id, ctx.channel.id)
                await create_embed_without_title(ctx, ":white_check_mark: Commands channel has been set.")
            else:
                embed = await make_embed_object(description=":no_entry_sign: You don't have the necessary permissions to use this command.")
                await ctx.author.send(embed=embed)
        else:
            BotConfig.create(ctx.guild.id, None, ctx.channel.id)
            await create_embed_without_title(ctx, ":white_check_mark: Commands channel has been set.")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.tutorial(guild)
        BotConfig.create(guild.id)
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
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()
        await self.bot.loop.create_task(self.restart_every_day())

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
    await bot.add_cog(BotCore(bot))