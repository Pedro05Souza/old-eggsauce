from discord import SelectOption, ui
from db.farmDB import Farm
from db.userDB import User
from tools.chickens.chickenhandlers import EventData
from tools.chickens.chickenshared import get_chicken_price, get_rarity_emoji
from tools.shared import confirmation_embed
from tools.shared import make_embed_object
import asyncio

class ChickenDeleteMenu(ui.Select):
    """Menu to delete chickens from the farm"""
    def __init__(self, chickens, author, message, s):
        options = [
            SelectOption(label=chicken['name'], description=f"{chicken['rarity']} {get_chicken_price(chicken)}", value=str(index), emoji=get_rarity_emoji(chicken['rarity']))
            for index, chicken in enumerate(chickens) if chicken['rarity'] != "DEAD" or chicken['rarity'] != "ETHEREAL"
        ]
        self.chickens = chickens
        self.author = author
        self.message = message
        self.delete_object = s
        super().__init__(min_values=1, max_values=len(chickens), options=options, placeholder="Select the chickens to delete:")

    async def callback(self, interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("You can't interact with this menu.", ephemeral=True)
            return
        farm_data = Farm.read(interaction.user.id)
        chickens_selected = [self.chickens[int(value)] for value in self.values]
        price = sum([get_chicken_price(chicken, farm_data['farmer']) for chicken in chickens_selected])
        for chicken in chickens_selected:
            farm_data['chickens'].remove(chicken)
        refund_price = 0
        if farm_data['farmer'] == 'Guardian Farmer':
            refund_price = price
        else:
            refund_price = price//2
        confirmation = await confirmation_embed(interaction, interaction.user, f"{interaction.user.display_name}, are you sure you want to delete the selected chickens for {refund_price} eggbux?")
        if confirmation:
            Farm.update(interaction.user.id, chickens=farm_data['chickens'])
            User.update_points(interaction.user.id, User.read(interaction.user.id)["points"] + (refund_price))
            embed = await make_embed_object(description=f":white_check_mark: {interaction.user.display_name} have deleted the chickens: \n\n" + "\n".join([f"{get_rarity_emoji(chicken['rarity'])} **{chicken['rarity']} {chicken['name']}**" for chicken in chickens_selected]) + f"\n\nYou have been refunded {refund_price} eggbux.")
            await interaction.followup.send(embed=embed)
            EventData.remove(self.delete_object)
            await asyncio.sleep(2.5)
            await interaction.message.delete()
            return
        else:
            embed = await make_embed_object(description=f":x: {interaction.user.display_name} have cancelled the deletion of the selected chickens.")
            await interaction.followup.send(embed=embed)
            EventData.remove(self.delete_object)
            await asyncio.sleep(2.5)
            await interaction.message.delete()