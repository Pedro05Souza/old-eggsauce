from dotenv import load_dotenv
import os
import discord
spam_command_cooldown = .8
regular_command_cooldown = 3.5
tax = .15

async def send_bot_embed(ctx, **kwargs):
    """Create an embed without a title."""
    embed = discord.Embed(**kwargs, color=discord.Color.yellow())
    if isinstance(ctx, discord.Interaction):
        message = await ctx.response.send_message(embed=embed)
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

async def confirmation_embed(ctx, user: discord.Member, description):
     """Confirmation embed for modularization"""
     embed = await make_embed_object(title=f":warning: {user.display_name}, you need to confirm this first:", description=description)
     embed.set_footer(text="React with ✅ to confirm or ❌ to cancel.")
     if isinstance(ctx, discord.Interaction):
        await ctx.response.send_message(embed=embed)
        msg = await ctx.original_response()
     else:
        msg = await ctx.send(embed=embed)
     await msg.add_reaction("✅")
     await msg.add_reaction("❌")
     client = ctx.client if isinstance(ctx, discord.Interaction) else ctx.bot
     reaction, _ = await client.wait_for("reaction_add", check=lambda reaction, author: reaction.message.id == msg.id and author.id == user.id and reaction.emoji in ["✅", "❌"])
     if reaction.emoji == "✅":
          return True




            

    



