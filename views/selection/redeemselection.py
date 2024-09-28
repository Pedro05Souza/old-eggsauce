from discord import SelectOption, ui
from db import Farm
from lib import make_embed_object, send_bot_embed
from lib.chickenlib import get_rarity_emoji, get_max_chicken_limit
from resources import MAX_BENCH
import asyncio
import discord

__all__ = ["RedeemPlayerMenu"]

class RedeemPlayerMenu(ui.Select):

    def __init__(self, chickens: list, author: discord.Member, message: discord.Embed):
        self.chickens = chickens
        self.author = author
        self.message = message
        options = [
            SelectOption(
                label=f"{chicken['rarity']} {chicken['name']}", 
                value=str(index), 
                emoji=get_rarity_emoji(chicken['rarity'])
                )
            for index, chicken in enumerate(chickens)
        ]
        super().__init__(min_values=1, max_values=len(chickens), options=options, placeholder="Select the chickens to redeem:")

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Responsable for redeeming chickens from the player market command.

        Args:
            interaction (discord.Interaction): The interaction object.

        Returns:
            None
        """
        if interaction.user.id != self.author:
            await send_bot_embed(interaction, description=":no_entry_sign: You can't redeem chickens for another user.", ephemeral=True)
            return
        
        farm_data = await Farm.read(interaction.user.id)
        chickens_selected = [self.chickens[int(index)] for index in self.values]
        chickens_sucessfully_redeemed = []
        
        if len(chickens_selected) >= get_max_chicken_limit(farm_data):
            await send_bot_embed(interaction, description=":no_entry_sign: You can't redeem more chickens than the farm size.", ephemeral=True)
            return
        
        for chicken in chickens_selected:
            if len(farm_data['chickens']) >= get_max_chicken_limit(farm_data):
                if len(farm_data['bench']) >= MAX_BENCH:
                    await send_bot_embed(interaction, description=":no_entry_sign: You can't redeem more chickens than the farm size.", ephemeral=True)
                    return
                chickens_sucessfully_redeemed.append(chicken)
                farm_data['bench'].append(chicken)
            else:
                chickens_sucessfully_redeemed.append(chicken)
                farm_data['chickens'].append(chicken)

        await asyncio.sleep(1)
        await interaction.delete_original_response()
        msg = await make_embed_object(description=f":white_check_mark: {interaction.user.display_name} have redeemed the chickens: **{', '.join([get_rarity_emoji(chicken['rarity']) + ' ' + chicken['rarity'] + ' ' + chicken['name'] for chicken in chickens_sucessfully_redeemed])}**.")
        await interaction.followup.send(embed=msg)
        
