from discord.ext import commands
import discord
from tools.embed import create_embed_without_title
import os
from db.botConfigDB import BotConfig
from db.userDB import Usuario
from tools.pagination import PaginationView
from tools.pricing import Prices
from tools.pricing import pricing
from random import choice

class FriendlyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @pricing()
    async def balls(self, ctx):
        """Bot sends balls."""
        await create_embed_without_title(ctx, f":soccer: balls")

    @commands.command()
    @pricing()
    async def mog(self, ctx, User: discord.Member):
            """Mog a user."""
            path = choice(os.listdir("images/mogged/"))
            await ctx.send(file=discord.File("images/mogged/"+path))
            await ctx.send(f"{User.mention} bye bye 🤫🧏‍♂️")
    
    @commands.command("shop", aliases=["store"])
    @pricing()
    async def shop(self, ctx):
        """Shows the shop."""
        data = []
        for member in Prices.__members__:
            if Prices.__members__[member].value > 0:
                data.append({"title": member, "value": str(Prices.__members__[member].value) + " eggbux"})
        view = PaginationView(data)
        await view.send(ctx, title="Shop", description="Buy commands with your eggbux:", color=0x00ff00)

    @commands.command("leaderboard", aliases=["ranking"])
    @pricing()
    async def leaderboard(self, ctx):
        """Shows the leaderboard."""
        users = Usuario.readAll()
        users = sorted(users, key=lambda x: x['points'], reverse=True)
        guild = ctx.guild
        data = []
        for i in users:
            member = discord.utils.get(self.bot.get_all_members(), id=i["user_id"])
            if member is not None and member in guild.members:
                data.append({"title": member.name, "value": i["points"]})
        view = PaginationView(data)
        await view.send(ctx, title="Leaderboard", description="Eggbux's ranking", color=0x00ff00)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Friendly commands are ready!")

async def setup(bot):
    await bot.add_cog(FriendlyCommands(bot))