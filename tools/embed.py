
import discord

async def create_embed_without_title(ctx, description):
    embed = discord.Embed(description=description)
    await ctx.send(embed=embed)

async def create_embed_with_title(ctx, title, description):
    embed = discord.Embed(title=title, description=description)
    await ctx.send(embed=embed)