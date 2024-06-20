
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
    message = await ctx.send(embed=embed)
    return message

            


    



