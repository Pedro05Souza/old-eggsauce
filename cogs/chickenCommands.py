import asyncio
from enum import Enum
from discord.ext import commands
from db.farmDB import Farm
from db.userDB import Usuario
from tools.ChickenSelection import ChickenSelectView
from random import randint
import discord
from tools.pricing import pricing
from tools.embed import create_embed_without_title, create_embed_with_title
roll_limit = {}
class ChickenRarity(Enum):
        COMMON = 1
        UNCOMMON = 2
        RARE = 3
        EXCEPTIONAL = 4
        EPIC = 5
        LEGENDARY = 6
        MYTHICAL = 7
        ULTIMATE = 8
        COSMIC = 9
        DIVINE = 10
        INFINITY = 14
        OMINOUS = 20

class ChickenCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command("createFarm", aliases=["cf"])
    @pricing()
    async def create_farm(self, ctx):
        """Farm some eggs"""
        if Farm.read(ctx.author.id):
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You already have a farm.")
        if Usuario.read(ctx.author.id):
            Farm.create(ctx.author.id, ctx)
            await create_embed_without_title(ctx, f"{ctx.author.display_name} You have created a farm.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You are not registered in the database.")

    @commands.command("market", aliases=["m"])
    @pricing()
    async def market(self, ctx):
        """Market to buy chickens"""
        if ctx.author.id not in roll_limit:
            roll_limit[ctx.author.id] = {
                "limit": 0,
                "chickens": []
            }

        if roll_limit[ctx.author.id]['limit'] >= 10:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You have reached the limit of chickens you can buy today.")
            return
        roll_limit[ctx.author.id]['limit'] += 1
        generated_chickens = self.generate_chickens(*self.roll_rates_sum(), 10)
        roll_limit[ctx.author.id]['chickens'] = generated_chickens
        message = discord.Embed(title=f":chicken: {ctx.author.display_name} here are the chickens you generated to buy: \n", description="\n".join([f" {self.get_rarity_emoji(chicken['Name'])} **{index + 1}.** **{chicken['Name']}**: {chicken['Price']}" for index, chicken in enumerate(generated_chickens)]))
        view = ChickenSelectView(chickens=generated_chickens, author_id=ctx.author.id, action="M", message=message, chicken_emoji=self.get_rarity_emoji)
        await ctx.send(embed=message, view=view)
  
    def roll_rates_sum(self):
        """Roll the sum of the rates of the chicken rarities"""
        rollRates = {
            "COMMON": 5000,
            "UNCOMMON": 3000,
            "RARE": 1500,
           "EXCEPTIONAL": 200,
            "EPIC": 150,
            "ULTIMATE": 100,
            "COSMIC": 25,
            "DIVINE": 15,
            "INFINITY": 9,
            "OMINOUS": 1
        }
        return sum(rollRates.values()), rollRates
    
    def generate_chickens(self, rollRatesSum, rollRates, quant):
        """Generate chickens according to the roll rates"""
        default_value = 175
        generated_chickens = []
        for _ in range(quant):
            randomRoll = randint(1, rollRatesSum)
            for rarity, rate in rollRates.items():
                if randomRoll <= rate:
                    generated_chickens.append({
                        "Name" : f"{rarity} Chicken",
                        "Price" : f" {default_value * ChickenRarity[rarity].value} eggbux.",
                        "Bought" : False
                    })
                    break
                randomRoll -= rate
        return generated_chickens
    
    def get_rarity_emoji(self, rarity):
        defineRarityEmojis = {
            "COMMON": ":brown_circle:",
            "UNCOMMON": ":green_circle:",
            "RARE": ":blue_circle:",
            "EXCEPTIONAL": ":purple_circle:",
            "EPIC": ":orange_circle:",
            "LEGENDARY": ":red_circle:",
            "MYTHICAL": ":yellow_circle:",
            "ULTIMATE": ":black_circle:",
            "COSMIC": ":white_circle:",
            "DIVINE": ":sparkles:",
            "INFINITY": ":milky_way:",
            "Ominous": ":boom:"
        }

        return defineRarityEmojis[rarity.split()[0]]
    
    async def reset_periodically(self):
        """Reset the roll limit every 24 hours"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            roll_limit.clear()
            await asyncio.sleep(86400)
    
    @commands.command("farm", aliases=["f"])
    @pricing()
    async def farm(self, ctx, User: discord.Member = None):
        """Check the chickens in the farm"""
        if User is None:
            User = ctx.author
        if Farm.read(User.id):
            farm_data = Farm.read(User.id)
            showFarm = farm_data['farm_name']
            if "_" in showFarm:
                showFarm = showFarm.replace("_", " ")
            await create_embed_with_title(ctx, f"{showFarm}\n", "\n".join([f"{self.get_rarity_emoji(chicken['Name'])}  **{index + 1}.** {chicken['Name']}" for index, chicken in enumerate(farm_data['chickens'])]))
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {User.display_name}, doesn't have a farm.")


    @commands.command("sellChicken", aliases=["sellc"])
    @pricing()
    async def sell_chicken(self, ctx):
        """Deletes a chicken from the farm"""
        if Farm.read(ctx.author.id):
            if not Farm.read(ctx.author.id)['chickens']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You don't have any chickens.")
                return
            farm_data = Farm.read(ctx.author.id)
            message = discord.Embed(title=f":chicken: {farm_data['farm_name']}", description="\n".join([f"{self.get_rarity_emoji(chicken['Name'])} **{index + 1}.** {chicken['Name']}" for index, chicken in enumerate(farm_data['chickens'])]))
            view = ChickenSelectView(message=message, chickens=farm_data['chickens'], author_id=ctx.author.id, action="D", chicken_emoji=self.get_rarity_emoji)
            await ctx.send(embed=message,view=view)
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You do not have a farm.")

    @commands.command("renameFarm", aliases=["rf"])
    @pricing()
    async def rename_farm(self, ctx, *nickname: str):
        """Rename the farm"""
        if Farm.read(ctx.author.id):
            farm_data = Farm.read(ctx.author.id)
            nickname = " ".join(nickname)
            if len(nickname) > 20:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} The farm name must have a maximum of 20 characters.")
                return
            farm_data['Name'] = nickname
            Farm.update(ctx.author.id, nickname, farm_data['chickens'], farm_data['eggs'], farm_data['eggs_generated'])
            await create_embed_without_title(ctx, f"{ctx.author.display_name} Your farm has been renamed to {nickname}.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You do not have a farm.")

    @commands.command("renameChicken", aliases=["rc"])
    async def rename_chicken(self, ctx, *nickname: str):
        """Rename a chicken in the farm"""
        pass
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.reset_periodically())

async def setup(bot):
    await bot.add_cog(ChickenCommands(bot))



