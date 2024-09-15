from tools.chickens.chickenshared import *
from tools.chickens.chickenhandlers import EventData
from tools.shared import user_cache_retriever
from tools.chickens.selection.deleteselection import ChickenDeleteMenu
from tools.chickens.selection.redeemselection import RedeemPlayerMenu
from tools.chickens.selection.tradeselection import ChickenAuthorTradeMenu, ChickenUserTradeMenu
from tools.chickens.selection.playermarketselection import PlayerMarketMenu
from tools.listeners import on_user_transaction
from typing import Union
from discord import SelectOption, ui
from db.farmdb import Farm
from db.userdb import User
from tools.shared import make_embed_object, send_bot_embed

class ChickenSelectView(ui.View):

    def __init__(self, chickens: list, author: Union[discord.Member, list], action:str, message: discord.Embed, *args, **kwargs):
        menu, timeout = self.action_handler(chickens, author, action, message, *args, **kwargs)
        kwargs = {k: kwargs[k] for k in kwargs if k not in ["role", "trade_data", "instance_bot", "offer_id"]}
        super().__init__(*args, **kwargs, timeout=timeout)
        self.add_item(menu)

    def action_handler(self, chickens: list, author: Union[discord.Member, list], action: str, message: discord.Embed, **kwargs) -> ui.View:
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
        if kwargs:
            role = kwargs.get("role", None)
            t = kwargs.get("trade_data", None)
            instance_bot = kwargs.get("instance_bot", None)
        menu = None
        if action == "M":
            timeout = 120
            menu = ChickenMarketMenu(chickens, author, message)
        elif action == "D":
            timeout = 30
            s = EventData(author)
            menu = ChickenDeleteMenu(chickens, author, message, s)
        elif action == "T":
            if role == "author":
                author = author[0]
                chickens = chickens[0]
                authorMessage = message[0]
                menu = ChickenAuthorTradeMenu(chickens, author, authorMessage, t)
            else:
                user = author[1]
                userMessage = message[1]
                chickens = chickens[1]
                menu = ChickenUserTradeMenu(chickens, user, userMessage, t, author[0], instance_bot)
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
        if self.children[0].__class__.__name__ == "ChickenDeleteMenu":
            if hasattr(self.children[0], "delete_object"):
                EventData.remove(self.children[0].delete_object)
        if self.children[0].__class__.__name__ == "ChickenUserTradeMenu":
            EventData.remove(self.children[0].td)
        return

class ChickenMarketMenu(ui.Select):
    
    def __init__(self, chickens: list, author_id: int, message: discord.Embed):
        self.chickens = chickens
        self.author_id = author_id
        self.message = message
        farm_data = Farm.read(author_id)
        options = [
            SelectOption(
                label=f"{chicken['rarity']} {chicken['name']}", 
                description=f"Price: {get_chicken_price(chicken, farm_data['farmer'])}", 
                value=str(index), 
                emoji=get_rarity_emoji(chicken['rarity'])
            )
            for index, chicken in enumerate(chickens)
        ]
        super().__init__(min_values=1, max_values=1, options=options, placeholder="Select the chicken to buy:")

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
        
        if not farm_data:
            await send_bot_embed(interaction, description=":no_entry_sign: You don't have a farm. Type !createfarm to start.", ephemeral=True)
            return
        
        if len(farm_data['chickens']) == get_max_chicken_limit(farm_data) and len(farm_data['bench']) == await get_max_bench_limit():
            await send_bot_embed(interaction, description=":no_entry_sign: You hit the maximum limit of chickens in the farm.", ephemeral=True)
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
        
        updated_view = ChickenSelectView(available_chickens, self.author_id, "M", self.message)
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
        farm_data['chickens'].append(chicken_selected)
        aux['bought'] = True
        Farm.update(interaction.user.id, chickens=farm_data['chickens'])
        User.update_points(interaction.user.id, user_data["points"] - price)
        await on_user_transaction(interaction, price, 1)
        embed = await make_embed_object(description=f":white_check_mark: {interaction.user.display_name} have bought the chicken: **{get_rarity_emoji(chicken_selected['rarity'])} {chicken_selected['rarity']} {chicken_selected['name']}**, costing {price} eggbux :money_with_wings:")
        await interaction.response.send_message(embed=embed)
        available_chickens = [chicken for chicken in self.chickens if not chicken.get('bought', False)]
        return available_chickens