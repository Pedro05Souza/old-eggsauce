from lib.chickenlib import get_chicken_price, get_rarity_emoji, get_max_chicken_limit, get_max_bench_limit, create_chicken, check_if_author
from lib.shared import user_cache_retriever
from views.selection.deleteselection import ChickenDeleteMenu
from views.selection.playermarketselection import PlayerMarketMenu
from views.selection.redeemselection import RedeemPlayerMenu
from views.selection.tradeselection import ChickenAuthorTradeMenu, ChickenUserTradeMenu
from tools import on_user_transaction, on_awaitable
from typing import Union
from discord import SelectOption, ui
from db import Farm, User
from lib.shared import make_embed_object, send_bot_embed
import discord

__all__ = ["ChickenSelectView"]

class ChickenSelectView(ui.View):

    def __init__(
            self, 
            chickens: list, 
            author: Union[discord.Member, list], 
            action: str, 
            message: discord.Embed, 
            farm_data: dict = None, 
            role: str = None,
            instance_bot: discord.Client = None,
            shared_trade_dict: dict = None,
            *args, 
            **kwargs
        ):
        self.author = author
        menu, timeout = self.action_handler(chickens, author, action, message, farm_data, role, instance_bot, shared_trade_dict)
        super().__init__(*args, **kwargs, timeout=timeout)
        self.add_item(menu)

    def action_handler(
            self, 
            chickens: list, 
            author: Union[discord.Member, list], 
            action: str, 
            message: discord.Embed, 
            farm_data: dict, 
            role: str = None, 
            instance_bot: discord.Client = None,
            shared_trade_dict: dict = None
            ) -> ui.View:
        """
        Handles the action to be taken for the menu.

        Args:
            chickens (list): The list of chickens to display.
            author (Union[discord.Member, list]): The author of the message.
            action (str): The action to take.
            message (discord.Embed): The message to display.
            *args: The arguments.
            **kwargs: The keyword arguments.

        Returns:
            ui.View
        """
        timeout = 60
        menu = None

        if action == "M":
            timeout = 120
            menu = ChickenMarketMenu(chickens, author, message, farm_data)

        elif action == "D":
            timeout = 30
            menu = ChickenDeleteMenu(chickens, author, message)

        elif action == "T":

            if role == "author":
                author = author[0]
                chickens = chickens[0]
                authorMessage = message[0]
                menu = ChickenAuthorTradeMenu(chickens, author, authorMessage, shared_trade_dict)

            else:
                user = author[1]
                userMessage = message[1]
                chickens = chickens[1]
                menu = ChickenUserTradeMenu(chickens, user, userMessage, author[0], instance_bot, shared_trade_dict)

        elif action == "PM":
            timeout = 120
            menu = PlayerMarketMenu(chickens, message, author, instance_bot)

        elif action == "R":
            timeout = 120
            menu = RedeemPlayerMenu(chickens, author, message)

        return menu, timeout

    async def on_timeout(self) -> None:
        """
        Execute when the view times out.

        Returns:
            None
        """
        if type(self.author) == list:
            author = self.author[0]
            user = self.author[1]
            await on_awaitable(author, user)
        else:
            author = self.author
            await on_awaitable(author)

class ChickenMarketMenu(ui.Select):
    
    def __init__(self, chickens: list, author_id: int, message: discord.Embed, farm_data: dict):
        self.chickens = chickens
        self.author_id = author_id
        self.message = message
        self.farm_data = farm_data
        super().__init__(min_values=1, max_values=1, options=self.initiaize_options(), placeholder="Select the chicken to buy:")

    def initiaize_options(self) -> list:
        """
        Initializes the options for the select menu.

        Returns:
            list

        """
        options = [
            SelectOption(
                label=f"{chicken['rarity']} {chicken['name']}", 
                description=f"Price: {get_chicken_price(chicken, self.farm_data['farmer'])}", 
                value=str(index), 
                emoji=get_rarity_emoji(chicken['rarity'])
            )
            for index, chicken in enumerate(self.chickens)
        ]
        return options

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Responsable for buying chickens from the regular market command.

        Args:
            interaction (discord.Interaction): The interaction object.

        Returns:
            None
        """
        if not await check_if_author(self.author_id, interaction.user.id, interaction):
            return
        
        index = self.values[0]
        chicken_selected = self.chickens[int(index)]
        data = await user_cache_retriever(interaction.user.id)
        farm_data = data["farm_data"]
        user_data = data["user_data"]
        price = get_chicken_price(chicken_selected, farm_data['farmer'])

        if price > user_data['points']:
            await send_bot_embed(interaction, ephemeral=True, description=f":no_entry_sign: You don't have enough eggbux to buy this chicken.")
            self.options = [
                SelectOption(label=f"{chicken['rarity']} {chicken['name']}", description=f"{chicken['rarity']} {get_chicken_price(chicken, farm_data['farmer'])}", value=str(index), emoji=get_rarity_emoji(chicken['rarity']))
                for index, chicken in enumerate(self.chickens)
            ]
            await interaction.message.edit(view=self.view)
            return
        
        if len(farm_data['chickens']) == get_max_chicken_limit(farm_data) and len(farm_data['bench']) == await get_max_bench_limit():
            await send_bot_embed(interaction, description=":no_entry_sign: You hit the maximum limit of chickens in the farm and the farm.", ephemeral=True)
            self.options = [
                SelectOption(label=f"{chicken['rarity']} {chicken['name']}", description=f"{chicken['rarity']} {get_chicken_price(chicken, farm_data['farmer'])}", value=str(index), emoji=get_rarity_emoji(chicken['rarity']))
                for index, chicken in enumerate(self.chickens)
            ]
            await interaction.message.edit(view=self.view)
            return
        
        available_chickens = await self.handle_chicken_purchase(interaction, chicken_selected, farm_data, user_data, price)

        if not available_chickens:
            await interaction.message.delete()
            return
        
        updated_view = ChickenSelectView(available_chickens, self.author_id, "M", self.message, farm_data=farm_data)
        updated_message = await make_embed_object(title=f":chicken: {interaction.user.display_name} here are the chickens you generated to buy: \n", description="\n".join([f" {get_rarity_emoji(chicken['rarity'])} **{index + 1}.** **{chicken['rarity']} {chicken['name']}**: {get_chicken_price(chicken)} eggbux." for index, chicken in enumerate(available_chickens)]))
        await interaction.message.edit(embed=updated_message, view=updated_view)
        self.message = updated_message
        return
    
    async def handle_chicken_purchase(self, interaction: discord.Interaction, chicken_selected: dict, farm_data: dict, user_data: dict, price: int) -> dict:
        """
        Handles the purchase of a chicken.

        Args:
            interaction (discord.Interaction): The interaction object.
            chicken_selected (dict): The selected chicken.
            farm_data (dict): The farm data.
            user_data (dict): The user data.

        Returns:
            dict
        """
        aux = chicken_selected.copy()
        self.chickens[self.chickens.index(chicken_selected)] = aux
        chicken_selected = await create_chicken(chicken_selected['rarity'], "market")

        if len(farm_data['chickens']) < get_max_chicken_limit(farm_data):
            farm_data['chickens'].append(chicken_selected)
        else:
            farm_data['bench'].append(chicken_selected)

        aux['bought'] = True
        await Farm.update(interaction.user.id, chickens=farm_data['chickens'], bench=farm_data['bench'])
        await User.update_points(interaction.user.id, user_data["points"] - price)
        await on_user_transaction(interaction, price, 1)
        embed = await make_embed_object(description=f":white_check_mark: {interaction.user.display_name} has bought the chicken: **{get_rarity_emoji(chicken_selected['rarity'])} {chicken_selected['rarity']} {chicken_selected['name']}**, costing {price} eggbux :money_with_wings:")
        await interaction.response.send_message(embed=embed)
        available_chickens = [chicken for chicken in self.chickens if not chicken.get('bought', False)]
        return available_chickens