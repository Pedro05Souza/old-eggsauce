from discord import SelectOption, ui
from lib.chickenlib import get_rarity_emoji, get_max_chicken_limit
from lib import make_embed_object, send_bot_embed
from resources.settings import TAX
from db import Market, User, Farm
import discord

__all__ = ["PlayerMarketMenu"]

class PlayerMarketMenu(ui.Select):

    def __init__(self, offers: list, message: discord.Embed, author: discord.Member, instance_bot: discord.Client, author_cached_data: dict, options: list = None):
        self.offers = offers
        self.message = message
        self.author = author
        self.instance_bot = instance_bot
        self.farm_data = author_cached_data['farm_data']
        self.user_data = author_cached_data['user_data']
        super().__init__(min_values=1, max_values=1, options=options, placeholder="Select the chicken to buy:")
    
    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Responsable for buying chickens from the player market command.

        Args:
            interaction (discord.Interaction): The interaction object.

        Returns:
            None
        """
        if interaction.user.id != self.author.id:
            return await send_bot_embed(interaction, description=":no_entry_sign: You can't buy chickens for another user.", ephemeral=True)
        
        index = self.values[0]
        offer = self.offers[int(index)]

        if not self.farm_data:
            return await send_bot_embed(interaction, description=":no_entry_sign: You do not have a farm.", ephemeral=True)
        
        if offer['price'] > self.user_data['points']:
            return await send_bot_embed(interaction, description=":no_entry_sign: You don't have enough eggbux to buy this chicken.", ephemeral=True)
        
        self.farm_data['chickens'].append(offer['chicken'])

        if len(self.farm_data['chickens']) > await get_max_chicken_limit(self.farm_data):
            return await send_bot_embed(interaction, description=":no_entry_sign: You hit the maximum limit of chickens in the farm.", ephemeral=True)
        
        msg = await make_embed_object(description=f":white_check_mark: {self.author.display_name} have successfully bought the **{await get_rarity_emoji(offer['chicken']['rarity'])}{offer['chicken']['rarity']}** chicken for {offer['price']} eggbux.")
        
        await interaction.response.send_message(embed=msg)
        await Market.delete(offer['offer_id'])
        await User.update_points(self.author.id, points=self.user_data['points'] - offer['price'])
        await Farm.update(self.author.id, chickens=self.farm_data['chickens'])
        await self.on_chicken_bought(offer)
        await interaction.message.delete()

    async def on_chicken_bought(self, offer: dict) -> None:
        """
        Called when a chicken is bought from the player market.

        Args:
            offer (dict): The offer that was bought.

        Returns:
            None
        """
        user_data = await User.read(offer['author_id'])
        take_off = int(offer['price'] * TAX)
        total = offer['price'] - take_off
        await User.update_points(offer['author_id'], points=user_data['points'] + total)
        user = self.instance_bot.get_user(offer['author_id'])
        user = user if user else await self.instance_bot.fetch_user(offer['author_id'])
        if user:
            try:
                msg = await make_embed_object(description=f":white_check_mark: Your **{await get_rarity_emoji(offer['chicken']['rarity'])}{offer['chicken']['rarity']}** has been bought for **{offer['price']}** eggbux. After a {int(TAX * 100)}% tax, you have received **{total}** eggbux.")
                await user.send(embed=msg)
            except Exception:
                print(f"User {offer['author_id']} has disabled DMs.")
        else:
            print(f"User {offer['author_id']} not found.")