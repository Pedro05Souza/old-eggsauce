import asyncio
from discord import SelectOption, ui
from db.userDB import Usuario
import discord
from time import time
from random import randint
from db.farmDB import Farm
from tools.sharedEnums import ChickenUpkeep, ChickenMultiplier

class ChickenSelectView(ui.View):
    """View for selecting chickens from the market or farm to buy or delete them."""
    def __init__(self, chickens, author_id, action, message, chicken_emoji, *args, **kwargs):
        role = kwargs.get("role", None)
        kwargs = {k: kwargs[k] for k in kwargs if k != "role"}
        super().__init__(*args, **kwargs)
        if action == "M":
            menu = ChickenMarketMenu(chickens, author_id, message, chicken_emoji)
        elif action == "D":
            menu = ChickenDeleteMenu(chickens, author_id, message, chicken_emoji)
        elif action == "T":
            if role == "author":
                trader_id = author_id[0]
                trader_message = message[0]
                trader_chickens = chickens[0]
                menu = ChickenAuthorTradeMenu(trader_chickens, trader_id, trader_message, chicken_emoji)
            elif role == "user":
                user_message = message[1]
                user_chickens = chickens[1]
                user_id = author_id[1]
                menu = ChickenAuthorTradeMenu.ChickenUserTradeMenu(user_chickens, user_id, user_message, chicken_emoji)

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
            await interaction.response.send_message("You can't steal chickens from other players.", ephemeral=True)
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
        chicken_selected['Happiness'] = randint(60, 100)
        chicken_selected['Egg_value'] = ChickenMultiplier[chicken_selected['Name'].split(" ")[0]].value
        chicken_selected['Eggs_generated'] = 0
        chicken_selected['Upkeep_multiplier'] = ChickenUpkeep[chicken_selected['Name'].split(" ")[0]].value
        farm_data['chickens'].append(chicken_selected)
        Farm.update(interaction.user.id, farm_data['farm_name'], farm_data['chickens'], farm_data['eggs_generated'])
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
        print(arr)
        arr[0] = int(arr[0])
        farm_data = Farm.read(interaction.user.id)
        farm_data['chickens'].remove(chicken_selected)
        Farm.update(interaction.user.id, farm_data['farm_name'], farm_data['chickens'], farm_data['eggs_generated'])
        Usuario.update(interaction.user.id, Usuario.read(interaction.user.id)["points"] + (arr[0]//2), Usuario.read(interaction.user.id)["roles"])
        chicken_selected['Deleted'] = chicken_selected.get('Deleted', True)
        embed = discord.Embed(description=f":white_check_mark: {interaction.user.display_name} have deleted the chicken: {chicken_selected['Name']} Price: {arr[1]//2} :money_with_wings:")
        await interaction.response.send_message(embed=embed)
        available_chickens = [chicken for chicken in self.chickens if not chicken.get('Deleted', False)]
        updated_view = ChickenSelectView(available_chickens, self.author_id, "D", self.message, self.chicken_emoji)
        updated_message = discord.Embed(title=f":chicken: {farm_data['farm_name']}", description="\n".join([f"{self.chicken_emoji(chicken['Name'])} **{index + 1}.** {chicken['Name']}" for index, chicken in enumerate(farm_data['chickens']) if not chicken.get('Deleted', False)]))
        self.message = updated_message
        await interaction.message.edit(view=updated_view, embed=updated_message)
        return

tradeItems = {}   
class ChickenAuthorTradeMenu(ui.Select):
    """Menu to trade chickens with other players"""
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
        global tradeItems
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You can't steal chickens from other players's inventory.", ephemeral=True)
            return
        index = self.values[0]
        chicken_selected = self.chickens[int(index)]
        await interaction.response.send_message(f"{interaction.user.display_name} selected the chicken: {chicken_selected['Name']} to trade.")
        tradeItems[interaction.user.id] = chicken_selected

        
    class ChickenUserTradeMenu(ui.Select):
        """Menu of the user to accept or decline the trade"""
        global tradeItems
        def __init__(self, chickens, author_id, message, chicken_emoji):
            options = [
                SelectOption(label=chicken['Name'], description=f"{chicken['Price']} :money_with_wings:", value=str(index))
                for index, chicken in enumerate(chickens)
            ]
            self.author_id = author_id
            self.chickens = chickens
            self.message = message
            self.chicken_emoji = chicken_emoji
            super().__init__(min_values=1, max_values=1, options=options)

        async def callback(self, interaction):
            if interaction.user.id != self.author_id:
                await interaction.response.send_message("You can't steal chickens from other player's inventory.", ephemeral=True)
                return
            index = self.values[0]
            chicken_selected = self.chickens[int(index)]
            await interaction.response.send_message(f"{interaction.user.display_name} selected the chicken: {chicken_selected['Name']} to trade.")
            tradeItems[interaction.user.id] = chicken_selected
            await self.trade(interaction)

        async def trade(self, interaction):
            global tradeItems
            if len(tradeItems) != 2:
                return
            user1 = self.trade.keys()[0]
            user2 = self.trade.keys()[1]
            embed = discord.Embed(description=f"{user1.display_name} and {user2.display_name} have selected {self.trade[user1]['Name']} and {self.trade[user2]['Name']} to trade. React with ✅ to accept the trade or ❌ to decline it. Or ignore this message to add more chickens to the trade.")
            await interaction.followup.send(embed=embed)
            await interaction.followup.message.add_reaction("✅")
            await interaction.followup.message.add_reaction("❌")
            reaction, user = await interaction.followup.message.wait_for("reaction_add", check=lambda reaction, user: user.id == user1.id and user.id == user2.id, timeout=30)
            if reaction.emoji == "✅" and user:
                embed = discord.Embed(description=f":white_check_mark: {user1.display_name} and {user2.display_name} have accepted the trade. Please wait 5 seconds for the trade to be completed. You can still decline the trade by removing the reaction.")
                await interaction.followup.send(embed=embed)
                limitTime = time() + 5
                while True:
                    removedReaction, removedUser = await interaction.followup.message.wait_for("reaction_remove", check=lambda reaction, user: user.id == user1.id or user.id == user2.id)
                    if removedReaction.emoji == "✅" and removedUser:
                        embed = discord.Embed(description=f":no_entry_sign: {removedUser.display_name} has declined the trade.")
                        await interaction.followup.send(embed=embed)
                        break
                    if limitTime - time() <= 0:
                        farm1 = Farm.read(user1.id)
                        farm2 = Farm.read(user2.id)
                        farm1['chickens'].append(self.trade[user2])
                        farm2['chickens'].append(self.trade[user1])
                        farm1['chickens'].remove(self.trade[user1])
                        farm2['chickens'].remove(self.trade[user2])
                        Farm.update(user1.id, farm1['farm_name'], farm1['chickens'], farm1['eggs_generated'])
                        Farm.update(user2.id, farm2['farm_name'], farm2['chickens'], farm2['eggs_generated'])
                        embed = discord.Embed(description=f":white_check_mark: {user1.display_name} and {user2.display_name} have completed the trade.")
                        await interaction.followup.send(embed=embed)
                        tradeItems = {}
                        break
            else:
                embed = discord.Embed(description=f":no_entry_sign: {user1.display_name} and {user2.display_name} have declined the trade.")
                await interaction.followup.send(embed=embed)
        
    

     

