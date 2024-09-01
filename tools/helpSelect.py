from discord.ui import View, Select
from discord import Interaction, SelectOption
from tools.shared import make_embed_object, send_bot_embed, confirmation_embed
from db.botConfigDB import BotConfig

class ShowPointsModules(View):
        def __init__(self, author_id: int, guild_cache: dict, *args, **kwargs):
            super().__init__(*args, **kwargs)
            select = Select(placeholder="Choose a module...",
                            min_values=1,  
                            max_values=1,  
                            options=[
                                SelectOption(label="Total", value="T", description="Select this option to enable all points commands.", emoji="🔥"),
                                SelectOption(label="Friendly", value="F", description="Select this option to enable friendly points commands.", emoji="🌟"),
                                SelectOption(label="Hostile", value="H", description="Select this option to enable hostile points commands.", emoji="🔫"),
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
                "F": "Friendly",
                "H": "Hostile",
                "N": "None"
            }
            moduleSelected = interaction.data["values"][0]
            flag = 0
            if moduleSelected in possibleOptions:
                await send_bot_embed(interaction, ephemeral=True, description=f":white_check_mark: Module {possibleOptions[moduleSelected]} selected")
                if possibleOptions[moduleSelected] == "Total" or possibleOptions[moduleSelected] == "Hostile":
                    if await confirmation_embed(interaction, interaction.user, f"Enabling **{possibleOptions[moduleSelected]}** will require an extra confirmation. There are hostile commands that may/can affect the server enviroment. Do you want to enable the **Destructive Hostiles** commands?"):
                        await send_bot_embed(interaction, ephemeral=True, description=":white_check_mark: **Destructive Hostiles** were enabled.")
                        flag = 1
                    else:
                        await send_bot_embed(interaction, ephemeral=True, description=":white_check_mark: **Destructive Hostiles** were not enabled.")
                if flag == 1:
                    BotConfig.update_toggled_modules(interaction.guild_id, moduleSelected + "D")
                else:
                    BotConfig.update_toggled_modules(interaction.guild_id, moduleSelected)