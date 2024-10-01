"""
This module contains the core commands for the chicken system.
"""
from random import uniform
from time import time
from db import Farm
from views.selection import ChickenSelectView
from lib.chickenlib import get_usr_farm, RollLimit, load_farmer_upgrades, get_rarity_emoji, get_chicken_price, rollRates
from tools import pricing
from lib import make_embed_object, send_bot_embed, return_data, update_user_param
from resources import REGULAR_COOLDOWN, SPAM_COOLDOWN, ROLL_PER_HOUR, DEFAULT_ROLLS, CHICKENS_GENERATED
from discord.ext import commands
from discord.ext.commands import Context
import discord

__all__ = ["ChickenCore"]

class ChickenCore(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="createfarm", aliases=["cf"], usage="createFarm", description="Create a farm to start farming eggs.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def create_farm(self, ctx: Context) -> None:
        """
        Create a farm to start farming eggs.

        Args:
            ctx (Context): The context of the command.
        
        Returns:
            None
        """
        farm_data = ctx.data["farm_data"]
        if farm_data:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} You already have a farm.")
        else:
            await Farm.create(ctx.author.id, ctx)
            await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name} You have created a farm.")

    @commands.hybrid_command(name="farm", aliases=["f"], usage="farm OPTIONAL [user]", description="Check the chickens in the farm.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def farm(self, ctx: Context, user: discord.Member = None) -> None:
        """
        Check the chickens in the farm.

        Args:
            ctx (Context): The context of the command.
            user (discord.Member, optional): The user to check the farm. Defaults to None, which is the author of the command.

        Returns:
            None
        """
        data, discord_member = await return_data(ctx, user)

        if user and data['user_data']:
            await update_user_param(ctx, data["user_data"], data, user)

        msg = await get_usr_farm(ctx, discord_member, data)

        if not msg:
            await send_bot_embed(ctx, description=f":no_entry_sign: {discord_member.display_name}, you don't have any chickens.")
            return
        
        await ctx.send(embed=msg)

    @commands.hybrid_command(name="market", aliases=["m"], usage="market", description="Market that generates 8 random chickens to buy.")
    @commands.cooldown(1, SPAM_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def market(self, ctx: Context) -> None:
        """
        Market to buy chickens.

        Args:
            ctx (Context): The context of the command.

        Returns:
            None
        """	
        await self.roll(ctx, CHICKENS_GENERATED, "market")

    @commands.hybrid_command(name="eggpack", aliases=["ep"], usage="eggpack", description="Buy an egg pack.")
    @commands.cooldown(1, SPAM_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def eggpack(self, ctx: Context) -> None:
        """
        Buy an egg pack.

        Args:
            ctx (Context): The context of the command.
        
        Returns:
            None
        """
        farm_data = ctx.data["farm_data"]
        if farm_data:
            await self.roll(ctx, CHICKENS_GENERATED, 'eggpack')
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have a farm.")
            
    async def roll(self, ctx: Context, chickens_to_generate: int, action: str) -> None:
        """
        Market to buy chickens.

        Args:
            ctx (Context): The context of the command.
            chickens_to_generate (int): The number of chickens to generate.
            action (str): The action to take.

        Returns:
            None
        """
        global DEFAULT_ROLLS
        
        farm_data = ctx.data["farm_data"]

        if action == "market":

            if not await self.verify_if_user_can_roll(farm_data):
                minutes_remaining = round((ROLL_PER_HOUR - (time() - farm_data['last_market_drop'])) / 60)
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} you can only roll once every **{ROLL_PER_HOUR // 3600}** hour(s). Try again in **{minutes_remaining}** minutes.")
                return
            
            if not RollLimit.read_key(ctx.author.id):

                if farm_data['farmer'] == "Executive Farmer":
                    farmer_upgrades = load_farmer_upgrades("Executive Farmer")
                    farmer_upgd = farmer_upgrades[0]
                    RollLimit.create(ctx.author.id, farmer_upgd + DEFAULT_ROLLS)
                else:
                    RollLimit.create(ctx.author.id, DEFAULT_ROLLS)

            RollLimit.update(ctx.author.id, RollLimit.read(ctx.author.id) - 1)

            if RollLimit.read(ctx.author.id) == 1:
                await Farm.update_last_market_drop(ctx.author.id)
                RollLimit.remove(ctx.author.id)

        if farm_data['farmer'] == "Generous Farmer":
            DEFAULT_ROLLS += load_farmer_upgrades("Generous Farmer")[0]
            
        generated_chickens = self.generate_chickens(*self.roll_rates_sum(), chickens_to_generate)
        message = await make_embed_object(title=f":chicken: {ctx.author.display_name} here are the chickens you generated to buy: \n", description="\n".join([f" {get_rarity_emoji(chicken['rarity'])} **{index + 1}.** **{chicken['rarity']} {chicken['name']}**: {get_chicken_price(chicken, farm_data['farmer'])} eggbux." for index, chicken in enumerate(generated_chickens)]))
        view = ChickenSelectView(chickens=generated_chickens, author=ctx.author.id, action="M", embed_text=message, author_cached_data=ctx.data)
        await ctx.send(embed=message, view=view)
                         
    def roll_rates_sum(self) -> tuple:
        """
        Roll the sum of the rates of the chicken rarities.

        Returns:
            tuple
        """
        return sum(rollRates.values()), rollRates
    
    def generate_chickens(self, rollRatesSum: float, rollRates: dict, quant: int) -> list:
        """
        Generate chickens according to the roll rates

        Args:
            rollRatesSum (float): The sum of the roll rates.
            rollRates (dict): The roll rates.
            quant (int): The quantity of chickens to generate.

        Returns:
            list
        """
        generated_chickens = []
        initial_range = 1
        for _ in range(quant):
            randomRoll = uniform(initial_range, rollRatesSum)
            for rarity, rate in rollRates.items():
                if randomRoll <= rate:
                    generated_chickens.append({
                        "rarity" : rarity,
                        "name" : "Chicken"
                    })
                    break
                randomRoll -= rate
        return generated_chickens
    
    async def verify_if_user_can_roll(self, farm_data: dict) -> bool:
        """
        Verify if the user can roll.

        Args:
            farm_data (dict): The farm data.

        Returns:
            bool
        """
        last_roll = time() - farm_data['last_market_drop']
        last_roll = min(last_roll // ROLL_PER_HOUR, 1)
        if last_roll >= 1:
            return True
        return False

async def setup(bot):
    await bot.add_cog(ChickenCore(bot))