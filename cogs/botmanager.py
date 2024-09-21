from discord.ext import commands
from discord.ext.commands import Context
from db.botconfigdb import BotConfig
from tools.shared import guild_cache_retriever
from tools.shared import make_embed_object, send_bot_embed
from tools.helpSelect import ShowPointsModules
import discord
import logging
from colorlog import ColoredFormatter


class BotManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.setup_logging()

    def setup_logging(self) -> logging.Logger:
        """
        Setup the logging for the bot.

        Returns:
            logging.Logger
        """
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

    @commands.command("setModule", aliases=["setM"])
    async def set_module(self, ctx: Context) -> None:
        """
        Set the module where the bot will pick commands from.

        Args:
            ctx (Context): The context of the command.
        
        Returns:
            None
        """
        guild_data = await guild_cache_retriever(ctx.guild.id)
        if ctx.author.id == ctx.guild.owner_id:
            embed = await make_embed_object(title="**:gear: MODULES:**", description="1. :infinity: **Total**\n2. 🐣 **Chickens**\n3. 🪩 **Interactives**\n4. :x: **None**\n\n**Important note**: \nSelect one of the modules to enable.")
            view = ShowPointsModules(ctx.author.id, guild_data)
            await ctx.send(embed=embed, view=view)
        else:
            embed = await make_embed_object(description=":no_entry_sign: You don't have the necessary permissions to use this command.")
            await ctx.author.send(embed=embed)

    @commands.command("setPrefix", aliases=["setP"])
    async def set_prefix(self, ctx: Context, prefix: str) -> None:
        """
        Set the prefix for the bot.

        Args:
            ctx (Context): The context of the command.
            prefix (str): The prefix to set.

        Returns:
            None
        """
        if ctx.author.guild_permissions.administrator:
            if len(prefix) > 3:
                await send_bot_embed(ctx, description=":no_entry_sign: The prefix can't have more than 3 characters.")
                return
            await BotConfig.update_prefix(ctx.guild.id, prefix)
            await send_bot_embed(ctx, description=f":white_check_mark: Prefix has been set to **{prefix}**.")
        else:
            embed = await make_embed_object(description=":no_entry_sign: You don't have the necessary permissions to use this command.")
            await ctx.author.send(embed=embed)
    
    @staticmethod
    async def get_prefix_for_guild(_, message: discord.Message = None) -> str:
     """
     Get the prefix for the guild.

    Args:
        message (discord.Message): The message object.

    Returns:
        str
     """
     if message and message.guild:        
        guild_id = message.guild.id
        guild_data = await guild_cache_retriever(guild_id)
        return guild_data['prefix']
            
    @commands.command("setChannel", alias=["setC"])
    async def set_channel(self, ctx: Context) -> None:
        """
        Set the channel where the bot will listen for commands.

        Args:
            ctx (Context): The context of the command.

        Returns:
            None
        """
        if ctx.author.guild_permissions.administrator:
            await BotConfig.update_channel_id(ctx.guild.id, ctx.channel.id)
            await send_bot_embed(ctx, description=":white_check_mark: Commands channel has been set.")
        else:
            embed = await make_embed_object(description=":no_entry_sign: You don't have the necessary permissions to use this command.")
            await ctx.author.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BotManager(bot))
