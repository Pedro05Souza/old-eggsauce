from discord.ui import View, Select
import discord
from discord import SelectOption
from tools.pagination import PaginationView

class SelectModule(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        select = Select(placeholder="Choose a module...",
                        min_values=1,  
                        max_values=1,  
                        options=[
                            SelectOption(label="Points", value="P", description="Select this option to view points.", emoji="🎉"),
                            SelectOption(label="Utility", value="U", description="Select this option to view utility commands.", emoji="🔧")
                        ])
        self.add_item(select)

    async def callback(self, interaction):
        moduleSelected = interaction.data['values'][0]
        if moduleSelected == "P":
            await interaction.response.send_message("Points module selected.")
        elif moduleSelected == "U":
            await interaction.response.send_message("Utility module selected.")

    

    async def points_commands_desc(self, interaction):
        """Send a message with the description of the points commands."""
        embed = discord.Embed(title="Points Commands", description="The points module contains a total of 4 submodules. These are: \n\n1. `**Total**` - This submodule enables all points-related commads. \n\n2. **Friendly** - This submodule enables every friendly and interactive points commands. \n\n3. **Hostile** - This submodule enables all hostile points commands. \n\n4. `NP` - This submodule disables all points commands.", color=discord.Color.green())
        
        


