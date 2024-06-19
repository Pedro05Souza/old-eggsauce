
import discord
from db.userDB import Usuario

async def create_embed_without_title(ctx, description):
    """Create an embed without a title."""
    embed = discord.Embed(description=description)
    await ctx.send(embed=embed)

async def create_embed_with_title(ctx, title, description):
    """Create an embed with a title."""
    embed = discord.Embed(title=title, description=description)
    await ctx.send(embed=embed)


@discord.ui.button(label="Roles", style=discord.ButtonStyle.green)
async def create_buttom_for_roles(button, interaction):
    """Create a button for roles."""
    roleNames = ["Low wage Worker", "Peasant", "Brokie who thinks they are rich", "Magnate"]
    possibleRoles = {
        "T" : await interaction.guild.create_role(name="Low wage Worker", color=discord.Color.from_rgb(0,0,0), hoist=True),
        "B" : await interaction.guild.create_role(name="Peasant", color=discord.Color.from_rgb(0,0,0), hoist=True),
        "M" : await interaction.guild.create_role(name="Brokie who thinks they are rich", color=discord.Color.from_rgb(0,0,0), hoist=True),
        "A" : await interaction.guild.create_role(name="Magnate", color=discord.Color.from_rgb(0,0,0), hoist=True)
    }
    if Usuario.read(interaction.user.id):
        userRoles = Usuario.read(interaction.user.id)["roles"][-1]



