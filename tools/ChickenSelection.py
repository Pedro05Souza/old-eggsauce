import asyncio
from discord import SelectOption, ui
from db.userDB import User
from random import randint
from db.farmDB import Farm
from tools.chickenshared import *
from tools.shared import make_embed_object

class ChickenSelectView(ui.View):
    """View for selecting chickens from the market or farm to buy or delete them."""
    def __init__(self, chickens, author, action, message, chicken_emoji, *args, **kwargs):
        role = kwargs.get("role", None)
        t = kwargs.get("trade_data", None)
        instance_bot = kwargs.get("instance_bot", None)
        allowed_kw = ["role", "trade_data", "instance_bot"]
        kwargs = {k: kwargs[k] for k in kwargs if k not in allowed_kw}
        super().__init__(*args, **kwargs)
        if action == "M":
            menu = ChickenMarketMenu(chickens, author, message, chicken_emoji)
        elif action == "D":
            menu = ChickenDeleteMenu(chickens, author, message, chicken_emoji)
        elif action == "T":
            if role=="author":
                author = author[0]
                chickens = chickens[0]
                authorMessage = message[0]
                menu = ChickenAuthorTradeMenu(chickens, author, authorMessage, chicken_emoji, t)
            else:
                user = author[1]
                userMessage = message[1]
                chickens = chickens[1]
                menu = ChickenUserTradeMenu(chickens, user, userMessage, chicken_emoji, t, author[0], instance_bot)
        self.add_item(menu)

class ChickenMarketMenu(ui.Select):
    """Menu to buy chickens from the market"""
    def __init__(self, chickens, author_id, message, chicken_emoji):
        options = [
            SelectOption(label=f"{chicken['rarity']} {chicken['name']}", description=f"{chicken['rarity']} {get_chicken_price(chicken)}", value=str(index))
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
        price = get_chicken_price(chicken_selected)
        if price > User.read(interaction.user.id)['points']:
            await interaction.response.send_message("You don't have enough eggbux to buy this chicken.", ephemeral=True)
            self.options = [
                SelectOption(label=chicken['name'], description=f"{get_chicken_price(chicken)}", value=str(index))
                for index, chicken in enumerate(self.chickens)
            ]
            await interaction.message.edit(view=self.view)
            return
        if not Farm.read(interaction.user.id):
            await interaction.response.send_message("You don't have a farm yet. Create one to buy chickens by typing !createFarm.", ephemeral=True)
            return
        if len(Farm.read(interaction.user.id)['chickens']) == 8 and Farm.read(interaction.user.id)['farmer'] != 'Warrior Farmer':
            await interaction.response.send_message("You hit the maximum limit of chickens in the farm.", ephemeral=True)
            return
        elif len(Farm.read(interaction.user.id)['chickens']) == 11 and Farm.read(interaction.user.id)['farmer'] == 'Warrior Farmer':
            await interaction.response.send_message("You hit the maximum limit of chickens in the farm.", ephemeral=True)
            return
        farm_data = Farm.read(interaction.user.id)
        chicken_selected['happiness'] = randint(60, 100)
        chicken_selected['eggs_generated'] = 0
        chicken_selected['upkeep_multiplier'] = determine_chicken_upkeep(chicken_selected)
        farm_data['chickens'].append(chicken_selected)
        aux = chicken_selected.copy()
        aux['bought'] = True
        self.chickens[self.chickens.index(chicken_selected)] = aux
        Farm.update_chickens(interaction.user.id, farm_data['chickens'])
        User.update_points(interaction.user.id, User.read(interaction.user.id)["points"] - price)
        embed = await make_embed_object(description=f":white_check_mark: {interaction.user.display_name} have bought the chicken: **{chicken_selected['rarity']}** {chicken_selected['name']} Price: {get_chicken_price(chicken_selected)} :money_with_wings:")
        await interaction.response.send_message(embed=embed)
        available_chickens = [chicken for chicken in self.chickens if not chicken.get('bought', False)]
        if not available_chickens:
            await interaction.message.delete()
            return
        updated_view = ChickenSelectView(available_chickens, self.author_id, "M", self.message, self.chicken_emoji)
        updated_message = await make_embed_object(title=f":chicken: {interaction.user.display_name} here are the chickens you generated to buy: \n", description="\n".join([f" {self.chicken_emoji(chicken['rarity'])} **{index + 1}.** **{chicken['rarity']} {chicken['name']}**: {get_chicken_price(chicken)}" for index, chicken in enumerate(available_chickens)]))
        await interaction.message.edit(embed=updated_message, view=updated_view)
        self.message = updated_message
        return
   
class ChickenDeleteMenu(ui.Select):
    """Menu to delete chickens from the farm"""
    def __init__(self, chickens, author_id, message, chicken_emoji):
        options = [
            SelectOption(label=chicken['name'], description=f"{chicken['rarity']} {get_chicken_price(chicken)}", value=str(index))
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
        index = self.values[0]
        chicken_selected = self.chickens[int(index)]
        price = get_chicken_price(chicken_selected)
        farm_data = Farm.read(interaction.user.id)
        farm_data['chickens'].remove(chicken_selected)
        refund_price = 0
        if farm_data['farmer'] == 'Guardian Farmer':
            refund_price = price
        else:
            refund_price = price//2
        Farm.update_chickens(interaction.user.id, farm_data['chickens'])
        User.update_points(interaction.user.id, User.read(interaction.user.id)["points"] + (refund_price))
        embed = await make_embed_object(description=f":white_check_mark: {interaction.user.display_name} have deleted the chicken: **{chicken_selected['rarity']} {chicken_selected['name']}** Price: {refund_price} :money_with_wings:")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        deleted_chicken = chicken_selected.copy()
        deleted_chicken['Deleted'] = True
        self.chickens[self.chickens.index(chicken_selected)] = deleted_chicken
        available_chickens = [chicken for chicken in self.chickens if not chicken.get('Deleted', False)]
        updated_view = ChickenSelectView(available_chickens, self.author_id, "D", self.message, self.chicken_emoji)
        msg = await make_embed_object(
        title=f":chicken: {farm_data['farm_name']}\n:egg: **Eggs generated**: {farm_data['eggs_generated']}\n:farmer: Farmer: {farm_data['farmer'] if farm_data['farmer'] else 'No Farmer.'}",
        description="\n".join([
        f"{self.chicken_emoji(chicken['rarity'])}  **{index + 1}.** **{chicken['rarity']} {chicken['name']}** \n:partying_face: Happiness: **{chicken['happiness']}%**\nEggs generated: **{chicken['eggs_generated']}**\n"
        for index, chicken in enumerate(farm_data['chickens'])
        ]))
        msg.set_thumbnail(url=interaction.user.display_avatar)
        self.message = msg
        await interaction.message.edit(view=updated_view, embed=msg)
        return
    
class ChickenAuthorTradeMenu(ui.Select):
    def __init__(self, chickens, author, message, chicken_emoji, td):
        options = [
            SelectOption(label=chicken['name'], description=f"{chicken['rarity']} {get_chicken_price(chicken)}", value=str(index))
            for index, chicken in enumerate(chickens)
        ]
        self.chickens = chickens
        self.author = author
        self.message = message
        self.chicken_emoji = chicken_emoji
        self.td = td
        super().__init__(min_values=1, max_values=len(chickens), options=options)

    async def callback(self, interaction):
        if interaction.user.id != self.author.id:
            embed = await make_embed_object(description="You can't interact with this menu.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        selected_chickens = [self.chickens[int(value)] for value in self.values]
        self.td.author = {
            self.author.id: selected_chickens
        }
        embed = await make_embed_object(description=f":white_check_mark: {self.author.display_name} have selected the chickens to trade.")
        await interaction.response.send_message(embed=embed)
        
class ChickenUserTradeMenu(ui.Select):
    def __init__(self, chickens, author, message, chicken_emoji, td, target, instance_bot):
        options = [
            SelectOption(label=chicken['name'], description=f"{chicken['rarity']} {get_chicken_price(chicken)}", value=str(index))
            for index, chicken in enumerate(chickens)
        ]
        self.chickens = chickens
        self.author = author
        self.message = message
        self.chicken_emoji = chicken_emoji
        self.td = td
        self.target = target
        self.instance_bot = instance_bot
        super().__init__(min_values=1, max_values=len(chickens), options=options)

    async def callback(self, interaction):
        if interaction.user.id != self.author.id:
            embed = await make_embed_object(description="You can't interact with this menu.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        selected_chickens = [self.chickens[int(value)] for value in self.values]
        self.td.target = {
            self.author.id: selected_chickens
        }
        embed = await make_embed_object(description=f":white_check_mark: {self.author.display_name} have selected the chickens to trade.")
        await interaction.response.send_message(embed=embed)
        while True:
            await asyncio.sleep(3)
            if len(self.td.author) == 1 and len(self.td.target) == 1:
                break
        author_chickens = self.td.target[self.author.id]
        target_chickens = self.td.author[self.target.id]
        embed = await make_embed_object(description=f"{self.author.display_name} wants to trade the following chickens: " +
        "\n".join([f"{self.chicken_emoji(chicken['rarity'])} **{chicken['rarity']} {chicken['name']}**" for chicken in author_chickens]) +
        f"\n{self.target.display_name} wants to trade the following chickens: " +
        "\n".join([f"{self.chicken_emoji(chicken['rarity'])} **{chicken['rarity']} {chicken['name']}**" for chicken in target_chickens]))
        msg = await interaction.followup.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        users_reacted = set()
        while len(users_reacted) < 2:
            try:
                reaction, reactUsr = await self.instance_bot.wait_for("reaction_add", check=lambda reaction, user: user.id == self.author.id or user.id == self.target.id, timeout=40)
                if reaction.emoji == "✅":
                    users_reacted.add(reactUsr.id)
                elif reaction.emoji == "❌":
                    embed = await make_embed_object(description="Trade has been cancelled.")
                    await msg.edit(embed=embed)
                    TradeData.remove(self.td)
                    break
            except asyncio.TimeoutError:
                embed = await make_embed_object(description="Trade confirmation has timed out.")
                await msg.edit(embed=embed)
                TradeData.remove(self.td)
                break
        if len(users_reacted) == 2:
            msg = await trade_handler(interaction, self.td, self.target)
            await interaction.followup.send(embed=msg)
            TradeData.remove(self.td)
            return

async def trade_handler(ctx, td, target):
    if td.author is not None and td.target is not None:
        author_chickens = td.target[ctx.user.id]
        user_chickens = td.author[target.id]
        author_farm = Farm.read(ctx.user.id)
        user_farm = Farm.read(target.id)
        author_farm['chickens'] = [chicken for chicken in author_farm['chickens'] if chicken not in author_chickens]
        user_farm['chickens'] = [chicken for chicken in user_farm['chickens'] if chicken not in user_chickens]
        author_farm['chickens'].extend(user_chickens)
        user_farm['chickens'].extend(author_chickens)
        Farm.update_chickens(ctx.user.id, author_farm['chickens'])
        Farm.update_chickens(target.id, user_farm['chickens'])
        embed = await make_embed_object(description=f":white_check_mark: {ctx.user.display_name} and {target.display_name} have traded chickens.")
        return embed

     

