"""
This file contains all the base commands in the bot.
This cog is shared between all configurable bot modules.
"""
from discord.ext import commands
from db.marketdb import Market
from tools.tips import tips
from tools.shared import *
from tools.settings import REGULAR_COOLDOWN
from tools.chickens.chickenshared import rank_determiner
from db.userdb import User
from db.bankdb import Bank
from tools.pagination import PaginationView
from tools.prices import Prices
from tools.pointscore import pricing
from random import randint
from discord.ext.commands import Context
import discord
import time

class BaseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="shop", brief="Shows the shop.", description="Shows all the points commands and their prices.", usage="shop")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def shop(self, ctx: Context) -> None:
        """
        Shows the shop.

        Args:
            ctx (Context): The context of the command.

        Returns:
            None
        """
        data = []
        for member in Prices.__members__:
            if Prices.__members__[member].value > 0:
                data.append({"title": member, "value": await format_number((Prices.__members__[member].value)) + " eggbux"})
        view = PaginationView(data)
        await view.send(ctx, title="Shop", description="Buy commands with your eggbux:", color=discord.Color.yellow())
    
    @commands.hybrid_command(name="profile", brief="Shows the user's profile.", description="Shows the user's profile with all the upgrades.", usage="profile OPTIONAL [user]")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def user_profile(self, ctx: Context, user: discord.Member = None) -> None:
        """
        Shows the user's profile.

        Args:
            ctx (Context): The context of the command.
            user (discord.Member, optional): The user to check the profile. Defaults to None, which is the author of the command.
        
        Returns:
            None
        """
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
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    async def points_status(self, ctx: Context) -> None:
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
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    async def register(self, ctx: Context) -> None:
        """Registers the user in the database."""
        if User.read(ctx.author.id):
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} is already registered.")
        else:
            User.create(ctx.author.id, 0)
            Bank.create(ctx.author.id, 0)
            await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name} has been registered.")
 
    @commands.hybrid_command(name="points", aliases=["pts", "eggbux", "p"], brief="Shows the amount of points the user has.", usage="points OPTIONAL [user]", description="Shows the amount of points a usr has. If not usr, shows author's points.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def points(self, ctx: Context, user: discord.Member = None) -> None:
        """Shows the amount of points the user has."""
        data, user = await return_data(ctx, user)
        user_data = data["user_data"]
        bank_data = data["bank_data"]
        if user_data:
            msg = await make_embed_object(title=f":egg: {user.display_name}'s eggbux", description=f":briefcase: Wallet: {await format_number(user_data['points'])}\n :bank: Bank: {await format_number(bank_data['bank'])}")
            msg.add_field(name=":money_with_wings: Total eggbux:", value=f"{await format_number(user_data['points'] + bank_data['bank'])}")
            msg.set_thumbnail(url=user.display_avatar)
            msg.set_footer(text=tips[randint(0, len(tips) - 1)])
            await ctx.send(embed=msg)
        else:   
            await send_bot_embed(ctx, description=f"{user.display_name} has no eggbux :cry:")
        
    @commands.hybrid_command(name="buytitles", aliases=["titles"], brief="Buy custom titles.", usage="Buytitles", description="Buy custom titles that comes with different salaries every 30 minutes.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def points_Titles(self, ctx: Context) -> None:
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

    async def buy_roles(self, ctx: Context, user: discord.Member, roleValue: int, roleChar: str, roleName: str, user_data: dict) -> None:
        """Buy roles."""
        if user_data["points"] >= roleValue and roleChar not in user_data["roles"]:
            User.update_all(user.id, user_data["points"] - roleValue, user_data["roles"] + roleChar)
            await send_bot_embed(ctx, description=f":white_check_mark: {user.display_name} has bought the role **{roleName}**.")
        elif user_data["points"] < roleValue:
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name}, you don't have enough eggbux to buy the role **{roleName}**.")
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} already has the role **{roleName}**.")
    
    @commands.hybrid_command(name="salary", aliases=["sal"], brief="Check the salary of a user.", usage="salary OPTIONAL [user]", description="Check the salary of a user. If not user, shows author's salary.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def salary(self, ctx: Context, user: discord.Member = None):
        """
        Check the salary of a user.

        Args:
            ctx (Context): The context of the command.
            user (discord.Member, optional): The user to check the salary. Defaults to None, which is the author of the command.

        Returns:
            None
        """
        data, user = await return_data(ctx, user)
        user_data = data["user_data"]
        if user_data["roles"] != "":
            await send_bot_embed(ctx, description=f":moneybag: {user.display_name} has the title of **{await get_user_title(user_data)}** and earns {await self.salary_role(user_data)} eggbux..")
            return   
        await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} doesn't have a title.")
            
async def setup(bot):
    await bot.add_cog(BaseCommands(bot))