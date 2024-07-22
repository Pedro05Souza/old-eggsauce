from tools.chickens.chickenshared import *
from tools.chickens.chickenhandlers import EventData
from tools.chickens.selection.deleteselection import ChickenDeleteMenu
from tools.chickens.selection.tradeselection import ChickenAuthorTradeMenu, ChickenUserTradeMenu
from tools.chickens.selection.playermarketselection import PlayerMarketMenu
from random import randint
from discord import SelectOption, ui
from db.farmDB import Farm
from db.userDB import User
from tools.shared import make_embed_object

class ChickenSelectView(ui.View):
    """View for selecting chickens from the market or farm to buy or delete them."""
    def __init__(self, chickens, author, action, message, *args, **kwargs):
        role = kwargs.get("role", None)
        t = kwargs.get("trade_data", None)
        instance_bot = kwargs.get("instance_bot", None)
        allowed_kw = ["role", "trade_data", "instance_bot", "offer_id"]
        kwargs = {k: kwargs[k] for k in kwargs if k not in allowed_kw}
        super().__init__(*args, **kwargs, timeout=60)
        if action == "M":
            self.timeout = 120
            menu = ChickenMarketMenu(chickens, author, message)
        elif action == "D":
            self.timeout = 30
            s = EventData(author=author)
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
        self.add_item(menu)
    
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
    def __init__(self, chickens, author_id, message):
        self.chickens = chickens
        self.author_id = author_id
        self.message = message
        farm_data = Farm.read(author_id)
        options = [
            SelectOption(label=f"{chicken['rarity']} {chicken['name']}", description=f"Price: {get_chicken_price(chicken, farm_data['farmer'])}", value=str(index), emoji=get_rarity_emoji(chicken['rarity']))
            for index, chicken in enumerate(chickens)
        ]
        super().__init__(min_values=1, max_values=1, options=options, placeholder="Select the chicken to buy:")

    async def callback(self, interaction):
        """Callback for the chicken market menu"""
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You can't steal chickens from other players.", ephemeral=True)
            return
        index = self.values[0]
        chicken_selected = self.chickens[int(index)]
        farm_data = Farm.read(interaction.user.id)
        user_data = User.read(interaction.user.id)
        price = get_chicken_price(chicken_selected, farm_data['farmer'])
        if price > user_data['points']:
            await interaction.response.send_message("You don't have enough eggbux to buy this chicken.", ephemeral=True)
            self.options = [
                SelectOption(label=f"{chicken['rarity']} {chicken['name']}", description=f"{chicken['rarity']} {get_chicken_price(chicken, farm_data['farmer'])}", value=str(index), emoji=get_rarity_emoji(chicken['rarity']))
                for index, chicken in enumerate(self.chickens)
            ]
            await interaction.message.edit(view=self.view)
            return
        if not farm_data:
            await interaction.response.send_message("You don't have a farm yet. Create one to buy chickens by typing !createFarm.", ephemeral=True)
            return
        if len(farm_data['chickens']) == get_max_chicken_limit(farm_data):
            await interaction.response.send_message("You hit the maximum limit of chickens in the farm.", ephemeral=True)
            self.options = [
                SelectOption(label=f"{chicken['rarity']} {chicken['name']}", description=f"{chicken['rarity']} {get_chicken_price(chicken, farm_data['farmer'])}", value=str(index), emoji=self.chicken_emoji(chicken['rarity']))
                for index, chicken in enumerate(self.chickens)
            ]
            await interaction.message.edit(view=self.view)
            return
        chicken_selected['happiness'] = randint(60, 100)
        chicken_selected['eggs_generated'] = 0
        chicken_selected['upkeep_multiplier'] = determine_chicken_upkeep(chicken_selected)
        farm_data['chickens'].append(chicken_selected)
        aux = chicken_selected.copy()
        aux['bought'] = True
        self.chickens[self.chickens.index(chicken_selected)] = aux
        Farm.update(interaction.user.id, chickens=farm_data['chickens'])
        User.update_points(interaction.user.id, user_data["points"] - price)
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