"""
This module handles events between users and their chickens.
"""
from discord.ext import commands
from db import Farm, User
from views.selection import ChickenSelectView
from lib.chickenlib import (
    get_usr_farm, get_rarity_emoji, create_chicken, determine_chicken_upkeep, get_max_chicken_limit, get_non_tradable_chickens,
    is_non_tradable_chicken, is_non_evolvable_chicken, EventData, ChickenRarity, load_farmer_upgrades
)
from tools import pricing, on_awaitable, on_user_transaction
from lib import send_bot_embed, confirmation_embed, user_cache_retriever, button_builder, button_view_builder
from resources import REGULAR_COOLDOWN, FARMER_PRICE
from discord.ext.commands import Context
import asyncio
import discord
import logging

logger = logging.getLogger("bot_logger")

__all__ = ["ChickenEvents"]

class ChickenEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="sellchicken", aliases=["sc"], usage="sellChicken", description="Deletes a chicken from the farm.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def sell_chicken(self, ctx: Context) -> None:
        """
        Deletes a chicken from the farm.
        
        Args:
            ctx (Context): The context of the command.
        
        Returns:
            None
        """
        farm_data = ctx.data["farm_data"]

        if not farm_data['chickens']:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} You don't have any chickens.")
            return
        
        if not await EventData.is_yieldable(ctx, ctx.author):
            return
        
        message = await get_usr_farm(ctx, ctx.author, ctx.data)
              
        async with EventData.manage_event_context(ctx.author, awaitable=True):
            view = ChickenSelectView(embed_text=message, chickens=farm_data['chickens'], author=ctx.author, action="D", author_cached_data=ctx.data)
            await ctx.send(embed=message, view=view)
                
    @commands.hybrid_command(name="evolvechicken", aliases=["ec", "fuse"], usage="evolveChicken <index> <index2>", description="Evolve a chicken if having 2 of the same rarity.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def evolve_chicken(self, ctx: Context, index: int, index2: int) -> None:
        """
        Evolves a chicken if having 2 of the same rarity.

        Args:
            ctx (Context): The context of the command.
            index (int): The index of the chicken to evolve.
            index2 (int): The index of the chicken to evolve.
        
        Returns:
            None
        """
        
        farm_data = ctx.data["farm_data"]

        if not farm_data['chickens']:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have any chickens.")
            return
        
        if index > len(farm_data['chickens']) or index < 0 or index2 > len(farm_data['chickens']) or index2 < 0:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
            return
        
        if index == index2:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't evolve a chicken with itself.")
            return
        
        chicken_selected = farm_data['chickens'][index - 1]
        chicken_removed = farm_data['chickens'][index2 - 1]

        if chicken_selected['rarity'] != chicken_removed['rarity']:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, the chickens must be of the same rarity to evolve.")
            return
        
        if await is_non_evolvable_chicken(chicken_selected['rarity']) or await is_non_evolvable_chicken(chicken_removed['rarity']):
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't evolve this chicken.")
            return
        
        if not await EventData.is_yieldable(ctx, ctx.author):
            return
        
        confirmation = await confirmation_embed(ctx, ctx.author, f"{ctx.author.display_name}, are you sure you want to evolve your **{get_rarity_emoji(chicken_selected['rarity'])}{chicken_selected['rarity']} {chicken_selected['name']}** to a higher rarity?")

        if confirmation:
            async with EventData.manage_event_context(ctx.author):
                rarity_list = list(ChickenRarity.__members__)
                chicken_selected['rarity'] = rarity_list[rarity_list.index(chicken_selected['rarity']) + 1]
                chicken_selected['upkeep_multiplier'] = determine_chicken_upkeep(chicken_selected)
                farm_data['chickens'].remove(chicken_removed)
                await Farm.update(ctx.author.id, chickens=farm_data['chickens'])
                await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, the chicken has been evolved to {chicken_selected['rarity']} {chicken_selected['name']}.")
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you have cancelled the evolution.")

    @commands.hybrid_command(name="farmer", aliases =["farmers"], usage="farmer", description="The farmers helps increase the productivity of the chickens.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def purchase_farmer(self, ctx: Context) -> None:
        """
        The farmers helps increase the productivity of the chickens in different ways.

        Args:
            ctx (Context): The context of the command.
        
        Returns:
            None
        """
        eggs_needed = FARMER_PRICE * 2
        message = await send_bot_embed(ctx, title=":farmer: Farmer roles:\n", description="\n".join(await self.farmers_descriptions(eggs_needed)))
        emojis = ["💰", "🛡️", "💼", "⚔️", "🍃", "🎟️"]
        buttons = []

        for emoji in emojis:
            buttons.append(await button_builder(emoji=emoji, style=discord.ButtonStyle.secondary, custom_id=emoji))

        view = await button_view_builder(*buttons)
        await message.edit(view=view)

        try:
            interaction = await self.bot.wait_for("interaction", check=lambda i: i.message.id == message.id and i.user.id == ctx.author.id, timeout=60)
            await interaction.response.defer()
            user_data = ctx.data["user_data"]
            farm_data = ctx.data["farm_data"]

            if user_data['points'] >= FARMER_PRICE:
                if farm_data['eggs_generated'] < eggs_needed:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you need to produce at least {eggs_needed} eggs in order to purchase a farmer role.")
                    return
                
                farm_size = get_max_chicken_limit(farm_data)

                if len(farm_data['chickens']) >= farm_size and len(farm_data['chickens']) > 8:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} you have a Warrior farmer, you need to sell the extra farm slots to buy another farmer.")
                    return
                
                farmer_dict = await self.retrieve_farmer_dict()
                await self.buy_farmer_upgrade(ctx, farmer_dict[interaction.data['custom_id']], FARMER_PRICE, user_data, farm_data)
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have enough eggbux to purchase a farmer role.")
        except asyncio.TimeoutError:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you have not selected a farmer role.")

    async def farmers_descriptions(self, eggs_needed: int) -> str:
        """
        Gets all the farmer roles descriptions.

        Args:
            eggs_needed (int): The amount of eggs needed to buy a farmer role.

        Returns:
            str
        """
        description = [
            f":moneybag: Rich Farmer: Increase the egg value of the chickens by **{load_farmer_upgrades('Rich Farmer')[0]}%** and increases the hourly corn production by **{load_farmer_upgrades('Rich Farmer')[1]}%**\n",
            f":shield: Guardian Farmer: Whenever you sell a chicken, sell it for the full price and reduces farm taxes by **{load_farmer_upgrades('Guardian Farmer')}%**.\n",
            f":briefcase: Executive Farmer: Gives you **{load_farmer_upgrades('Executive Farmer')[0]}** more daily rolls in the market and chickens generated in the market comes with **{load_farmer_upgrades('Executive Farmer')[1]}%** discount. \n",
            f":crossed_swords: Warrior Farmer: Gives **{load_farmer_upgrades('Warrior Farmer')}** more farm slots.\n",
            f":leaves: Sustainable Farmer: Auto-feeds the chickens every **{load_farmer_upgrades('Sustainable Farmer')[0] // 3600}** hours, the happiness generated is a number between **{load_farmer_upgrades('Sustainable Farmer')[1][0]}-{load_farmer_upgrades('Sustainable Farmer')[1][1]}%**. The farmer uses the money from your bank account.\n",
            f":tickets: Generous Farmer: Increases the maximum chickens generated in the market by **{load_farmer_upgrades('Generous Farmer')[0]}** slots.\n"
            f"\n\nAll the farmer roles have a cost of **{FARMER_PRICE}** eggbux and you can only buy one of them. Buying a farmer when you already have one will override the existing one. You need at least **{eggs_needed}** total eggs produced by your farm in order to buy them.\nReact with the corresponding emoji to purchase the role."
        ]
        return description

    async def retrieve_farmer_dict(self) -> dict:
        """
        Retrieves a dictionary of the farmer roles.

        Returns:
            dict
        """
        farmer_dict = {
            "💰": "Rich Farmer",
            "🛡️": "Guardian Farmer",
            "💼": "Executive Farmer",
            "⚔️": "Warrior Farmer",
            "🍃": "Sustainable Farmer",
            "🎟️": "Generous Farmer"
        }
        return farmer_dict

    async def buy_farmer_upgrade(self, ctx: Context, name: str, farmer_price: int, user_data: dict, farm_data: dict) -> None:
        """
        Buy the farmer upgrade

        Args:
            ctx (Context): The context of the command.
            name (str): The name of the farmer.
            farmer_price (int): The price of the farmer.
            user_data (dict): The user data.
            farm_data (dict): The farm data.

        Returns:
            None
        """
        if farm_data['farmer'] == name:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you already have the {name} farmer role.")
            return
        
        if name == "Sustainable Farmer":
            await Farm.add_last_farm_drop_attribute(ctx.author.id)

        if await self.verify_player_has_sustainable(farm_data) and not name == "Sustainable Farmer":
            await Farm.remove_last_farm_drop_attribute(ctx.author.id)

        farm_data['farmer'] = name
        await User.update_points(ctx.author.id, user_data['points'] - farmer_price)
        await Farm.update(ctx.author.id, farmer=name)
        await on_user_transaction(ctx, farmer_price, 1)
        await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, you have purchased the {name} farmer role.")
        return
    
    @commands.hybrid_command(name="transcend", usage="transcend", description="Only available when having 8 ascended chickens.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def transcend(self, ctx: Context) -> None:
        """
        Transcend 8 ascended chickens to an ethereal chicken.

        Args:
            ctx (Context): The context of the command.
        
        Returns:
            None
        """
        farm_data = ctx.data["farm_data"]
        ascended_chickens = [chicken for chicken in farm_data['chickens'] if chicken['rarity'] == 'ASCENDED']
        extra_ascended_chickens = []

        if len(ascended_chickens) < 8:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you need to have ** {8 - len(ascended_chickens)} more {get_rarity_emoji('ASCENDED')} ASCENDED chickens** in order to transcend them.")
            return
        
        elif len(ascended_chickens) > 8:
            extra_ascended_chickens = [chicken for chicken in ascended_chickens[8:]]
        
        if not await EventData.is_yieldable(ctx, ctx.author):
            return

        if await confirmation_embed(ctx, ctx.author, f"{ctx.author.display_name}, are you sure you want to transcend your 8 ascended chickens to an ETHEREAL Chicken?"):

            async with EventData.manage_event_context(ctx.author):
                transcended_chicken = await create_chicken("ETHEREAL", "transcend")
                farm_data['chickens'] = [for_chicken for for_chicken in farm_data['chickens'] if for_chicken['rarity'] != "ASCENDED"]
                farm_data['chickens'].extend(extra_ascended_chickens)
                farm_data['chickens'].append(transcended_chicken)
                await Farm.update(ctx.author.id, chickens=farm_data['chickens'])
                await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, you have transcended your chickens to an **{get_rarity_emoji('ETHEREAL')} ETHEREAL Chicken.**")
        
    async def verify_player_has_sustainable(self, farm_data: dict) -> bool:
        """
        Verify if the player has the sustainable farmer role.

        Args:
            farm_data (dict): The farm data.

        Returns:
            bool
        """
        return farm_data['farmer'] == "Sustainable Farmer"
            
async def setup(bot):
    await bot.add_cog(ChickenEvents(bot))