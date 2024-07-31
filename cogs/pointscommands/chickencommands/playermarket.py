from discord.ext import commands
from db.farmDB import Farm
from db.MarketDB import Market
from tools.shared import send_bot_embed, make_embed_object
from tools.chickens.chickenshared import get_rarity_emoji, verify_events, offer_expire_time
from tools.shared import confirmation_embed
from tools.chickens.chickeninfo import ChickenRarity
from tools.chickens.chickenhandlers import EventData
from tools.chickens.selection.chickenselection import ChickenSelectView
from better_profanity import profanity
import discord

class PlayerMarket(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="offerchicken", aliases=["offer"], brief="Register a chicken to the player market.", description="Register a chicken to the player market.", usage="<index> OPTIONAL <description>")
    async def register_offer(self, ctx, index: int, price: int, *, desc: str = None):
        """Register a chicken to the player market."""
        index -= 1
        description = ""
        farm_data = Farm.read(ctx.author.id)
        if farm_data:
            if await verify_events(ctx, ctx.author):
             return
            r = EventData(ctx.author)
            total_user_offers = Market.get_user_offers(ctx.author.id)
            if not total_user_offers:
                total_user_offers = []
            if index < 0 or index >= len(farm_data['chickens']):
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have a chicken at that index.")
                EventData.remove(r)
                return
            if price < 50 or price > 500000:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you cannot set a price lower than **50** eggbux or higher than **250,000** eggbux.")
                EventData.remove(r)
                return
            if desc:
                censor = profanity.contains_profanity(desc)
                if censor:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, your description contains profanity.")
                    EventData.remove(r)
                    return
                if len(desc) > 50:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, your description cannot be longer than **50** characters.")
                    EventData.remove(r)
                    return
                else:
                    description = desc
            else:
                description = "No description provided."
            if len(total_user_offers) >= 8:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can only have a maximum of 8 active offers.")
                EventData.remove(r)
                return
            selected_chicken = farm_data['chickens'][index]
            if selected_chicken['rarity'] == "DEAD":
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you cannot sell a dead chicken.")
                EventData.remove(r)
                return
            if selected_chicken['rarity'] == "ETHEREAL":
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you cannot sell an ethereal chicken.")
                EventData.remove(r)
                return
            confirmation = await confirmation_embed(ctx, ctx.author, f"{ctx.author.display_name}, are you sure you want to register your **{get_rarity_emoji(selected_chicken['rarity'])}{selected_chicken['rarity']} {selected_chicken['name']}** to the player market for **{price}** eggbux?")
            if confirmation:
                Market.create(ctx.author.id, selected_chicken, price, description, ctx.author.id)
                await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, you have successfully registered your chicken to the player market. If no one buys it, it automatically gets back to your farm after **{offer_expire_time}** hours.")
                farm_data['chickens'].pop(index)
                Farm.update(ctx.author.id, chickens=farm_data['chickens'])
                EventData.remove(r)
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you have cancelled the offer registration.")
                EventData.remove(r)
    
    @commands.hybrid_command(name="playeroffers", aliases=["offers"], description="Shows your current market offers.", usage="viewplrmarket OPTIONAL [user]")
    async def view_offers(self, ctx, user: discord.Member = None):
        """Shows the player's current market offers."""
        if user is None:
            user = ctx.author
        current_offers = Market.get_user_offers(user.id)
        if current_offers:
            msg = await make_embed_object(title=f":chicken: {user.display_name}'s Market Offers", description=f"Here are your current market offers:\n\n" + "\n\n".join([f"**{i+1}.** **{get_rarity_emoji(offer['chicken']['rarity'])}{offer['chicken']['rarity']} {offer['chicken']['name']}** - **Price:** {offer['price']} eggbux. :money_with_wings: \n **:gem: Upkeep rarity**: {(offer['chicken']['upkeep_multiplier']) * 100}% \n**:scroll: Description:** {offer['description']}" for i, offer in enumerate(current_offers)]))
            await ctx.send(embed=msg)
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name}, has no active market offers.")

    @commands.hybrid_command(name="searchchicken", aliases=["search"], description="Search for a chicken in the player market.", usage="OPTIONAL <chicken rarity> OPTIONAL <upkeep rarity> OPTIONAL <price> OPTIONAL [user]")
    async def search_chicken(self, ctx, chicken_rarity: str = None, upkeep_rarity: int = None, price: int = None, author: discord.Member = None):
        """Search for 10 chickens offered by other players."""
        search_param = [chicken_rarity, upkeep_rarity, price, author]
        if all([not param for param in search_param]):
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you need to provide at least one search parameter.")
            return
        if upkeep_rarity:
            if upkeep_rarity < 0 or upkeep_rarity > 100:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, the upkeep rarity must be between **0%** and **100%**.")
                return
            upkeep_rarity = upkeep_rarity / 100
        if chicken_rarity:
            chicken_rarity = chicken_rarity.upper()
            if chicken_rarity not in ChickenRarity.__members__:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, the chicken rarity provided is not valid.")
                return
        search = Market.get_chicken_offers(chicken_rarity=chicken_rarity, upkeep_rarity=upkeep_rarity, price=price, author_id=author.id if author else None)
        if search:
            search = await self.search_organizer(ctx, search)
            if search:
                msg = await make_embed_object(title=f":chicken: Search results", description=f"Here are the current player market offers:\n\n" + "\n\n".join([f"**{i+1}.** **{get_rarity_emoji(offer['chicken']['rarity'])}{offer['chicken']['rarity']} {offer['chicken']['name']}** - **Price:** {offer['price']} eggbux. :money_with_wings: \n **:gem: Upkeep rarity**: {(offer['chicken']['upkeep_multiplier']) * 100}% \n**:scroll: Description:** {offer['description']} \n **:bust_in_silhouette: Seller:** {offer['author_name']}" for i, offer in enumerate(search)]))
                view = ChickenSelectView(chickens=search, author=ctx.author, message=msg, action="PM", instance_bot=self.bot)
                await ctx.send(embed=msg, view=view)
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: No offers found with the parameters provided.")
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: No offers found with the parameters provided.")

    async def search_organizer(self, ctx, db_request: list):
        offers = db_request
        offers_copy = offers.copy()
        if offers:
            for offer in offers:
                if offer['author_id'] == ctx.author.id:
                    continue
                else:
                    member = self.bot.get_user(offer['author_id'])
                    if member:
                        offer['author_name'] = member.name
                    else:
                        offer['author_name'] = "Unknown User"
            offers_copy = [offer for offer in offers if offer.get('author_name')]
            offers = offers_copy
            return offers
        else:
            return None
        
async def setup(bot):
    await bot.add_cog(PlayerMarket(bot))
        