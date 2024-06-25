from discord.ext import commands
from db.botConfigDB import BotConfig
from tools.embed import create_embed_without_title
from tools.helpSelect import SelectModule
import discord
import asyncio
import os
import sys

class PointsConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command("togglePoints")
    async def toggle_points(self, ctx):
        """Enable or disable the points commands."""
        if BotConfig.read(ctx.guild.id):
            if ctx.guild.owner_id == ctx.author.id:
                if BotConfig.read(ctx.guild.id)['toggle']:
                    BotConfig.update_toggle_value(ctx.guild.id, False)
                    await create_embed_without_title(ctx, ":warning: Points commands are now disabled.")
                else:
                    BotConfig.update_toggle_value(ctx.guild.id, True)
                    await create_embed_without_title(ctx, ":white_check_mark: Points commands are now enabled.")
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you do not have permission to do this.")
        else:
            BotConfig.create(ctx.guild.id, True, None)
            await create_embed_without_title(ctx, ":white_check_mark: Points commands are now enabled.")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Points commands are ready!")

async def setup(bot):
    await bot.add_cog(PointsConfig(bot))
