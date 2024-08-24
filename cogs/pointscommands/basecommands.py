"""
This file contains all the base commands in the bot.  
"""

from discord.ext import commands
from db.MarketDB import Market
from tools.tips import tips
from tools.shared import guild_cache_retriever, return_data, send_bot_embed, make_embed_object, get_user_title, user_cache_retriever
from tools.settings import regular_command_cooldown
from tools.chickens.chickenshared import rank_determiner
from db.userDB import User
from db.bankDB import Bank
from tools.pagination import PaginationView
from tools.prices import Prices
from tools.pointscore import pricing, refund
from random import choice, randint
import os
import discord
import time

class BaseCommands(commands.Cog):
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
    
    @commands.hybrid_command(name="modulestatus", aliases=["status"], brief="Check the status of ptscmds.", usage="points_toggle", description="Check if the points commands are enabled or disabled in the server.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    async def points_status(self, ctx):
        """Check the current module active in the server"""
        modules = {
            "T": "Total",
            "F": "Friendly",
            "H": "Hostile",
            "N": "None"
        }
        current_module = await guild_cache_retriever(ctx.guild.id)
        current_module = current_module['toggled_modules']
        await send_bot_embed(ctx, description=f":warning: Points commands are currently set to: **{modules[current_module]}**")
                
    @commands.hybrid_command(name="register", aliases=["reg"], brief="Registers the user in the database.", usage="register", description="Registers the user in the database.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    async def register(self, ctx):
        """Registers the user in the database."""
        if User.read(ctx.author.id):
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} is already registered.")
        else:
            User.create(ctx.author.id, 0)
            await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name} has been registered.")
 
    @commands.hybrid_command(name="points", aliases=["pts", "eggbux", "p"], brief="Shows the amount of points the user has.", usage="points OPTIONAL [user]", description="Shows the amount of points a usr has. If not usr, shows author's points.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def points(self, ctx, user: discord.Member = None):
        """Shows the amount of points the user has."""
        data, user = await return_data(ctx, user)
        user_data = data["user_data"]
        bank_data = data["bank_data"]
        if user_data:
            if bank_data:
                msg = await make_embed_object(title=f":egg: {user.display_name}'s eggbux", description=f":briefcase: Wallet: {user_data['points']}\n :bank: Bank: {bank_data['bank']}")
                msg.add_field(name=":money_with_wings: Total eggbux:", value=f"{user_data['points'] + bank_data['bank']}")
                msg.set_thumbnail(url=user.display_avatar)
                msg.set_footer(text=tips[randint(0, len(tips) - 1)])
                await ctx.send(embed=msg)
            else:
                msg = await make_embed_object(title=f":egg: {user.display_name}'s eggbux", description=f":briefcase: Wallet: {user_data['points']}")
                msg.set_thumbnail(url=user.display_avatar)
                await ctx.send(embed=msg)
        else:   
            await send_bot_embed(ctx, description=f"{user.display_name} has no eggbux :cry:")
        
    @commands.hybrid_command(name="buytitles", aliases=["titles"], brief="Buy custom titles.", usage="Buytitles", description="Buy custom titles that comes with different salaries every 30 minutes.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def points_Titles(self, ctx):
        end_time = time.time() + 60
        roles = {
            "T" : "Egg Novice",
            "L" : "Egg Apprentice",
            "M" : "Egg wizard",
            "H" : "Egg King",
        }
        rolePrices = {
            "T" : 1500,
            "L" : 2500,
            "M" : 4000,
            "H" : 5000
        }
        message = await send_bot_embed(ctx, title="Custom Titles:", description=f":poop: **{roles['T']}**\nIncome: 20 eggbux. :money_bag: \nPrice: {rolePrices['T']} eggbux.\n\n :farmer: **{roles['L']}** \nIncome: 40 eggbux. :money_bag:\n Price: {rolePrices['L']} eggbux. \n\n:man_mage: **{roles['M']}** \n Income: 60 eggbux. :money_bag:\n Price: {rolePrices['M']} eggbux. \n\n:crown: **{roles['H']}** \n Income: 80 eggbux. :money_bag:\n Price: {rolePrices['H']} eggbux. \n\n**The titles are bought sequentially.**\nReact with ✅ to buy a title.")
        await message.add_reaction("✅")
        while True:
            actual_time = end_time - time.time()
            if actual_time <= 0:
                await message.clear_reactions()
                break
            check = lambda reaction, _: reaction.emoji == "✅" and reaction.message.id == message.id
            reaction, user = await self.bot.wait_for("reaction_add", check=check)
            if reaction.emoji == "✅":
                user_data = await user_cache_retriever(user.id)
                if user_data["roles"] == "":
                    await self.buy_roles(ctx, user, rolePrices["T"], "T", roles["T"], user_data)
                elif user_data["roles"][-1] == "T":
                    await self.buy_roles(ctx, user, rolePrices["L"], "L", roles["L"], user_data)
                elif user_data["roles"][-1] == "L":
                    await self.buy_roles(ctx, user, rolePrices["M"], "M", roles["M"], user_data)
                elif user_data["roles"][-1] == "M":
                    await self.buy_roles(ctx, user, rolePrices["H"], "H", roles["H"], user_data)

    async def buy_roles(self, ctx, user: discord.Member, roleValue, roleChar, roleName, user_data):
        """Buy roles."""
        if user_data["points"] >= roleValue and roleChar not in user_data["roles"]:
            User.update_all(user.id, user_data["points"] - roleValue, user_data["roles"] + roleChar)
            await send_bot_embed(ctx, description=f":white_check_mark: {user.display_name} has bought the role **{roleName}**.")
        elif user_data["points"] < roleValue:
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name}, you don't have enough eggbux to buy the role **{roleName}**.")
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} already has the role **{roleName}**.")
    
    @commands.hybrid_command(name="salary", aliases=["sal"], brief="Check the salary of a user.", usage="salary OPTIONAL [user]", description="Check the salary of a user. If not user, shows author's salary.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def salary(self, ctx, user: discord.Member = None):
        """Check the salary of a user."""
        data, user = await return_data(ctx, user)
        user_data = data["user_data"]
        if user_data:
            if user_data["roles"] != "":
                await send_bot_embed(ctx, description=f":moneybag: {user.display_name} has the title of **{await get_user_title(user_data)}** and earns {await self.salary_role(user_data)} eggbux..")
                return   
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} doesn't have a title.")
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} isn't registered in the database.")
            await refund(ctx.author, ctx)

async def setup(bot):
    await bot.add_cog(BaseCommands(bot))