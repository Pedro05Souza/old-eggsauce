"""
This module contains commands that require at least 2 users to run.
"""
from discord.ext import commands
from discord.ext.commands import Context
from lib import user_cache_retriever, send_bot_embed, confirmation_embed
from lib.chickenlib import EventData, is_non_tradable_chicken, get_usr_farm, get_non_tradable_chickens, get_max_chicken_limit, get_rarity_emoji
from db import Farm
from views.selection import ChickenSelectView, chicken_options_initializer
from resources import REGULAR_COOLDOWN
from tools import pricing, on_awaitable
import discord

__all__ = ['ChickenInteractive']


class ChickenInteractive(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_command(name="tradechicken", aliases=["tc", "trade"], usage="tradeChicken <user>", description="Trade a chicken(s) with another user.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def trade_chicken(self, ctx: Context, user: discord.Member) -> None:
        """
        Trade a chicken(s) with another user.

        Args:
            ctx (Context): The context of the command.
            user (discord.Member): The user to trade the chicken(s) with.
        
        Returns:
            None
        """
        
        farm_author = ctx.data["farm_data"]
        user_cache_data = await user_cache_retriever(user.id)
        farm_target = user_cache_data["farm_data"]

        if farm_target:

            if not await EventData.is_yieldable(ctx, ctx.author, user):
                return

            if not farm_author['chickens'] or not farm_target['chickens']:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, {user.display_name} doesn't have any chickens.")
                return
            
            if user.id == ctx.author.id:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't trade with yourself.")
                return
            
            if len(farm_author['chickens']) == 1 and await is_non_tradable_chicken(farm_author['chickens'][0]['rarity']):
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't trade this chicken.")
                return
            
            async with EventData.manage_event_context(ctx.author, user, awaitable=True):
                confirmation = await confirmation_embed(ctx, user, f":question: :chicken: **{ctx.author.display_name}** has sent a trade request to **{user.display_name}**. **{user.display_name}**. Do you accept the trade request?")

                if confirmation:
                    await self.trade_chickens(ctx, user, farm_author, farm_target, user_cache_data)
                else:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} has declined the trade request.")
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} doesn't have a farm.")

    async def trade_chickens(self, ctx: Context, user: discord.Member, farm_author: dict, farm_target: dict, user_cache_data: dict) -> None:
        """
        Trade the chickens.

        Args:
            ctx (Context): The context of the command.
            User (discord.Member): The user to trade the chicken(s) with.
            t (EventData): The event data.
            farm_author (dict): The farm data of the author.
            farm_target (dict): The farm data of the target.
            user_cache_data (dict): The user cache data.

        Returns:
            None
        """
        authorEmbed = await get_usr_farm(ctx, ctx.author, ctx.data)
        userEmbed = await get_usr_farm(ctx, user, user_cache_data)
        trade_data = [farm_author['chickens'], farm_target['chickens']]
        trade_data[0] = [chicken for chicken in trade_data[0] if chicken['rarity'] not in await get_non_tradable_chickens()]
        trade_data[1] = [chicken for chicken in trade_data[1] if chicken['rarity'] not in await get_non_tradable_chickens()]
        members_data = [ctx.author, user]
        embeds = [authorEmbed, userEmbed]

        if len(farm_target['chickens']) == 1 and farm_target['chickens'][0]['rarity'] == "ETHEREAL":
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't trade an ethereal chicken.")
            await on_awaitable(ctx.author.id, user.id)
            return
        
        shared_trade_dict = {}
        options_author = await chicken_options_initializer(trade_data[0], ctx.data)
        view_author = ChickenSelectView(
            chickens=trade_data, 
            author=members_data, 
            action="T", 
            embed_text=embeds, 
            role="author", 
            shared_trade_dict=shared_trade_dict, 
            selection_options=options_author
            )

        options_user = await chicken_options_initializer(trade_data[1], user_cache_data)
        view_user = ChickenSelectView(
            chickens=trade_data, 
            author=members_data, 
            action="T", 
            embed_text=embeds, 
            role="user", 
            instance_bot=self.bot, 
            shared_trade_dict=shared_trade_dict, 
            user_view=view_author,
            selection_options=options_user
            )
        view_author.user_view = view_user

        await ctx.send(embed=authorEmbed, view=view_author)
        await ctx.send(embed=userEmbed, view=view_user)

    @commands.hybrid_command(name="giftchicken", aliases=["gc"], usage="giftChicken <index> <user>", description="Gift a chicken to another user.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def gift_chicken(self, ctx: Context, index: int, user: discord.Member) -> None:
        """
        Gift a chicken to another user.

        Args:
            ctx (Context): The context of the command.
            index (int): The index of the chicken to gift.
            user (discord.Member): The user to gift the chicken to.
        
        Returns:
            None
        """
        
        author_data = ctx.data["farm_data"]
        cache = await user_cache_retriever(user.id)
        user_farm_data = cache["farm_data"]
        index -= 1

        if user_farm_data:

            if not await EventData.is_yieldable(ctx, ctx.author, user):
                return
            
            if index > len(author_data['chickens']) or index < 0:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
                return
            
            if user.id == ctx.author.id:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't gift a chicken to yourself.")
                return
            
            if len(user_farm_data['chickens']) >= await get_max_chicken_limit(user_farm_data):
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, {user.display_name} already has the maximum amount of chickens.")
                return
            
            gifted_chicken = author_data['chickens'][index]

            if await is_non_tradable_chicken(gifted_chicken['rarity']):
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't gift this chicken.")
                return
            
            async with EventData.manage_event_context(ctx.author, user, awaitable=True):
            
                confirmation = await confirmation_embed(ctx, ctx.author, f":question: {ctx.author.display_name}, are you sure you want to gift **{await get_rarity_emoji(gifted_chicken['rarity'])}{gifted_chicken['rarity']}** {gifted_chicken['name']} to {user.display_name}?")

                if confirmation:
                    await self.gift_request(ctx, user, gifted_chicken, author_data, user_farm_data, index)
                else:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you have cancelled the gift request.")
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} doesn't have a farm.")

    async def gift_request(self, ctx: Context, user: discord.Member, gifted_chicken: dict, author_data: dict, user_data: dict, index: int) -> None:
        """
        Gift request to the user.

        Args:
            ctx (Context): The context of the command.
            user (discord.Member): The user to gift the chicken to.
            gifted_chicken (dict): The gifted chicken.
            author_data (dict): The author data.
            user_data (dict): The user data.

        Returns:
            None
        """  
        confirmation = await confirmation_embed(ctx, user, f":question: {user.display_name}, {ctx.author.display_name} has sent you a gift request for **{await get_rarity_emoji(gifted_chicken['rarity'])}{gifted_chicken['rarity']}** {gifted_chicken['name']}. Do you accept the gift request?")
        if confirmation:
            chicken = author_data['chickens'][index]
            user_data['chickens'].append(chicken)
            author_data['chickens'].remove(chicken)
            await Farm.update(ctx.author.id, chickens=author_data['chickens'])
            await Farm.update(user.id, chickens=user_data['chickens'])
            await send_bot_embed(ctx, description=f":gift: {ctx.author.display_name}, the chicken has been gifted to {user.display_name}.")
            await on_awaitable(ctx.author.id, user.id)
            return
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} has declined the gift request.")
            await on_awaitable(ctx.author.id, user.id)
            return
        
async def setup(bot):
    await bot.add_cog(ChickenInteractive(bot))