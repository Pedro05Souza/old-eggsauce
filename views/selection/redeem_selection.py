from discord import SelectOption, ui
from lib import make_embed_object, send_bot_embed, user_cache_retriever
from lib.chickenlib import get_rarity_emoji, get_max_chicken_limit
from resources import MAX_BENCH
import asyncio
import discord

__all__ = ["RedeemPlayerMenu"]

class RedeemPlayerMenu(ui.Select):

    def __init__(self, chickens: list, author: discord.Member, message: discord.Embed, author_cached_data: dict, options: list = None):
        self.chickens = chickens
        self.author = author
        self.message = message
        self.farm_data = author_cached_data
        super().__init__(min_values=1, max_values=len(chickens), options=options, placeholder="Select the chickens to redeem:")

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Responsable for redeeming chickens from the player market command.

        Args:
            interaction (discord.Interaction): The interaction object.

        Returns:
            None
        """
        if interaction.user.id != self.author.id:
            await send_bot_embed(interaction, description=":no_entry_sign: You can't redeem chickens for another user.", ephemeral=True)
            return
        
        chickens_selected = [self.chickens[int(index)] for index in self.values]
        chickens_sucessfully_redeemed = []
        
        if len(chickens_selected) >= await get_max_chicken_limit(self.farm_data):
            await send_bot_embed(interaction, description=":no_entry_sign: You can't redeem more chickens than the farm size.", ephemeral=True)
            return
        
        for chicken in chickens_selected:

            if len(self.farm_data['chickens']) >= await get_max_chicken_limit(self.farm_data):

                if len(self.farm_data['bench']) >= MAX_BENCH:
                    await send_bot_embed(interaction, description=":no_entry_sign: You can't redeem more chickens than the farm size.", ephemeral=True)
                    return
                chickens_sucessfully_redeemed.append(chicken)
                self.farm_data['bench'].append(chicken)
            else:
                chickens_sucessfully_redeemed.append(chicken)
                self.farm_data['chickens'].append(chicken)

        await asyncio.sleep(1)
        await interaction.delete_original_response()
        msg = await make_embed_object(description=f":white_check_mark: {interaction.user.display_name} have redeemed the chickens: **{', '.join([await get_rarity_emoji(chicken['rarity']) + ' ' + chicken['rarity'] + ' ' + chicken['name'] for chicken in chickens_sucessfully_redeemed])}**.")
        await interaction.followup.send(embed=msg)
        
