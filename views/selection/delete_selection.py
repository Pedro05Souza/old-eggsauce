from discord import SelectOption, ui
from db import Farm, User
from tools import on_awaitable
from lib.chickenlib import get_chicken_price, get_rarity_emoji, check_if_author
from lib import make_embed_object, confirmation_embed, user_cache_retriever_copy
import asyncio
import discord

__all__ = ["ChickenDeleteMenu"]

class ChickenDeleteMenu(ui.Select):

    def __init__(self, chickens: list, author: discord.Member, message: discord.Embed, author_cached_data: dict):
        options = [
            SelectOption(
                label=chicken['name'], 
                description=f"{chicken['rarity']} {get_chicken_price(chicken)}", 
                value=str(index), 
                emoji=get_rarity_emoji(chicken['rarity'])
                )
            for index, chicken in enumerate(chickens) if chicken['rarity'] != "DEAD" or chicken['rarity'] != "ETHEREAL"
        ]
        self.chickens = chickens
        self.author = author
        self.message = message
        self.farm_data = author_cached_data['farm_data'].copy()
        self.data = author_cached_data
        super().__init__(min_values=1, max_values=len(chickens), options=options, placeholder="Select the chickens to delete:")

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Responsable for deleting chickens from the farm.

        Args:
            interaction (discord.Interaction): The interaction object.

        Returns:
            None
        """
        if not await check_if_author(self.author.id, interaction.user.id, interaction):
            return

        chickens_selected = [self.chickens[int(value)] for value in self.values]
        refund_price = await self.calculate_refund_price(chickens_selected)

        confirmation = await confirmation_embed(interaction, interaction.user, f"{interaction.user.display_name}, are you sure you want to delete the selected chickens for {refund_price} eggbux?")

        if confirmation:
            if self.view.is_finished():
                return

            await self.handle_chicken_deletion(interaction, self.data, self.farm_data, chickens_selected, refund_price)
        else:
            embed = await make_embed_object(description=f":x: {interaction.user.display_name} have cancelled the deletion of the selected chickens.")
            await interaction.followup.send(embed=embed)
            await on_awaitable(interaction.user.id)
            await asyncio.sleep(2.5)
            await interaction.message.delete()


    async def handle_chicken_deletion(
            self, 
            interaction: discord.Interaction, 
            data: dict, 
            farm_data: dict, 
            chickens_selected: list, 
            refund_price: int
            ) -> None:
        """
        Handles the deletion of the chickens.

        Args:
            interaction (discord.Interaction): The interaction object.

        Returns:
            None
        """
        for chicken in chickens_selected:
            farm_data['chickens'].remove(chicken)
        user_data = data["user_data"]
        await Farm.update(interaction.user.id, chickens=farm_data['chickens'])
        await User.update_points(interaction.user.id, user_data['points'] + refund_price)
        embed = await make_embed_object(description=f":white_check_mark: {interaction.user.display_name} have deleted the chickens: \n\n" + "\n".join([f"{get_rarity_emoji(chicken['rarity'])} **{chicken['rarity']} {chicken['name']}**" for chicken in chickens_selected]) + f"\n\nYou have been refunded {refund_price} eggbux.")
        await interaction.followup.send(embed=embed)
        await on_awaitable(interaction.user.id)
        await asyncio.sleep(2.5)
        await interaction.message.delete()

    async def calculate_refund_price(self, chickens_selected: list) -> int:
        """
        Calculate the refund price of the chickens.

        Args:
            chickens_selected (list): The chickens selected.

        Returns:
            int
        """
        price_sum = sum([get_chicken_price(chicken, self.farm_data['farmer']) for chicken in chickens_selected])

        if self.farm_data['farmer'] == 'Guardian Farmer':
            return price_sum
        else:
            return price_sum//2