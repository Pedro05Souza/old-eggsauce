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
from db.farmDB import Farm
from db.userDB import User
from tools.shared import make_embed_object, send_bot_embed

class ChickenSelectView(ui.View):
    """View for selecting chickens from the market or farm to buy or delete them."""
    def __init__(self, chickens: list, author: Union[discord.Member, list], action:str, message: discord.Embed, *args, **kwargs):
        super().__init__(*args, **kwargs, timeout=60)
        menu = self.action_handler(chickens, author, action, message, *args, **kwargs)
        self.add_item(menu)

    def action_handler(self, chickens: list, author: Union[discord.Member, list], action: str, message: discord.Embed, *args, **kwargs) -> ui.View:
        """Method to handle the action of the view."""
        role = kwargs.get("role", None)
        t = kwargs.get("trade_data", None)
        instance_bot = kwargs.get("instance_bot", None)
        allowed_kw = ["role", "trade_data", "instance_bot", "offer_id"]
        kwargs = {k: kwargs[k] for k in kwargs if k not in allowed_kw}
        menu = None
        if action == "M":
            self.timeout = 120
            menu = ChickenMarketMenu(chickens, author, message)
        elif action == "D":
            self.timeout = 30
            s = EventData(author)
            menu = ChickenDeleteMenu(chickens, author, message, s)
        elif action == "T":
            if role=="author":
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
            self.timeout = 120
            menu = PlayerMarketMenu(chickens, message, author, instance_bot)
        elif action == "R":
            self.timeout = 120
            menu = RedeemPlayerMenu(chickens, author, message)
        return menu

    
    async def on_timeout(self) -> None:
        """Method to execute when the view times out."""
        if self.children[0].__class__.__name__ == "ChickenDeleteMenu":
            if hasattr(self.children[0], "delete_object"):
                EventData.remove(self.children[0].delete_object)
        if self.children[0].__class__.__name__ == "ChickenUserTradeMenu":
            EventData.remove(self.children[0].td)
        return

class ChickenMarketMenu(ui.Select):
    """Menu to buy chickens from the market"""
    def __init__(self, chickens: list, author_id: int, message: discord.Embed):
        self.chickens = chickens
        self.author_id = author_id
        self.message = message
        farm_data = Farm.read(author_id)
        options = [
            SelectOption(label=f"{chicken['rarity']} {chicken['name']}", description=f"Price: {get_chicken_price(chicken, farm_data['farmer'])}", value=str(index), emoji=get_rarity_emoji(chicken['rarity']))
            for index, chicken in enumerate(chickens)
        ]
        super().__init__(min_values=1, max_values=1, options=options, placeholder="Select the chicken to buy:")

    async def callback(self, interaction: discord.Interaction) -> None:
        """Callback for the chicken market menu"""
        if interaction.user.id != self.author_id:
            return await send_bot_embed(interaction, description=":no_entry_sign: You can't buy chickens for another user.", ephemeral=True)
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
        if len(farm_data['chickens']) == get_max_chicken_limit(farm_data):
            await send_bot_embed(interaction, description=":no_entry_sign: You hit the maximum limit of chickens in the farm.", ephemeral=True)
            self.options = [
                SelectOption(label=f"{chicken['rarity']} {chicken['name']}", description=f"{chicken['rarity']} {get_chicken_price(chicken, farm_data['farmer'])}", value=str(index), emoji=get_rarity_emoji(chicken['rarity']))
                for index, chicken in enumerate(self.chickens)
            ]
            await interaction.message.edit(view=self.view)
            return
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
        if not available_chickens:
            await interaction.message.delete()
            return
        updated_view = ChickenSelectView(available_chickens, self.author_id, "M", self.message)
        updated_message = await make_embed_object(title=f":chicken: {interaction.user.display_name} here are the chickens you generated to buy: \n", description="\n".join([f" {get_rarity_emoji(chicken['rarity'])} **{index + 1}.** **{chicken['rarity']} {chicken['name']}**: {get_chicken_price(chicken)} eggbux." for index, chicken in enumerate(available_chickens)]))
        await interaction.message.edit(embed=updated_message, view=updated_view)
        self.message = updated_message
        return