from discord.ui import View, Select
from discord import Interaction, SelectOption
from tools.shared import make_embed_object, send_bot_embed, confirmation_embed
from db.botConfigDB import BotConfig

class SelectModule(View):
    def __init__(self, author_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        select = Select(placeholder="Choose a module...",
                        min_values=1,  
                        max_values=1,  
                        options=[
                            SelectOption(label="Points", value="P", description="Select this option to view points.", emoji="🎉"),
                            SelectOption(label="Utility", value="U", description="Select this option to view utility commands.", emoji="🔧")
                        ])
        select.callback = self.callback
        self.add_item(select)
        self.author_id = author_id
        
    async def callback(self, interaction):
        if interaction.user.id != self.author_id:
            embed = await make_embed_object(description=":no_entry_sign: You can't interact with this menu.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        moduleSelected = interaction.data["values"][0]
        if moduleSelected == "P":
            embed = await make_embed_object(title="**:egg: Points Module:**", description=":infinity: **Total**: This submodule enables all points-related commads.\n:star: **Friendly**: This submodule is a collection of all friendly related commands, some of them being bank commands, chicken management commands and many fun others. \n:gun: **Hostile**: This sub-module is a collection of all commands that can affect the server enviroment. If you don't want users being able to disconnect, move and mute others it is recommended to disable this sub-module. \n:x: **None**: This submodule disables all points-related commands.") 
            await interaction.response.send_message(embed=embed)
        elif moduleSelected == "U":
            await interaction.response.send_message("WIP: Utility commands are still being developed. Please check back later")
class ShowPointsModules(View):
        def __init__(self,author_id, *args, **kwargs):
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
            if moduleSelected in possibleOptions:
                await send_bot_embed(interaction, ephemeral=True, description=f":white_check_mark: Module {possibleOptions[moduleSelected]} selected")
                if possibleOptions[moduleSelected] == "Total" or possibleOptions[moduleSelected] == "Hostile":
                    if await confirmation_embed(interaction, interaction.user, f":warning: Enabling **{possibleOptions[moduleSelected]}** will require an extra confirmation. There are hostile commands that may/can affect the server enviroment. Do you want to enable the **Destructive Hostiles** commands?"):
                        BotConfig.update_toggled_modules(interaction.guild_id, moduleSelected + "D")
                        await send_bot_embed(interaction, ephemeral=True, description=":white_check_mark: **Destructive Hostiles** were enabled.")
                        return
                    else:
                        BotConfig.update_toggled_modules(interaction.guild_id, moduleSelected)
                        await send_bot_embed(interaction, ephemeral=True, description=":white_check_mark: **Destructive Hostiles** were not enabled.")
                        return
                BotConfig.update_toggled_modules(interaction.guild_id, moduleSelected)