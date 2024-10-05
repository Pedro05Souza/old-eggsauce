"""
This module contains the player market commands for the chicken system.
"""
from discord.ext import commands
from db import Farm, Market
from lib import send_bot_embed, make_embed_object, confirmation_embed, format_number, user_cache_retriever
from lib.chickenlib import get_rarity_emoji, is_non_market_place_chicken, ChickenRarity, EventData
from resources import REGULAR_COOLDOWN, OFFER_EXPIRE_TIME
from tools import pricing
from views.selection import ChickenSelectView
from better_profanity import profanity
from discord.ext.commands import Context
import discord

__all__ = ["PlayerMarket"]

class PlayerMarket(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="offerchicken", aliases=["offer"], brief="Register a chicken to the player market.", description="Register a chicken to the player market.", usage="<index> OPTIONAL <description>")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def register_offer(self, ctx: Context, index: int, price: int, *, desc: str = None) -> None:
        """
        Register a chicken to the player market.

        Args:
            ctx (Context): The context of the command.
            index (int): The index of the chicken to register.
            price (int): The price of the chicken.
            desc (str, optional): The description of the chicken. Defaults to None.
        
        Returns:
            None
        """
        index -= 1
        description = ""
        farm_data = ctx.data['farm_data']
        if farm_data:
            
            total_user_offers = await Market.get_user_offers(ctx.author.id)

            if not total_user_offers:
                total_user_offers = []

            if index < 0 or index >= len(farm_data['chickens']):
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have a chicken at that index.")
                return
            
            if price < 50 or price > 500000:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you cannot set a price lower than **50** eggbux or higher than **250,000** eggbux.")
                return
            
            if desc:
                censor = profanity.contains_profanity(desc)
                if censor:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, your description contains profanity.")

                    return
                if len(desc) > 25:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, your description cannot be longer than **25** characters.")

                    return
                else:
                    description = desc
            else:
                description = "No description provided."
            
            if len(total_user_offers) >= 8:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can only have a maximum of 8 active offers.")
                return
            
            selected_chicken = farm_data['chickens'][index]

            if await is_non_market_place_chicken(selected_chicken['rarity']):
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you cannot register this chicken to the player market.")
                return
            
            if not await EventData.is_yieldable(ctx, ctx.author):
                return
            
            confirmation = await confirmation_embed(ctx, ctx.author, f"{ctx.author.display_name}, are you sure you want to register your **{get_rarity_emoji(selected_chicken['rarity'])}{selected_chicken['rarity']} {selected_chicken['name']}** to the player market for **{price}** eggbux?")
            
            if confirmation:
                
                async with EventData.manage_event_context(ctx.author):
                    await Market.create(ctx.author.id, selected_chicken, price, description, ctx.author.id)
                    await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, you have successfully registered your chicken to the player market. If no one buys it, it automatically gets back to your farm after **{OFFER_EXPIRE_TIME}** hours.")
                    farm_data['chickens'].pop(index)
                    await Farm.update(ctx.author.id, chickens=farm_data['chickens'])
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you have cancelled the offer registration.")
    
    @commands.hybrid_command(name="viewoffers", aliases=["offers"], description="Shows your current market offers.", usage="viewplrmarket OPTIONAL [user]")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def view_offers(self, ctx: Context, user: discord.Member = None) -> None:
        """
        Shows the player's current market offers.

        Args:
            ctx (Context): The context of the command.
            user (discord.Member, optional): The user to check the offers. Defaults to None, which is the author of the command.
        
        Returns:
            None
        """
        if user is None:
            user = ctx.author
        current_offers = await Market.get_user_offers(user.id)
        if current_offers:
            msg = await make_embed_object(
                title=f":chicken: {user.display_name}'s Market Offers",
                description=(
                    "Here are your current market offers:\n\n" +
                    "\n\n".join([
                        f"**{i+1}.** **{get_rarity_emoji(offer['chicken']['rarity'])}"
                        f"{offer['chicken']['rarity']} {offer['chicken']['name']}** - "
                        f"**Price:** {await format_number(offer['price'])} eggbux. :money_with_wings: \n"
                        f"**:gem: Upkeep rarity**: {(offer['chicken']['upkeep_multiplier']) * 100}% \n"
                        f"**:scroll: Description:** {offer['description']}"
                        for i, offer in enumerate(current_offers)
                    ])
                )
            )
            await ctx.send(embed=msg)
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name}, has no active market offers.")

    @discord.app_commands.command(name="searchchicken", description="Search for a chicken in the player market.")
    @discord.app_commands.describe(
        chicken_rarity="OPTIONAL <chicken rarity>",
        upkeep_rarity="OPTIONAL <upkeep rarity>",
        price="OPTIONAL <price>",
        author="OPTIONAL [author]"
    )
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def search_chicken(self, interaction: discord.Interaction, chicken_rarity: str = None, upkeep_rarity: int = None, price: int = None, author: discord.Member = None):
        """
        Search for a maximum 10 chickens offered by other players.

        Args:
            interaction (discord.Interaction): The interaction of the command.
            chicken_rarity (str, optional): The rarity of the chicken. Defaults to None.
            upkeep_rarity (int, optional): The upkeep rarity of the chicken. Defaults to None.
            price (int, optional): The price of the chicken. Defaults to None.
            author (discord.Member, optional): The author of the chicken. Defaults to None.
        """
        cache = await user_cache_retriever(interaction.user.id)
        search_param = [chicken_rarity, upkeep_rarity, price, author]

        if all([not param for param in search_param]):
            await send_bot_embed(interaction, ephemeral=True, description=f":no_entry_sign: {interaction.user.display_name}, you need to provide at least one search parameter.")
            return
        
        if upkeep_rarity:
            if upkeep_rarity < 0 or upkeep_rarity > 100:
                await send_bot_embed(interaction, ephemeral=True, description=f":no_entry_sign: {interaction.user.display_name}, the upkeep rarity must be between **0%** and **100%**.")
                return  
            upkeep_rarity = upkeep_rarity / 100

        if chicken_rarity:
            chicken_rarity = chicken_rarity.upper()
            if chicken_rarity not in ChickenRarity.__members__:
                await send_bot_embed(interaction, ephemeral=True, description=f":no_entry_sign: {interaction.user.display_name}, the chicken rarity provided is not valid.")
                return
            
        search = await Market.get_chicken_offers(chicken_rarity=chicken_rarity, upkeep_rarity=upkeep_rarity, price=price, author_id=author.id if author else None)

        if search:
            search = await self.search_organizer(interaction, search)

            if search:
                msg = await make_embed_object(
                title=":chicken: Search results",
                description=(
                    "Here are the current player market offers:\n\n" +
                    "\n\n".join([
                        f"**{i+1}.** **{get_rarity_emoji(offer['chicken']['rarity'])}"
                        f"{offer['chicken']['rarity']} {offer['chicken']['name']}** - "
                        f"**Price:** {await format_number(offer['price'])} eggbux. :money_with_wings:\n"
                        f"**:gem: Upkeep rarity**: {(offer['chicken']['upkeep_multiplier']) * 100}% \n"
                        f"**:scroll: Description:** {offer['description']} \n"
                        f"**:bust_in_silhouette: Seller:** {offer['author_name']}"
                        for i, offer in enumerate(search)
                    ])
                )
            )
                view = ChickenSelectView(chickens=search, author=interaction.user, embed_text=msg, action="PM", instance_bot=self.bot, author_cached_data=cache, has_cancel_button=False)
                await interaction.response.send_message(embed=msg, view=view)
            else:
                await send_bot_embed(interaction, ephemeral=True, description=f":no_entry_sign: No offers found with the parameters provided.")
        else:
            await send_bot_embed(interaction, ephemeral=True, description=f":no_entry_sign: No offers found with the parameters provided.")

    async def search_organizer(self, interaction: discord.Interaction, db_request: list) -> list:
        """
        Organizes the search results.

        Args:
            interaction (discord.Interaction): The interaction of the command.
            db_request (list): The list of offers.
        
        Returns:
            list
        """
        offers = db_request
        offers_copy = offers.copy()
        if offers:
            for offer in offers:
                if offer['author_id'] == interaction.user.id:
                    continue
                else:
                    member = self.bot.get_user(offer['author_id'])
                    if member:
                        offer['author_name'] = member.name
                    else:
                        await Market.delete(offer['author_id'])
            offers_copy = [offer for offer in offers if offer.get('author_name')]
            offers = offers_copy
            return offers
        else:
            return None
        
async def setup(bot):
    await bot.add_cog(PlayerMarket(bot))
        