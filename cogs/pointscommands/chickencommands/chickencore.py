from random import uniform
from time import time
from discord.ext import commands
from db.farmDB import Farm
from tools.chickens.selection.chickenselection import ChickenSelectView
from tools.chickens.chickenhandlers import RollLimit
from tools.chickens.chickenshared import get_chicken_price, get_rarity_emoji, load_farmer_upgrades, get_usr_farm
from tools.chickens.chickeninfo import rollRates
from tools.pointscore import pricing
from tools.shared import make_embed_object, regular_command_cooldown, spam_command_cooldown, send_bot_embed
import discord
import asyncio

class ChickenCore(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="createfarm", aliases=["cf"], usage="createFarm", description="Create a farm to start farming eggs.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def create_farm(self, ctx) -> None:
        """Farm some eggs"""
        if Farm.read(ctx.author.id):
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} You already have a farm.")
        else:
            Farm.create(ctx.author.id, ctx)
            await send_bot_embed(ctx, description=f"{ctx.author.display_name} You have created a farm.")

    @commands.hybrid_command(name="farm", aliases=["f"], usage="farm OPTIONAL [user]", description="Check the chickens in the farm.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def farm(self, ctx, user: discord.Member = None) -> None:
        """Check the chickens in the farm"""
        if user is None:
            user = ctx.author
        msg = await get_usr_farm(ctx, user)
        if not msg:
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name}, you don't have a farm or any chickens.")
            return
        await ctx.send(embed=msg)

    @commands.hybrid_command(name="market", aliases=["m"], usage="market", description="Market that generates 8 random chickens to buy.")
    @commands.cooldown(1, spam_command_cooldown, commands.BucketType.user)
    @pricing()
    async def market(self, ctx) -> None:
        await self.roll(ctx, 8, "market")

    @commands.hybrid_command(name="eggpack", aliases=["ep"], usage="eggpack", description="Buy an egg pack.")
    @commands.cooldown(1, spam_command_cooldown, commands.BucketType.user)
    @pricing()
    async def eggpack(self, ctx) -> None:
        """Buy an egg pack"""
        farm_data = Farm.read(ctx.author.id)
        if farm_data:
            await self.roll(ctx, 8, 'eggpack')
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have a farm.")
            
    async def roll(self, ctx, chickens_to_generate, action) -> None:
        """Market to buy chickens"""
        farm_data = Farm.read(ctx.author.id)
        if farm_data:
            default_rolls = 10
            if action == "market":
                plrObj = RollLimit.read(ctx.author.id)
                if not plrObj:  
                    if farm_data['farmer'] == "Executive Farmer":
                        farmer_upgrades = load_farmer_upgrades("Executive Farmer")
                        farmer_upgd = farmer_upgrades[0]
                        plrObj = RollLimit(ctx.author.id, default_rolls + farmer_upgd)
                    else:
                        plrObj = RollLimit(ctx.author.id, default_rolls)
                if plrObj.current == 0:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} you have reached the limit of rolls for today.")
                    return
                plrObj.current -= 1
            if farm_data['farmer'] == "Generous Farmer":
                default_rolls += load_farmer_upgrades("Generous Farmer")[0]
            generated_chickens = self.generate_chickens(*self.roll_rates_sum(), chickens_to_generate)
            message = await make_embed_object(title=f":chicken: {ctx.author.display_name} here are the chickens you generated to buy: \n", description="\n".join([f" {get_rarity_emoji(chicken['rarity'])} **{index + 1}.** **{chicken['rarity']} {chicken['name']}**: {get_chicken_price(chicken, farm_data['farmer'])} eggbux." for index, chicken in enumerate(generated_chickens)]))
            view = ChickenSelectView(chickens=generated_chickens, author=ctx.author.id, action="M", message=message)
            await ctx.send(embed=message, view=view)
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} you don't have a farm.")
                         
    def roll_rates_sum(self) -> tuple:
        """Roll the sum of the rates of the chicken rarities"""
        return sum(rollRates.values()), rollRates
    
    def generate_chickens(self, rollRatesSum, rollRates, quant) -> list:
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
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.reset_periodically())
    
    async def reset_periodically(self):
        """Reset the roll limit every hour"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await asyncio.sleep(3600 - time() % 3600)
            RollLimit.remove_all()

async def setup(bot):
    await bot.add_cog(ChickenCore(bot))