from discord.ext import commands
from db.farmDB import Farm
from db.MarketDB import Market
from tools.shared import create_embed_without_title, make_embed_object
from tools.chickens.chickenshared import get_rarity_emoji


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
            total_user_offers = Market.get_user_offers(ctx.author.id)
            if not total_user_offers:
                total_user_offers = []
            if index < 0 or index >= len(farm_data['chickens']):
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have a chicken at that index.")
                return
            if price < 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you cannot set a negative price.")
                return
            if desc:
                description = desc
            if len(total_user_offers) >= 8:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can only have a maximum of 8 active offers.")
                return
            selected_chicken = farm_data['chickens'][index]
            Market.create(ctx.author.id, selected_chicken, price, description, ctx.author.id)
            await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, you have successfully registered your chicken to the player market. If no one buys it, it automatically gets back to your farm after **24** hours.")
            farm_data['chickens'].pop(index)
            Farm.update(ctx.author.id, chickens=farm_data['chickens'])
    
    @commands.hybrid_command(name="viewplrmarket", aliases=["vpm"], description="Shows your current market offers.", usage="viewplrmarket")
    async def view_offers(self, ctx):
        """Shows the player's current market offers."""
        current_offers = Market.get_user_offers(ctx.author.id)
        if current_offers:
            msg = await make_embed_object(title=f"{ctx.author.display_name}'s Market Offers", description=f"Here are your current market offers:\n" + "\n\n".join([f"**{i+1}.** **{get_rarity_emoji(offer['chicken']['rarity'])}{offer['chicken']['rarity']} {offer['chicken']['name']}** - **Price:** {offer['price']} eggbux. - **Description:** {offer['description']}" for i, offer in enumerate(current_offers)]))
            await ctx.send(embed=msg)
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you have no market offers.")

async def setup(bot):
    await bot.add_cog(PlayerMarket(bot))
        