"""
This module contains the class ShowPointsModules which is a discord.ui.View class that is used to create a select menu for the user to select which points module they want to enable or disable.
"""
from discord.ui import View, Select
from discord import Interaction, SelectOption
from lib.shared import make_embed_object, send_bot_embed
from db.botconfigdb import BotConfig

class ShowPointsModules(View):
        
        def __init__(self, author_id: int, guild_cache: dict, *args, **kwargs):
            super().__init__(*args, **kwargs)
            select = Select(placeholder="Choose a module...",
                            min_values=1,  
                            max_values=1,  
                            options=[
                                SelectOption(label="Total", value="T", description="Select this option to enable all points commands.", emoji="🔥"),
                                SelectOption(label="Chicken", value="C", description="Select this option to enable chicken related commands.", emoji="🐣"),
                                SelectOption(label="Interactive", value="H", description="Select this option to enable interactive related points commands.", emoji="🪩"),
                                SelectOption(label="None", value="N", description="Select this option to disable all points commands.", emoji="❌")
                            ])
            select.callback = self.callback
            self.add_item(select)
            self.author_id = author_id
            self.guild_cache = guild_cache

        async def callback(self, interaction: Interaction) -> None:
            if interaction.user.id != self.author_id:
                embed = await make_embed_object(description=":no_entry_sign: You can't interact with this menu.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            possibleOptions = {
                "T": "Total",
                "C": "Chicken",
                "I": "Interactive",
                "N": "None"
            }
            moduleSelected = interaction.data["values"][0]
            await send_bot_embed(interaction, ephemeral=True, description=f":white_check_mark: Module {possibleOptions[moduleSelected]} selected")
            BotConfig.update_toggled_modules(interaction.guild.id, moduleSelected)