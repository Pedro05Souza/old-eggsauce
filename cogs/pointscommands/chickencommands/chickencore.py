"""
This module contains the core commands and processes for the chicken system in order for it to work properly.
"""


from random import uniform
from time import time
from db.farmDB import Farm
from tools.chickens.selection.chickenselection import ChickenSelectView
from tools.chickens.chickenhandlers import RollLimit
from tools.chickens.chickenshared import get_chicken_price, get_rarity_emoji, load_farmer_upgrades, get_usr_farm
from tools.chickens.chickeninfo import rollRates
from tools.pointscore import pricing
from tools.shared import make_embed_object, send_bot_embed, return_data
from tools.settings import spam_command_cooldown, regular_command_cooldown, roll_per_hour, default_rolls
from discord.ext import commands
from discord.ext.commands import Context
import discord
import asyncio

class ChickenCore(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="createfarm", aliases=["cf"], usage="createFarm", description="Create a farm to start farming eggs.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def create_farm(self, ctx: Context) -> None:
        """Farm some eggs."""
        farm_data = ctx.data["farm_data"]
        if farm_data:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} You already have a farm.")
        else:
            Farm.create(ctx.author.id, ctx)
            await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name} You have created a farm.")

    @commands.hybrid_command(name="farm", aliases=["f"], usage="farm OPTIONAL [user]", description="Check the chickens in the farm.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def farm(self, ctx: Context, user: discord.Member = None) -> None:
        """Check the chickens in the farm."""
        data, user = await return_data(ctx, user)
        msg = await get_usr_farm(ctx, user, data)
        if not msg:
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name}, you don't have any chickens.")
            return
        await ctx.send(embed=msg)

    @commands.hybrid_command(name="market", aliases=["m"], usage="market", description="Market that generates 8 random chickens to buy.")
    @commands.cooldown(1, spam_command_cooldown, commands.BucketType.user)
    @pricing()
    async def market(self, ctx: Context) -> None:
        """Market to buy chickens."""	
        await self.roll(ctx, 8, "market")

    @commands.hybrid_command(name="eggpack", aliases=["ep"], usage="eggpack", description="Buy an egg pack.")
    @commands.cooldown(1, spam_command_cooldown, commands.BucketType.user)
    @pricing()
    async def eggpack(self, ctx: Context) -> None:
        """Buy an egg pack."""
        farm_data = ctx.data["farm_data"]
        if farm_data:
            await self.roll(ctx, 8, 'eggpack')
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have a farm.")
            
    async def roll(self, ctx: Context, chickens_to_generate: list, action: str) -> None:
        """Market to buy chickens."""
        global default_rolls
        farm_data = ctx.data["farm_data"]
        if action == "market":
            if not await self.verify_if_user_can_roll(farm_data):
                minutes_remaining = round((roll_per_hour - (time() - farm_data['last_market_drop'])) / 60)
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} you can only roll once every **{roll_per_hour // 3600}** hour(s). Try again in **{minutes_remaining}** minutes.")
                return
            if not RollLimit.read_key(ctx.author.id):
                if farm_data['farmer'] == "Executive Farmer":
                    farmer_upgrades = load_farmer_upgrades("Executive Farmer")
                    farmer_upgd = farmer_upgrades[0]
                    RollLimit.create(ctx.author.id, farmer_upgd + default_rolls)
                else:
                    RollLimit.create(ctx.author.id, default_rolls)
            RollLimit.update(ctx.author.id, RollLimit.read(ctx.author.id) - 1)
            if RollLimit.read(ctx.author.id) == 1:
                Farm.update_last_market_drop(ctx.author.id)
                RollLimit.remove(ctx.author.id)
        if farm_data['farmer'] == "Generous Farmer":
            default_rolls += load_farmer_upgrades("Generous Farmer")[0]
        generated_chickens = self.generate_chickens(*self.roll_rates_sum(), chickens_to_generate)
        message = await make_embed_object(title=f":chicken: {ctx.author.display_name} here are the chickens you generated to buy: \n", description="\n".join([f" {get_rarity_emoji(chicken['rarity'])} **{index + 1}.** **{chicken['rarity']} {chicken['name']}**: {get_chicken_price(chicken, farm_data['farmer'])} eggbux." for index, chicken in enumerate(generated_chickens)]))
        view = ChickenSelectView(chickens=generated_chickens, author=ctx.author.id, action="M", message=message)
        await ctx.send(embed=message, view=view)
                         
    def roll_rates_sum(self) -> tuple:
        """Roll the sum of the rates of the chicken rarities"""
        return sum(rollRates.values()), rollRates
    
    def generate_chickens(self, rollRatesSum: float, rollRates: dict, quant: int) -> list:
        """Generate chickens according to the roll rates"""
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
        last_roll = time() - farm_data['last_market_drop']
        last_roll = min(last_roll // roll_per_hour, 1)
        if last_roll >= 1:
            return True
        return False

async def setup(bot):
    await bot.add_cog(ChickenCore(bot))