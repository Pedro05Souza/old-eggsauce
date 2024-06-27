
import discord
from db.botConfigDB import BotConfig

async def create_embed_without_title(ctx, description, **kwargs):
    """Create an embed without a title."""
    if not BotConfig.read(ctx.guild.id)['channel_id'] == ctx.channel.id:
        channel = discord.utils.get(ctx.guild.text_channels, id=BotConfig.read(ctx.guild.id)['channel_id'])
        await ctx.author.send(f"Please use the commands channel: {channel.mention}")
        return
    embed = discord.Embed(description=description, color=discord.Color.yellow())
    if isinstance(ctx, discord.Interaction):
        message = await ctx.response.send_message(embed=embed, **kwargs)
    else:
        message = await ctx.send(embed=embed, **kwargs)
    return message

async def create_embed_with_title(ctx, title, description, **kwargs):
    """Create an embed with a title."""
    if not BotConfig.read(ctx.guild.id)['channel_id'] == ctx.channel.id:
        channel = discord.utils.get(ctx.guild.text_channels, id=BotConfig.read(ctx.guild.id)['channel_id'])
        await ctx.author.send(f"Please use the commands channel: {channel.mention}")
        return
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


            

    



