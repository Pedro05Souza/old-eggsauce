from db.botConfigDB import BotConfig
from dotenv import load_dotenv
import os
import discord
spam_command_cooldown = .8
regular_command_cooldown = 3.5

async def create_embed_without_title(ctx, description, **kwargs):
    """Create an embed without a title."""
    embed = discord.Embed(description=description, color=discord.Color.yellow())
    if isinstance(ctx, discord.Interaction):
        message = await ctx.response.send_message(embed=embed, **kwargs)
    else:
        message = await ctx.send(embed=embed, **kwargs)
    return message

async def create_embed_with_title(ctx, title, description, **kwargs):
    """Create an embed with a title."""
    embed = discord.Embed(title=title, description=description, color=discord.Color.yellow())
    if isinstance(ctx, discord.Interaction):
        message = await ctx.response.send_message(embed=embed, **kwargs)
    else:
        message = await ctx.send(embed=embed)
    return message

async def make_embed_object(**kwargs):
    """Create an embed with a title."""
    embed = discord.Embed(**kwargs, color=discord.Color.yellow())
    return embed

def is_dev(ctx):
    """Check if the user is a developer."""
    load_dotenv()
    devs = os.getenv("DEVS").split(",")
    return str(ctx.author.id) in devs

def dev_list():
    """Return the list of developers."""
    load_dotenv()
    devs = os.getenv("DEVS").split(",")
    return devs

async def get_user_title(user_data):
        userRoles = {
            "T" : "Egg Novice",
            "L" : "Egg Apprentice",
            "M" : "Egg wizard",
            "H" : "Egg King",
        }
        if user_data:
            if user_data["roles"] == "":
                return "Unemployed"
            return userRoles[user_data["roles"][-1]]




            

    



