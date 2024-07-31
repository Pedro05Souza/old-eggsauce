from discord import SelectOption, ui
from tools.chickens.chickenshared import get_rarity_emoji, get_max_chicken_limit
from tools.shared import make_embed_object, tax
from db.userDB import User
from db.farmDB import Farm
from db.MarketDB import Market

class PlayerMarketMenu(ui.Select):
    """Menu to buy chickens from the market"""
    def __init__(self, offers, message, author, instance_bot):
        self.offers = offers
        self.message = message
        self.author = author
        self.instance_bot = instance_bot
        options = [
            SelectOption(label=f"{offer['chicken']['rarity']}", description=f"Price: {offer['price']} eggbux", value=str(index), emoji=get_rarity_emoji(offer['chicken']['rarity']))
            for index, offer in enumerate(offers)
        ]
        super().__init__(min_values=1, max_values=1, options=options, placeholder="Select the chicken to buy:")
    
    async def callback(self, interaction):
        """Callback for the interaction"""
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("You cannot select a chicken for another user.")
        index = self.values[0]
        offer = self.offers[int(index)]
        author_data = User.read(self.author.id)
        farm_data = Farm.read(self.author.id)
        if not farm_data:
            return await interaction.response.send_message("You do not have a farm.", ephemeral=True)
        if offer['price'] > author_data['points']:
            return await interaction.response.send_message("You do not have enough eggbux to buy this chicken.")
        farm_data['chickens'].append(offer['chicken'])
        if len(farm_data['chickens']) > get_max_chicken_limit(farm_data):
            return await interaction.response.send_message("You can't buy more chickens as you have reached the maximum limit.", ephemeral=True)
        msg = await make_embed_object(description=f":white_check_mark: {self.author.display_name} have successfully bought the **{get_rarity_emoji(offer['chicken']['rarity'])}{offer['chicken']['rarity']}** chicken for {offer['price']} eggbux.")
        await interaction.response.send_message(embed=msg)
        Market.delete(offer['offer_id'])
        User.update_points(self.author.id, points=author_data['points'] - offer['price'])
        Farm.update(self.author.id, chickens=farm_data['chickens'])
        await self.on_chicken_bought(offer)
        await interaction.message.delete()

    async def on_chicken_bought(self, offer):
        """Callback for the chicken being bought"""
        user_data = User.read(offer['author_id'])
        take_off = int(offer['price'] * tax)
        total = offer['price'] - take_off
        User.update_points(offer['author_id'], points=user_data['points'] + total)
        user = self.instance_bot.get_user(offer['author_id'])
        user = user if user else await self.instance_bot.fetch_user(offer['author_id'])
        if user:
            try:
                msg = await make_embed_object(description=f":white_check_mark: Your **{get_rarity_emoji(offer['chicken']['rarity'])}{offer['chicken']['rarity']}** has been bought for **{offer['price']}** eggbux. After a {int(tax * 100)}% tax, you have received **{total}** eggbux.")
                await user.send(embed=msg)
            except Exception:
                print(f"User {offer['author_id']} has disabled DMs.")
        else:
            print(f"User {offer['author_id']} not found.")
        
        



