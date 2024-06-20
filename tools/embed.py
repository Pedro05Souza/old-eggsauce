
import discord
from discord import Message
from db.userDB import Usuario

async def create_embed_without_title(ctx, description):
    """Create an embed without a title."""
    embed = discord.Embed(description=description)
    message = await ctx.send(embed=embed)
    return message

async def create_embed_with_title(ctx, title, description):
    """Create an embed with a title."""
    embed = discord.Embed(title=title, description=description)
    await ctx.send(embed=embed)


@discord.ui.button(label="Roles", style=discord.ButtonStyle.green)
async def create_buttom_for_roles(button, interaction):
    """Create a button for roles."""
    roleNames = {"Low wage Worker" : "",
                 "Peasant" : "B", 
                 "Brokie who thinks they are rich" : "M", 
                 "Magnate" : "A"
                 }
    possibleRoles = {
        "T"  : discord.Role(guild=interaction.guild.id, name="Low Wage Worker", hoist=True, position=1),
        "B" : discord.Role(guild=interaction.guild.id, name="Peasant", hoist=True, position=2),
        "M" : discord.Role(guild=interaction.guild.id, name="Brokie who thinks they are rich", hoist=True, position=3),
        "A" : discord.Role(guild=interaction.guild.id, name="Magnate", hoist=True, position=4)
    }
    guild_hasRoles = [role for role in roleNames.keys() if role.name not in interaction.guild.roles]
    for role in guild_hasRoles:
        await interaction.guild.create_role(possibleRoles[roleNames[role]])
    if Usuario.read(interaction.user.id):
            match Usuario.read(interaction.user.id)['role']:
                case "":
                    await interaction.user.add_roles(possibleRoles["T"])
                    await create_embed_without_title(interaction, f"{interaction.user.display_name} bought the role of Low Wage Worker.")
                case "T":
                    await interaction.user.add_roles(possibleRoles["B"])
                    await create_embed_without_title(interaction, f"{interaction.user.display_name} bought the role of Peasant.")
                case "TB":
                    await interaction.user.add_roles(possibleRoles["M"])
                    await create_embed_without_title(interaction, f"{interaction.user.display_name} bought the role of Brokie who thinks they are rich.")
                case "TBM":
                    await interaction.user.add_roles(possibleRoles["A"])
                    await create_embed_without_title(interaction, f"{interaction.user.display_name} bought the role of Magnate.")
                case __:
                    await create_embed_without_title(interaction, ":no_entry_sign: Something went wrong with giving the user the expected roles.")
    else:
        await create_embed_without_title(interaction, "You are not registered in the database.")
            


    



