"""
This module contains commands that are used to display information about the chickens in the game.
"""
from discord.ext import commands
from db import Farm
from lib import send_bot_embed, make_embed_object, user_cache_retriever, return_data, format_number, update_user_param
from lib.chickenlib import (
    get_chicken_egg_value, get_rarity_emoji, get_chicken_price,
    get_rarity_emoji, ChickenMultiplier, ChickenRarity, ChickenFood, rollRates, chicken_ranking,
    rank_determiner, give_total_farm_profit, farm_maintence_tax
)
from views.selection import ChickenSelectView
from resources import REGULAR_COOLDOWN, FARM_DROP
from tools import pricing
from better_profanity import profanity
from discord.ext.commands import Context
import discord

__all__ = ["ChickenView"]

class ChickenView(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="chickeninfo", aliases=["ci"], usage="chickenInfo <index>", description="Check the information of a chicken.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def check_chicken_info(self, ctx: Context, index: int, user: discord.Member = None) -> None:
        """
        Check the information of a chicken.

        Args:
            ctx (Context): The context of the command.
            index (int): The index of the chicken to check.
            user (discord.Member, optional): The user to check the chicken. Defaults to None, which is the author of the command.
        
        Returns:
            None
        """
        farm_data, _ = await return_data(ctx, user)
        farm_data = farm_data["farm_data"]
        if farm_data:
            if index > len(farm_data['chickens']) or index < 0:
                await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name}, the chicken index is invalid.")
                return
            
            chicken = farm_data['chickens'][index - 1]
            chicken_egg_value = await get_chicken_egg_value(chicken) - int((await get_chicken_egg_value(chicken) * chicken['upkeep_multiplier']))
            happiness_loss = int((chicken_egg_value * (100 - chicken['happiness'])) // 100)
            total_profit = chicken_egg_value - happiness_loss
            msg = await make_embed_object(
                title=f":chicken: {chicken['rarity']} {chicken['name']}",
                description=(
                    f":partying_face: **Happiness**: {chicken['happiness']}%\n"
                    f":moneybag: **Price**: {get_chicken_price(chicken, farm_data['farmer'])} eggbux\n"
                    f":egg: **Egg value**: {chicken_egg_value}/{ChickenMultiplier[chicken['rarity']].value}\n"
                    f":gem: **Upkeep rarity**: {round(chicken['upkeep_multiplier'] * 100)}%\n"
                    f":coin: **Eggs generated:** {await format_number(chicken['eggs_generated'])}\n"
                    f":corn: **Food necessary:** {ChickenFood[chicken['rarity']].value}\n"
                    f":warning: **Happiness penalty:** {happiness_loss}\n" 
                    f":money_with_wings: **Total profit: {total_profit} eggbux.**"
                )
            )
            await ctx.send(embed=msg)
            
    @commands.hybrid_command(name="chickenrarities", aliases=["cr"], usage="chickenRarities", description="Check the rarities of the chickens.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def check_chicken_rarities(self, ctx: Context) -> None:
        """
        Check the rarities of the chickens.

        Args:
            ctx (Context): The context of the command.
        
        Returns:
            None
        """
        rarity_info = "\n".join([f"{get_rarity_emoji(rarity)} **{rarity}**: {round(rate/100, 4)}%" for rarity, rate in rollRates.items()])
        await send_bot_embed(ctx, title="Chicken Rarities:", description=rarity_info)

    @commands.hybrid_command(name="chickenvalues", aliases=["cv"], usage="chickenValues", description="Check the values of eggs produced by chickens.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def check_chicken_values(self, ctx: Context) -> None:
        """
        Check the amount of eggs produced by chickens.

        Args:
            ctx (Context): The context of the command.

        Returns:
            None
        """
        value_info = "\n".join([f"{get_rarity_emoji(rarity)} **{rarity}**: {ChickenMultiplier[rarity].value}x" for rarity in ChickenMultiplier.__members__])
        await send_bot_embed(ctx, title="Amount of eggs produced by rarity:", description=value_info)
    
    @commands.hybrid_command(name="chickencorn", usage="chickencorn", description="Show all the chicken food values.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def chicken_corn(self, ctx: Context) -> None:
        """
        Show all the chicken food values.

        Args:
            ctx (Context): The context of the command.

        Returns:
            None
        """
        corn_info = "\n".join([f"{get_rarity_emoji(rarity)} **{rarity}**: {ChickenFood[rarity].value}" for rarity in ChickenFood.__members__])
        await send_bot_embed(ctx, title="Chicken food values:", description=corn_info)
    
    @commands.hybrid_command(name="chickenprices", aliases=["cprice"], usage="chickenPrices", description="Check the prices of the chickens.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def check_chicken_prices(self, ctx: Context) -> None:
        """
        Check the prices of the chickens.

        Args:
            ctx (Context): The context of the command.

        Returns:
            None
        """
        prices_info = "\n".join([f"{get_rarity_emoji(rarity)} **{rarity}**: {175 * ChickenRarity[rarity].value} eggbux" for rarity in ChickenRarity.__members__])
        await send_bot_embed(ctx, title="Chicken prices:", description=prices_info)

    @commands.hybrid_command(name="battleinfo", aliases=["binfo"], brief="Shows your current rank.", description="Shows your current rank.", usage="rank")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def player_rank(self, ctx: Context, user: discord.Member = None) -> None:
        """
        Shows your current rank.

        Args:
            ctx (Context): The context of the command.
            user (discord.Member, optional): The user to check the rank. Defaults to None, which is the author of the command.
        
        Returns:
            None
        """
        farm_data, user = await return_data(ctx, user)
        farm_data = farm_data["farm_data"]
        
        if farm_data:
            rank = await rank_determiner(farm_data['mmr'])
            msg = await make_embed_object(title=f":crossed_swords: {user.display_name}'s battle stats:")
            msg.add_field(name="🏆 Rank:", value=f"🥇 Rank: **{rank}**\n📊 MMR: **{farm_data['mmr']}**")
            wins = farm_data['wins']
            losses = farm_data['losses']
            highest_mmr = farm_data['highest_mmr']

            if wins + losses > 0:
                win_rate = round((wins / (wins + losses)) * 100, 2)
                msg.add_field(name="🏅 Win rate:", value=f"🔥 Wins: **{wins}**\n 🚫 Losses: **{losses}**\n 📖 Win rate: **{win_rate}%**")

            if highest_mmr > 0:
                msg.add_field(name="📈 Highest MMR:", value=f"**{highest_mmr}**")
            
            msg.set_thumbnail(url=user.display_avatar)
            await ctx.send(embed=msg)
            return
        
    @commands.hybrid_command(name="eggrank", aliases=["erank"], usage="rankInfo", description="Check the chicken matchmaking ranks.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def rank_info(self, ctx: Context) -> None:
        """
        Check the chicken matchmaking ranks.

        Args:
            ctx (Context): The context of the command.
        
        Returns:
            None
        """
        rank_info = "\n".join([f"{rank} - {weight} MMR" for rank, weight in chicken_ranking.items()])
        await send_bot_embed(ctx, title="Chicken matchmaking ranks:", description=rank_info)

    @commands.hybrid_command(name="farmprofit", aliases=["fp"], usage="farmprofit OPTIONAL [user]", description="Check the farm profit.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def farm_profit(self, ctx: Context, user: discord.Member = None) -> None:
        """
        Check the farm profit.

        Args:
            ctx (Context): The context of the command.
            user (discord.Member, optional): The user to check the farm. Defaults to None, which is the author of the command.
        
        Returns:
            None
        """
        data, user = await return_data(ctx, user)
        farm_data = data["farm_data"]
        user_data = data["user_data"]   

        if data["farm_data"]:
            if user:
                await update_user_param(ctx, user_data, data, user)

            if len(farm_data['chickens']) == 0:
                await send_bot_embed(ctx,description= f":no_entry_sign: {user.display_name}, you don't have any chickens.")
                return
            
            income, _ = await give_total_farm_profit(farm_data, 1, update=False)
            taxes = await farm_maintence_tax(farm_data)
            income_with_tax = income - taxes
            total_corn = sum([ChickenFood[chicken['rarity']].value for chicken in farm_data['chickens']])

            status_message = ""
            status_emoji = ""

            if income_with_tax > 0:
                status_emoji = ":white_check_mark:"
                status_message = f"Your farm is expected to generate a profit of **{income_with_tax}** eggbux per **{FARM_DROP // 3600}** hour(s)."
            elif income_with_tax == 0:
                description= f":no_entry_sign: {user.display_name}, your farm is expected to generate neither profit nor loss."
            else:
                status_emoji = ":no_entry_sign:"
                status_message = f"Your farm is expected to generate a loss of **{income_with_tax}** eggbux per **{FARM_DROP // 3600}** hour(s)."

            if income_with_tax != 0:
                    description = (
                    f"{status_emoji} {user.display_name}, "
                    f"{status_message} :money_with_wings:.\n"
                    f":egg: Eggs produced: **{income}**\n"
                    f":corn: Corn going to the chickens: **{total_corn}**\n"
                    f"🚜 Farm maintenance: **{taxes}**"
                )

            await send_bot_embed(ctx,description=description)

        else:
            await send_bot_embed(ctx,description= f":no_entry_sign: {user.display_name}, you don't have a farm.")

    @commands.hybrid_command(name="renamefarm", aliases=["rf"], usage="renameFarm <nickname>", description="Rename the farm.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def rename_farm(self, ctx: Context, nickname: str) -> None:
        """
        Renames the farm.

        Args:
            ctx (Context): The context of the command.
            nickname (str): The new nickname of the farm.
        
        Returns:
            None
        """
        farm_data = ctx.data["farm_data"]
        censor = profanity.contains_profanity(nickname)

        if censor:
            await send_bot_embed(ctx, description= f":no_entry_sign: {ctx.author.display_name}, you can't use profanity in the farm name.")
            return
        
        if len(nickname) > 20:
            await send_bot_embed(ctx, description= f":no_entry_sign: {ctx.author.display_name} The farm name must have a maximum of 20 characters.")
            return
        
        farm_data['farm_name'] = nickname
        await Farm.update(ctx.author.id, farm_name=nickname)
        await send_bot_embed(ctx,description= f"{ctx.author.display_name} Your farm has been renamed to {nickname}.")

    @commands.hybrid_command(name="renamechicken", aliases=["rc"], usage="renameChicken <index> <nickname>", description="Rename a chicken in the farm.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def rename_chicken(self, ctx: Context, index: int, nickname: str) -> None:
        """
        Renames a chicken in the farm.

        Args:
            ctx (Context): The context of the command.
            index (int): The index of the chicken to rename.
            nickname (str): The new nickname of the chicken.
        
        Returns:
            None
        """
        index -= 1
        farm_data = ctx.data["farm_data"]
        censor = profanity.contains_profanity(nickname)

        if index > len(farm_data['chickens']) or index < 0:
            await send_bot_embed(ctx, description= f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
            return

        if censor:
            await send_bot_embed(ctx, description= f":no_entry_sign: {ctx.author.display_name}, you can't use profanity in the chicken name.")
            return
        
        if len(nickname) > 15:
            await send_bot_embed(ctx, description= f":no_entry_sign: {ctx.author.display_name}, the chicken name must have a maximum of 15 characters.")
            return
        
        check_nickname = nickname.upper()

        if check_nickname in ChickenRarity.__members__:
            await send_bot_embed(ctx, description= f":no_entry_sign: {ctx.author.display_name}, you can't rename a chicken with a rarity name.")
            return
        
        chicken_arr = farm_data['chickens']

        for i, _ in enumerate(chicken_arr):
            if index == i:
                chicken_arr[i]['name'] = nickname
                break

        farm_data['chickens'] = chicken_arr
        await Farm.update(ctx.author.id, chickens=farm_data['chickens'])
        await send_bot_embed(ctx,description= f":white_check_mark: {ctx.author.display_name}, the chicken has been renamed to {nickname}.")

    @commands.hybrid_command(name="switchchicken", aliases=["switch"], usage="switchChicken <index> <index2>", description="Switch the position of two chickens.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def switch_chicken(self, ctx: Context, index: int, index2: int) -> None:
        """
        Switch chickens positions in the farm.

        Args:
            ctx (Context): The context of the command.
            index (int): The index of the first chicken.
            index2 (int): The index of the second chicken.

        Returns:
            None
        """
        farm_data = ctx.data["farm_data"]

        if index > len(farm_data['chickens']) or index < 0 or index2 > len(farm_data['chickens']) or index2 < 0:
            await send_bot_embed(ctx,description= f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
            return
        
        farm_data['chickens'][index - 1], farm_data['chickens'][index2 - 1] = farm_data['chickens'][index2 - 1], farm_data['chickens'][index - 1]
        await Farm.update(ctx.author.id, chickens=farm_data['chickens'])
        await send_bot_embed(ctx,description= f":white_check_mark: {ctx.author.display_name}, the chickens have been switched.")
    
    @commands.hybrid_command(name="redeemables", aliases=["redeem"], usage="redeemables", description="Check the redeemable items.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def redeemables(self, ctx: Context) -> None:
        """
        Check the redeemable items.

        Args:
            ctx (Context): The context of the command.
        
        Returns:
            None
        """
        farm_data = await user_cache_retriever(ctx.author.id)
        farm_data = farm_data["farm_data"]
        redeemables = farm_data['redeemables']

        if not redeemables:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have any redeemable items.")
            return
        
        redeemables_info = "\n".join(
            [f"**{index + 1}.** {get_rarity_emoji(redeemable['rarity'])} **{redeemable['rarity']}** **{redeemable['name']}**" 
            for index, redeemable in enumerate(redeemables)]
        )
        msg = await make_embed_object(
            title=f":gift: {ctx.author.display_name}'s redeemable items:", 
            description=redeemables_info
        )
        
        view = ChickenSelectView(
            chickens=redeemables, 
            author=ctx.author, 
            action="R", 
            embed_text=msg, 
            author_cached_data=ctx.data, 
            has_cancel_button=False
        )
        await ctx.send(embed=msg, view=view)
        
async def setup(bot):
    await bot.add_cog(ChickenView(bot))