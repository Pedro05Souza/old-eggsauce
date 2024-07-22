from discord import SelectOption, ui
from db.farmDB import Farm
from tools.chickens.chickenhandlers import EventData
from tools.chickens.chickenshared import get_chicken_price, get_max_chicken_limit, get_rarity_emoji
from tools.shared import make_embed_object
import asyncio


class ChickenAuthorTradeMenu(ui.Select):
    def __init__(self, chickens, author, message, td):
        options = [
            SelectOption(label=chicken['name'], description=f"{chicken['rarity']} {get_chicken_price(chicken)}", value=str(index), emoji=get_rarity_emoji(chicken['rarity']))
            for index, chicken in enumerate(chickens)
        ]
        self.chickens = chickens
        self.author = author
        self.message = message
        self.td = td
        super().__init__(min_values=1, max_values=len(chickens), options=options, placeholder=f"{author.display_name}, select the chickens to trade:")

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
    def __init__(self, chickens, author, message, td, target, instance_bot):
        options = [
            SelectOption(label=chicken['name'], description=f"{chicken['rarity']} {get_chicken_price(chicken)}", value=str(index), emoji=get_rarity_emoji(chicken['rarity']))
            for index, chicken in enumerate(chickens)
        ]
        self.chickens = chickens
        self.author = author
        self.message = message
        self.td = td
        self.target = target
        self.instance_bot = instance_bot
        super().__init__(min_values=1, max_values=len(chickens), options=options, placeholder=f"{author.display_name}, select the chickens to trade:")

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
        "\n".join([f"{get_rarity_emoji(chicken['rarity'])} **{chicken['rarity']} {chicken['name']}**" for chicken in author_chickens]) +
        f"\n{self.target.display_name} wants to trade the following chickens: " +
        "\n".join([f"{get_rarity_emoji(chicken['rarity'])} **{chicken['rarity']} {chicken['name']}**" for chicken in target_chickens]))
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
                    EventData.remove(self.td)
                    break
            except asyncio.TimeoutError:
                embed = await make_embed_object(description="Trade confirmation has timed out.")
                await msg.edit(embed=embed)
                EventData.remove(self.td)
                break
        if len(users_reacted) == 2:
            msg = await trade_handler(interaction, self.td, self.target)
            await interaction.followup.send(embed=msg)
            EventData.remove(self.td)
            return

async def trade_handler(ctx, td, target):
    if td.author is not None and td.target is not None:
        author_chickens = td.target[ctx.user.id]
        user_chickens = td.author[target.id]
        author_farm = Farm.read(ctx.user.id)
        user_farm = Farm.read(target.id)
        if len(author_chickens) + len(user_chickens) > get_max_chicken_limit(author_farm) or len(user_chickens) + len(author_chickens) > get_max_chicken_limit(user_farm):
            embed = await make_embed_object(description="Trade cannot be completed. The total number of chickens after the trade exceeds the maximum limit.")
            return embed
        author_farm['chickens'] = [chicken for chicken in author_farm['chickens'] if chicken not in author_chickens]
        user_farm['chickens'] = [chicken for chicken in user_farm['chickens'] if chicken not in user_chickens]
        author_farm['chickens'].extend(user_chickens)
        user_farm['chickens'].extend(author_chickens)
        Farm.update(ctx.user.id, chickens=author_farm['chickens'])
        Farm.update(target.id, chickens=user_farm['chickens'])
        embed = await make_embed_object(description=f":white_check_mark: {ctx.user.display_name} and {target.display_name} have traded chickens.")
        return embed