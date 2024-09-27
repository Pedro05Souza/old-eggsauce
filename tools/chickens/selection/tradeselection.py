from discord import SelectOption, ui
from db.farmdb import Farm
from tools.chickens.chickenshared import get_chicken_price, get_max_chicken_limit, get_rarity_emoji, check_if_author
from tools.shared import make_embed_object, send_bot_embed, user_cache_retriever
import asyncio
import discord


class ChickenAuthorTradeMenu(ui.Select):

    def __init__(self, chickens: list, author: discord.Member, message: discord.Embed, shared_trade_dict: dict):
        options = [
            SelectOption(label=chicken['name'], description=f"{chicken['rarity']} {get_chicken_price(chicken)}", value=str(index), emoji=get_rarity_emoji(chicken['rarity']))
            for index, chicken in enumerate(chickens)
        ]
        self.chickens = chickens
        self.author = author
        self.message = message
        self.shared_trade_dict = shared_trade_dict
        super().__init__(min_values=1, max_values=len(chickens), options=options, placeholder=f"{author.display_name}, select the chickens to trade:")

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Responsable for selecting the chickens to trade.

        Args:
            interaction (discord.Interaction): The interaction object.

        Returns:
            None
        """
        if not await check_if_author(self.author.id, interaction.user.id, interaction):
            return
        
        selected_chickens = [self.chickens[int(value)] for value in self.values]
        self.shared_trade_dict = {
            self.author.id: selected_chickens
        }
        embed = await make_embed_object(description=f":white_check_mark: {self.author.display_name} have selected the chickens to trade.")
        await interaction.response.send_message(embed=embed)
        
class ChickenUserTradeMenu(ui.Select):

    def __init__(self, chickens: list, author: discord.Member, message: discord.Member, target: discord.Member, instance_bot: discord.Client, shared_trade_dict: dict):
        options = [
            SelectOption(
                label=chicken['name'], 
                description=f"{chicken['rarity']} {get_chicken_price(chicken)}", 
                value=str(index), 
                emoji=get_rarity_emoji(chicken['rarity'])
                )
            for index, chicken in enumerate(chickens) if chicken['rarity'] != "ETHEREAL"
        ]
        self.chickens = chickens
        self.author = author
        self.message = message
        self.shared_trade_dict = shared_trade_dict
        self.target = target
        self.instance_bot = instance_bot
        super().__init__(min_values=1, max_values=len(chickens), options=options, placeholder=f"{author.display_name}, select the chickens to trade:")

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Responsable for selecting the chickens to trade.

        Args:
            interaction (discord.Interaction): The interaction object.

        Returns:
            None
        """
        if not await check_if_author(self.author.id, interaction.user.id, interaction):
            return
        
        selected_chickens = [self.chickens[int(value)] for value in self.values]
        self.shared_trade_dict = {self.author.id: selected_chickens}
        embed = await make_embed_object(description=f":white_check_mark: {self.author.display_name} have selected the chickens to trade.")
        await interaction.response.send_message(embed=embed)
        await self.wait_for_trade_confirmation(interaction)
        
    async def wait_for_trade_confirmation(self, interaction: discord.Interaction) -> None:
        author_description = None
        target_description = None

        while len(self.shared_trade_dict) < 2:
            await asyncio.sleep(2.5)

            if self.author.id in self.shared_trade_dict:
                author_chickens = self.shared_trade_dict[self.author.id]
                author_chickens = f"{self.author.display_name} wants to trade the following chickens: " + "\n".join([f"{get_rarity_emoji(chicken['rarity'])} **{chicken['rarity']} {chicken['name']}**" for chicken in author_chickens])
            
            if self.target.id in self.shared_trade_dict:
                target_chickens = self.shared_trade_dict[self.target.id]
                target_description = f"\n{self.target.display_name} wants to trade the following chickens: " + "\n".join([f"{get_rarity_emoji(chicken['rarity'])} **{chicken['rarity']} {chicken['name']}**" for chicken in target_chickens])
            embed = await make_embed_object(description="")

            if author_description:
                embed.description += author_description

            if target_description:
                embed.description += target_description

        if embed.description != "":
            msg = await interaction.followup.send(embed=embed)
            await self.reaction_handler(interaction, msg)

    async def reaction_handler(self, interaction: discord.Interaction, msg: discord.Message) -> None:
        users_reacted = set()
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")  
        try:
            while len(users_reacted) < 2:
                reaction, reactUsr = await self.instance_bot.wait_for(
                    "reaction_add",
                    check=lambda _, user: user.id in {self.author.id, self.target.id},
                    timeout=40
                )
                if reaction.emoji == "✅":
                    users_reacted.add(reactUsr.id)
                elif reaction.emoji == "❌":
                    await send_bot_embed(interaction, description="Trade has been cancelled.")
                    await self.delete_shared_dict(self.author)
                    return
        except asyncio.TimeoutError:
            await send_bot_embed(interaction, description="Trade confirmation has timed out.")
            await self.delete_shared_dict(self.author)
            return 
            
        if len(users_reacted) == 2:
            msg = await self.trade_handler(interaction)
            await interaction.followup.send(embed=msg)
            await self.delete_shared_dict(self.author)
            return
        
    async def delete_shared_dict(self, author):
        self.shared_trade_dict.pop(author.id)
        self.shared_trade_dict.pop(self.target.id)

    async def trade_handler(self, ctx) -> discord.Embed:
        """
        Handles the trade between two users.

        Args:
            ctx (discord.Interaction): The interaction object.
            td (EventData): The EventData object.
            target (discord.Member): The target user.

        Returns:
            discord.Embed: The embed object.
        """
        author_chickens = self.shared_trade_dict[self.target.id]
        user_chickens = self.shared_trade_dict[ctx.user.id]
        author_cache = await user_cache_retriever(ctx.user.id)
        user_cache = await user_cache_retriever(self.target.id)
        author_farm = author_cache["farm_data"]
        user_farm = user_cache["farm_data"]

        if len(author_chickens) + len(user_chickens) > get_max_chicken_limit(author_farm) or len(user_chickens) + len(author_chickens) > get_max_chicken_limit(user_farm):
            embed = await make_embed_object(description="Trade cannot be completed. The total number of chickens after the trade exceeds the maximum limit.")
            return embed
        
        author_farm['chickens'] = [chicken for chicken in author_farm['chickens'] if chicken not in author_chickens]
        user_farm['chickens'] = [chicken for chicken in user_farm['chickens'] if chicken not in user_chickens]
        author_farm['chickens'].extend(user_chickens)
        user_farm['chickens'].extend(author_chickens)
        await Farm.update(ctx.user.id, chickens=author_farm['chickens'])
        await Farm.update(self.target.id, chickens=user_farm['chickens'])
        embed = await make_embed_object(description=f":white_check_mark: {ctx.user.display_name} and {self.target.display_name} have traded chickens.")
        await self.delete_shared_dict(ctx.user)
        return embed