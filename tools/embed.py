
import discord

async def create_embed_without_title(ctx, description):
    """Create an embed without a title."""
    embed = discord.Embed(description=description)
    await ctx.send(embed=embed)

async def create_embed_with_title(ctx, title, description):
    """Create an embed with a title."""
    embed = discord.Embed(title=title, description=description)
    await ctx.send(embed=embed)