from dotenv import load_dotenv
from tools.cache.init import cache_initiator
import os
import discord
import concurrent.futures
import asyncio

spam_command_cooldown = .8
regular_command_cooldown = 3.5
queue_command_cooldown = 90
tax = .15

async def send_bot_embed(ctx, ephemeral=False, **kwargs):
    """Create an embed without a title."""
    embed = discord.Embed(**kwargs, color=discord.Color.yellow())
    if isinstance(ctx, discord.Interaction):
        message = await ctx.response.send_message(embed=embed, ephemeral=ephemeral)
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
     try:
        reaction, _ = await client.wait_for("reaction_add", check=lambda reaction, author: reaction.message.id == msg.id and author.id == user.id and reaction.emoji in ["✅", "❌"], timeout=60)
        if reaction.emoji == "✅":
            return True
        else:
            return False
     except asyncio.TimeoutError:
        return False

async def user_cache_retriever(user_id):
    """Retrieve the user cache"""
    from db.userDB import User
    from db.bankDB import Bank
    from db.farmDB import Farm
    user_cache = await cache_initiator.get_user_cache(user_id)
    
    if not user_cache:
        print("db")
        user_data = User.read(user_id)
        farm_data = Farm.read(user_id)
        bank_data = Bank.read(user_id)
        await cache_initiator.add_to_user_cache(user_id, user_data=user_data, farm_data=farm_data, bank_data=bank_data)
        user_cache = await cache_initiator.get_user_cache(user_id)
        return user_cache
    print("cache")
    return user_cache

async def guild_cache_retriever(guild_id):
    """Retrieve the guild cache"""
    from db.botConfigDB import BotConfig
    guild_cache = await cache_initiator.get_guild_cache(guild_id)
    if not guild_cache:
        guild_data = BotConfig.read(guild_id)
        await cache_initiator.add_to_guild_cache(guild_id, prefix=guild_data['prefix'], toggled_modules=guild_data['toggled_modules'], channel_id=guild_data['channel_id'])
        guild_cache = await cache_initiator.get_guild_cache(guild_id)
        return guild_cache
    return guild_cache

def update_scheduler(func):
    """Schedules a coroutine to be run in the event loop."""
    if asyncio.get_event_loop().is_running():
        asyncio.ensure_future(func())
    else:
        asyncio.run(func())

def request_threading(func):
    """Request a function to be run in a separate thread."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future = executor.submit(func)
        return future.result()
    