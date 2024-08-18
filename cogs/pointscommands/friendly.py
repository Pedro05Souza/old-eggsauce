from discord.ext import commands
from db.MarketDB import Market
from tools.shared import return_data, send_bot_embed, make_embed_object, get_user_title
from tools.settings import regular_command_cooldown
from tools.chickens.chickenshared import rank_determiner
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
        await send_bot_embed(ctx, description=f":soccer: balls")

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

    # @commands.hybrid_command(name="leaderboard", brief="Shows the leaderboard.", description="Shows the leaderboard..", usage="leaderboard")
    # @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    # @pricing()
    # async def leaderboard(self, ctx):
    #     """Shows the leaderboard."""
    #     users = User.readAll()
    #     user_data = []
    #     guild = ctx.guild
    #     for user in users:
    #         member = discord.utils.get(guild.members, id=user["user_id"])
    #         if member is not None and member in guild.members:
    #             user_data.append({"username": member.display_name, "points": user["points"], "user_id": user["user_id"]})
    #     for user in user_data:
    #         if Bank.read(user['user_id']) is not None:
    #             user["points"] += Bank.read(user["user_id"])['bank']
    #     user_data = sorted(user_data, key=lambda x: x['points'], reverse=True)
    #     data = []
    #     for index, user in enumerate(user_data):
    #         data.append({"title": f"#{index + 1}-{user['username']}", "value": f":egg: Eggbux: {user['points']}"})
    #     view = PaginationView(data, thumbnail="https://cdn.discordapp.com/attachments/747917669772165121/1259261871744090142/Trophy-3.png?ex=668b0a82&is=6689b902&hm=f74e5d322d1315103dfd6b744127de67c380dc25c86c9afd17b98a126efe7e85&")
    #     await view.send(ctx, title="Leaderboard", description="Eggbux's ranking", color=0x00ff00)
    
    @commands.hybrid_command(name="profile", brief="Shows the user's profile.", description="Shows the user's profile with all the upgrades.", usage="profile OPTIONAL [user]")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def user_profile(self, ctx, user: discord.Member = None):
        """Shows the user's profile."""
        data, user = await return_data(ctx, user)
        user_data = data["user_data"]
        bank_data = data["bank_data"]
        farm_data = data["farm_data"]
        market_data = Market.get_user_offers(user.id)
        if not user_data:
            await send_bot_embed(ctx, description=f"{user.display_name} doesn't have a profile.")
            return
        msg = await make_embed_object(title=f"{user.display_name}'s Profile:\n")
        msg.add_field(name=":coin: Title:", value=await get_user_title(user_data), inline=True)
        msg.add_field(name=":chicken: Farm Size:", value=len(farm_data['chickens']) if farm_data else 0, inline=True)
        msg.add_field(name=":farmer: Farmer:", value=farm_data['farmer'] if farm_data else "No Farmer.", inline=True)
        msg.add_field(name=":bank: Bank upgrades:", value=bank_data['upgrades'] - 1 if bank_data else 0, inline=True)
        msg.add_field(name=":corn: Corn limit:", value=farm_data['corn_limit'] if farm_data else 0, inline=True)
        msg.add_field(name=":moneybag: Corn plot:", value=farm_data['plot'] if farm_data else 0, inline=True)
        msg.add_field(name=":scroll: Activate offers:", value=len(market_data) if market_data else 0, inline=True)
        msg.add_field(name="Chicken Rank:", value=await rank_determiner(farm_data['mmr']))
        msg.set_footer(text=f"User ID: {user.id}. Created at: {user.created_at}")
        msg.set_thumbnail(url=user.display_avatar.url)
        await ctx.send(embed=msg)

async def setup(bot):
    await bot.add_cog(FriendlyCommands(bot))