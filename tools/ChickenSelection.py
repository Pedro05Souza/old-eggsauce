from discord import SelectOption, ui
from db.userDB import Usuario
import discord
from db.farmDB import Farm

class ChickenSelectView(ui.View):
    """View for selecting chickens from the market or farm to buy or delete them."""
    def __init__(self, chickens, author_id, action, message, chicken_emoji, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if action == "M":
            menu = ChickenMarketMenu(chickens, author_id, message, chicken_emoji)
        elif action == "D":
            menu = ChickenDeleteMenu(chickens, author_id, message, chicken_emoji)
        self.add_item(menu)

class ChickenMarketMenu(ui.Select):
    """Menu to buy chickens from the market"""
    def __init__(self, chickens, author_id, message, chicken_emoji):
        options = [
            SelectOption(label=chicken['Name'], description=f"{chicken['Price']} :money_with_wings:", value=str(index))
            for index, chicken in enumerate(chickens)
        ]
        self.chickens = chickens
        self.author_id = author_id
        self.message = message
        self.chicken_emoji = chicken_emoji
        super().__init__(min_values=1, max_values=1, options=options)

    async def callback(self, interaction):
        """Callback for the chicken market menu"""
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You can't interact with this menu.", ephemeral=True)
            return
        index = self.values[0]
        chicken_selected = self.chickens[int(index)]
        arr = chicken_selected['Price'].split(" ")
        arr[1] = int(arr[1])
        if arr[1] > Usuario.read(interaction.user.id)['points']:
            await interaction.response.send_message("You don't have enough eggbux to buy this chicken.", ephemeral=True)
            return
        if not Farm.read(interaction.user.id):
            await interaction.response.send_message("You don't have a farm yet. Create one to buy chickens by typing !createFarm.", ephemeral=True)
            return
        if len(Farm.read(interaction.user.id)['chickens']) == 10:
            await interaction.response.send_message("You hit the maximum limit of chickens in the farm.", ephemeral=True)
            return
        if chicken_selected['Bought']:
            await interaction.response.send_message("This chicken has already been bought.", ephemeral=True)
            return
        farm_data = Farm.read(interaction.user.id)
        farm_data['chickens'].append(chicken_selected)
        Farm.update(interaction.user.id, farm_data['farm_name'], farm_data['chickens'], farm_data['eggs'], farm_data['eggs_generated'])
        Usuario.update(interaction.user.id, Usuario.read(interaction.user.id)["points"] - int(arr[1]), Usuario.read(interaction.user.id)["roles"])
        chicken_selected['Bought'] = True
        embed = discord.Embed(description=f":white_check_mark: {interaction.user.display_name} have bought the chicken: {chicken_selected['Name']} Price: {chicken_selected['Price']} :money_with_wings:")
        await interaction.response.send_message(embed=embed)
        available_chickens = [chicken for chicken in self.chickens if not chicken.get('Bought', False)]
        updated_view = ChickenSelectView(available_chickens, self.author_id, "M", self.message, self.chicken_emoji)
        updated_message = discord.Embed(title=f":chicken: {interaction.user.display_name} here are the chickens you generated to buy: \n", description="\n".join([f" {self.chicken_emoji(chicken['Name'])} **{index + 1}.** **{chicken['Name']}**: {chicken['Price']} :money_with_wings:" for index, chicken in enumerate(available_chickens)]))
        await interaction.message.edit(view=updated_view, embed=updated_message)
        self.message = updated_message
        return

        
class ChickenDeleteMenu(ui.Select):
    """Menu to delete chickens from the farm"""
    def __init__(self, chickens, author_id, message, chicken_emoji):
        options = [
            SelectOption(label=chicken['Name'], description=f"{chicken['Price']} :money_with_wings:", value=str(index))
            for index, chicken in enumerate(chickens)
        ]
        self.chickens = chickens
        self.author_id = author_id
        self.message = message
        self.chicken_emoji = chicken_emoji
        super().__init__(min_values=1, max_values=1, options=options)

    async def callback(self, interaction):
        chicken_selected = self.chickens[int(self.values[0])]
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You can't interact with this menu.", ephemeral=True)
            return
        if 'Deleted' in chicken_selected.keys():
            await interaction.response.send_message("This chicken has already been deleted.", ephemeral=True)
            return
        index = self.values[0]
        chicken_selected = self.chickens[int(index)]
        arr = chicken_selected['Price'].split(" ")
        arr[1] = int(arr[1])
        farm_data = Farm.read(interaction.user.id)
        farm_data['chickens'].remove(chicken_selected)
        Farm.update(interaction.user.id, farm_data['farm_name'], farm_data['chickens'], farm_data['eggs'], farm_data['eggs_generated'])
        Usuario.update(interaction.user.id, Usuario.read(interaction.user.id)["points"] + (arr[1]//2), Usuario.read(interaction.user.id)["roles"])
        chicken_selected['Deleted'] = chicken_selected.get('Deleted', True)
        embed = discord.Embed(description=f":white_check_mark: {interaction.user.display_name} have deleted the chicken: {chicken_selected['Name']} Price: {arr[1]//2} :money_with_wings:")
        await interaction.response.send_message(embed=embed)
        available_chickens = [chicken for chicken in self.chickens if not chicken.get('Deleted', False)]
        updated_view = ChickenSelectView(available_chickens, self.author_id, "D", self.message, self.chicken_emoji)
        updated_message = discord.Embed(title=f":chicken: {farm_data['farm_name']}", description="\n".join([f"{self.chicken_emoji(chicken['Name'])} **{index + 1}.** {chicken['Name']}" for index, chicken in enumerate(farm_data['chickens']) if not chicken.get('Deleted', False)]))
        self.message = updated_message
        await interaction.message.edit(view=updated_view, embed=updated_message)
        return


        

