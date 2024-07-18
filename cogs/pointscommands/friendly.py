from discord.ext import commands
from tools.shared import create_embed_without_title, regular_command_cooldown
from db.userDB import User
from db.bankDB import Bank
from tools.pagination import PaginationView
from tools.prices import Prices
from tools.pointscore import pricing
from random import choice
import os
import discord

class FriendlyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @pricing()
    async def balls(self, ctx):
        """Bot sends balls."""
        await create_embed_without_title(ctx, f":soccer: balls")

    @commands.hybrid_command("mog", brief="Mog a user", parameters=["user: discord.Member"], examples=["mog @user"], description="Mog a user.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def mog(self, ctx, user: discord.Member):
            """Mog a user."""
            path = choice(os.listdir("images/mogged/"))
            await ctx.send(file=discord.File("images/mogged/"+path))
            await ctx.send(f"{user.mention} bye bye 🤫🧏‍♂️")
    
    @commands.hybrid_command(name="shop", brief="Shows the shop.", description="Shows all the points commands and their prices.", usage="shop")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def shop(self, ctx):
        """Shows the shop."""
        data = []
        for member in Prices.__members__:
            if Prices.__members__[member].value > 0:
                data.append({"title": member, "value": str(Prices.__members__[member].value) + " eggbux"})
        view = PaginationView(data)
        await view.send(ctx, title="Shop", description="Buy commands with your eggbux:", color=0x00ff00)

    @commands.hybrid_command(name="leaderboard", brief="Shows the leaderboard.", description="Shows the leaderboard..", usage="leaderboard")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def leaderboard(self, ctx):
        """Shows the leaderboard."""
        users = User.readAll()
        user_data = []
        guild = ctx.guild
        for user in users:
            member = discord.utils.get(guild.members, id=user["user_id"])
            if member is not None and member in guild.members:
                user_data.append({"username": member.display_name, "points": user["points"], "user_id": user["user_id"]})
        for user in user_data:
            if Bank.read(user['user_id']) is not None:
                user["points"] += Bank.read(user["user_id"])['bank']
        user_data = sorted(user_data, key=lambda x: x['points'], reverse=True)
        data = []
        for index, user in enumerate(user_data):
            data.append({"title": f"#{index + 1}-{user['username']}", "value": f":egg: Eggbux: {user['points']}"})
        view = PaginationView(data, thumbnail="https://cdn.discordapp.com/attachments/747917669772165121/1259261871744090142/Trophy-3.png?ex=668b0a82&is=6689b902&hm=f74e5d322d1315103dfd6b744127de67c380dc25c86c9afd17b98a126efe7e85&")
        await view.send(ctx, title="Leaderboard", description="Eggbux's ranking", color=0x00ff00)

async def setup(bot):
    await bot.add_cog(FriendlyCommands(bot))