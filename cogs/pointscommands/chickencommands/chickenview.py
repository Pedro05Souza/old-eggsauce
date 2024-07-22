from discord.ext import commands
from db.farmDB import Farm
from tools.chickens.chickeninfo import ChickenFood, ChickenMultiplier, ChickenRarity, rollRates
from tools.chickens.chickenshared import get_chicken_egg_value, get_chicken_price, get_rarity_emoji, load_farmer_upgrades, update_user_farm
from tools.shared import create_embed_with_title, create_embed_without_title, make_embed_object, regular_command_cooldown
from tools.pointscore import pricing
from math import ceil
import discord

class ChickenView(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="chickeninfo", aliases=["ci"], usage="chickenInfo <index>", description="Check the information of a chicken.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def check_chicken_info(self, ctx, index: int, user: discord.Member = None):
        """Check the information of a chicken."""
        if user is None:
            user = ctx.author
        farm_data = Farm.read(user.id)
        if farm_data:
            if index > len(farm_data['chickens']) or index < 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, the chicken index is invalid.")
                return
            chicken = farm_data['chickens'][index - 1]
            chicken_egg_value = await get_chicken_egg_value(chicken) - int((await get_chicken_egg_value(chicken) * chicken['upkeep_multiplier']))
            total_profit = (chicken_egg_value * chicken['happiness']) // 100
            msg = await make_embed_object(title=f":chicken: {chicken['rarity']} {chicken['name']}", description=f":partying_face: **Happiness**: {chicken['happiness']}%\n:moneybag: **Price**: {get_chicken_price(chicken, farm_data['farmer'])} eggbux\n:egg: **Egg value**: {chicken_egg_value} \n:gem: **Upkeep rarity**: {round(chicken['upkeep_multiplier'], 2)}%\n:coin: **Eggs generated:** {chicken['eggs_generated']}\n:corn: **Food necessary:** {ChickenFood[chicken['rarity']].value} \n:money_with_wings: **Total profit: {total_profit} eggbux.**")
            await ctx.send(embed=msg)
            
    @commands.hybrid_command(name="chickenrarities", aliases=["cr"], usage="chickenRarities", description="Check the rarities of the chickens.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def check_chicken_rarities(self, ctx):
        """Check the rarities of the chickens"""
        rarity_info = "\n".join([f"{get_rarity_emoji(rarity)} **{rarity}**: {round(rate/100, 4)}%" for rarity, rate in rollRates.items()])
        await create_embed_with_title(ctx, "Chicken Rarities:", rarity_info)

    @commands.hybrid_command(name="chickenvalues", aliases=["cv"], usage="chickenValues", description="Check the values of eggs produced by chickens.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def check_chicken_values(self, ctx):
        """Check the amount of eggs produced by chickens"""
        value_info = "\n".join([f"{get_rarity_emoji(rarity)} **{rarity}**: {ChickenMultiplier[rarity].value}x" for rarity in ChickenMultiplier.__members__])
        await create_embed_with_title(ctx, "Amount of eggs produced by rarity:", value_info)
    
    @commands.hybrid_command(name="chickencorn", usage="chickencorn", description="Show all the chicken food values.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def chicken_corn(self, ctx):
        """Show all the chicken food values"""
        corn_info = "\n".join([f"{get_rarity_emoji(rarity)} **{rarity}**: {ChickenFood[rarity].value}" for rarity in ChickenFood.__members__])
        await create_embed_with_title(ctx, "Chicken food values:", corn_info)
    
    @commands.hybrid_command(name="chickenprices", aliases=["cprice"], usage="chickenPrices", description="Check the prices of the chickens.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def check_chicken_prices(self, ctx):
        """Check the prices of the chickens"""
        prices_info = "\n".join([f"{get_rarity_emoji(rarity)} **{rarity}**: {175 * ChickenRarity[rarity].value} eggbux" for rarity in ChickenRarity.__members__])
        await create_embed_with_title(ctx, "Chicken prices:", prices_info)

    @commands.hybrid_command(name="farmprofit", aliases=["fp"], usage="farmprofit OPTIONAL [user]", description="Check the farm profit.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def farm_profit(self, ctx, user: discord.Member = None):
        """Check the farm profit"""
        if not user:
            user = ctx.author
        farm_data = await update_user_farm(user, Farm.read(user.id))
        if farm_data:
            totalProfit = 0
            totalLoss = 0
            current_upkeep = 0
            totalcorn = 0
            if len(farm_data['chickens']) == 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, you don't have any chickens.")
                return
            for chicken in farm_data['chickens']:
                totalcorn += ChickenFood[chicken['rarity']].value
                chicken_loss = int((await get_chicken_egg_value(chicken) * chicken['upkeep_multiplier']))
                chicken_profit = await get_chicken_egg_value(chicken) - chicken_loss
                totalProfit += (chicken_profit * chicken['happiness']) // 100
                if farm_data['farmer'] == 'Guardian Farmer':
                    to_reduce = load_farmer_upgrades("Guardian Farmer")
                    current_upkeep = chicken['upkeep_multiplier'] - to_reduce
                    totalLoss += ceil(await get_chicken_egg_value(chicken) * current_upkeep)
                else:
                    current_upkeep = chicken['upkeep_multiplier']
                    totalLoss += ceil(await get_chicken_egg_value(chicken) * current_upkeep)
            if farm_data['farmer'] == "Rich Farmer":
                to_add = load_farmer_upgrades("Rich Farmer")
                added_value = (totalProfit * to_add) // 100
                totalProfit += added_value
            result = totalProfit - totalLoss
            if result > 0:
                await create_embed_without_title(ctx, f":white_check_mark: {user.display_name}, your farm is expected to generate a profit of **{result}** per hour :money_with_wings:.\n:chicken: Chicken upkeep: **{totalLoss}**\n:egg: Eggs produced: **{totalProfit}**\n :corn: Corn going to the chickens: **{totalcorn}**.")
            elif result < 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, your farm is expected to generate a loss of **{result}** per hour :money_with_wings:.\n:chicken: Chicken upkeep: **{totalLoss}**\n:egg: Eggs produced: **{totalProfit}**\n :corn: Corn going to the chickens: **{totalcorn}**.")
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, your farm is expected to generate neither profit nor loss.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, you don't have a farm.")

    @commands.hybrid_command(name="renamefarm", aliases=["rf"], usage="renameFarm <nickname>", description="Rename the farm.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def rename_farm(self, ctx, nickname: str):
        """Rename the farm"""
        farm_data = Farm.read(ctx.author.id)
        if farm_data:
            if len(nickname) > 20:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} The farm name must have a maximum of 20 characters.")
                return
            farm_data['farm_name'] = nickname
            Farm.update(ctx.author.id, farm_name=nickname)
            await create_embed_without_title(ctx, f"{ctx.author.display_name} Your farm has been renamed to {nickname}.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You do not have a farm.")

    @commands.hybrid_command(name="renamechicken", aliases=["rc"], usage="renameChicken <index> <nickname>", description="Rename a chicken in the farm.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def rename_chicken(self, ctx, index: int, nickname: str):
        """Rename a chicken in the farm"""
        index -= 1
        farm_data = Farm.read(ctx.author.id)
        if farm_data:
            if not farm_data['chickens']:
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have any chickens.")
                    return
            if len(nickname) > 15:
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the chicken name must have a maximum of 15 characters.")
                    return
            if index > len(farm_data['chickens']) or index < 0:
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
                    return
            check_nickname = nickname.upper()
            if check_nickname in ChickenRarity.__members__:
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't rename a chicken with a rarity name.")
                    return
            chicken_arr = farm_data['chickens']
            for i, chicken in enumerate(chicken_arr):
                if index == i:
                    chicken_arr[i]['name'] = nickname
                    break
            farm_data['chickens'] = chicken_arr
            Farm.update(ctx.author.id, chickens=farm_data['chickens'])
            await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, the chicken has been renamed to {nickname}.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have a farm.")
    
    @commands.hybrid_command(name="switchchicken", aliases=["switch"], usage="switchChicken <index> <index2>", description="Switch the position of two chickens.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def switch_chicken(self, ctx, index: int, index2: int):
        """Switches chickens"""
        farm_data = Farm.read(ctx.author.id)
        if farm_data:
            if index > len(farm_data['chickens']) or index < 0 or index2 > len(farm_data['chickens']) or index2 < 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
                return
            farm_data['chickens'][index - 1], farm_data['chickens'][index2 - 1] = farm_data['chickens'][index2 - 1], farm_data['chickens'][index - 1]
            Farm.update(ctx.author.id, chickens=farm_data['chickens'])
            await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, the chickens have been switched.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have a farm.")

async def setup(bot):
    await bot.add_cog(ChickenView(bot))

    
