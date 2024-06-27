from discord.ui import View, Select
import discord
from discord import SelectOption
from tools.embed import create_embed_without_title, make_embed_object
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

        async def callback(self, interaction):
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
                embed = await make_embed_object(description=f":white_check_mark: Module {possibleOptions[moduleSelected]} selected")
                await interaction.response.send_message(embed=embed)
                BotConfig.update_toggled_modules(interaction.guild_id, moduleSelected)

class ShowAllModules(View):
    def __init__(self, author_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        select = Select(placeholder="Choose a module to display its commands...",
                        min_values=1,  
                        max_values=1,  
                        options=[
                            SelectOption(label="Chicken Commands", value="P", description="Select this option to view chicken commands.", emoji="🐔"),
                            SelectOption(label="Interactive Commands", value="U", description="Select this option to view interactive commands.", emoji="🔧"),
                            SelectOption(label="AI Commands", value="U", description="Select this option to view AI commands.", emoji="🤖"),
                            SelectOption(label="Bank Commands", value="U", description="Select this option to view bank commands.", emoji="💰"),
                            SelectOption(label="Hostile Commands", value="U", description="Select this option to view hostile commands.", emoji="🔫"),
                            SelectOption(label="Friendly Commands", value="U", description="Select this option to view friendly commands.", emoji="🌟")
                        ])
        select.callback = self.callback
        self.add_item(select)
        self.author_id = author_id