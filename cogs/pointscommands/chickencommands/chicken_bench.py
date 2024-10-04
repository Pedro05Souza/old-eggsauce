"""
This module contains commands for managing the chicken bench in the chicken game.
"""
from discord.ext import commands
from discord.ext.commands import Context
from db import Farm
from lib import return_data, send_bot_embed
from lib.chickenlib import get_user_bench, get_rarity_emoji, EventData, get_max_chicken_limit
from tools import pricing
from resources import REGULAR_COOLDOWN, MAX_BENCH
import discord

__all__ = ['ChickenBench']

class ChickenBench(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="bench", aliases=["b"], usage="b", description="You can store chickens in the bench.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def view_bench(self, ctx: Context, user: discord.Member = None) -> None:
        """
        View the chickens in the bench.

        Args:
            ctx (Context): The context of the command.
            user (discord.Member, optional): The user to check the bench. Defaults to None, which is the author of the command.
        
        Returns:
            None
        """
        farm_data, user = await return_data(ctx, user)
        farm_data = farm_data["farm_data"]

        if farm_data:
            await get_user_bench(ctx, farm_data, user)
        else:
            await send_bot_embed(ctx,description= f":no_entry_sign: {user.display_name}, you don't have a farm.")

    @commands.hybrid_command(name="addbench", aliases=["ab"], usage="addbench <index>", description="Add a chicken from the farm to the bench.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def add_bench(self, ctx: Context, index: int) -> None:
        """
        Adds a chicken to the bench.

        Args:
            ctx (Context): The context of the command.
            index (int): The index of the chicken to add.

        Returns:
            None
        """
        
        farm_data = ctx.data["farm_data"]
        index -= 1

        if index > len(farm_data['chickens']) or index < 0:
            await send_bot_embed(ctx,description= f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
            return
        
        if len(farm_data['bench']) >= MAX_BENCH:
            await send_bot_embed(ctx,description= f":no_entry_sign: {ctx.author.display_name}, the bench is full.")
            return
        
        if not await EventData.is_yieldable(ctx, ctx.author):
            return
        
        async with EventData.manage_event_context(ctx.author):
            farm_data['bench'].append(farm_data['chickens'][index])
            farm_data['chickens'].pop(index)
            await Farm.update(ctx.author.id, bench=farm_data['bench'], chickens=farm_data['chickens'])
            await send_bot_embed(ctx,description= f":white_check_mark: {ctx.author.display_name}, **{get_rarity_emoji(farm_data['bench'][-1]['rarity'])}{farm_data['bench'][-1]['rarity']} {farm_data['bench'][-1]['name']}** has been added to the bench.")
 
    @commands.hybrid_command(name="removebench", aliases=["rb"], usage="removebench <index>", description="Remove a chicken from the bench to the farm.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def remove_bench(self, ctx: Context, index: int) -> None:
        """
        Removes a chicken from the bench.

        Args:
            ctx (Context): The context of the command.
            index (int): The index of the chicken to remove.
        
        Returns:
            None
        """
        farm_data = ctx.data["farm_data"]
        index -= 1

        if index > len(farm_data['bench']) or index < 0:
            await send_bot_embed(ctx,description= f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
            return
        
        if len(farm_data['chickens']) >= get_max_chicken_limit(farm_data):
            await send_bot_embed(ctx,description= f":no_entry_sign: {ctx.author.display_name}, you have reached the maximum chicken limit.")
            return
        
        if not await EventData.is_yieldable(ctx, ctx.author):
            return
        
        async with EventData.manage_event_context(ctx.author):
            farm_data['chickens'].append(farm_data['bench'][index])
            farm_data['bench'].pop(index)
            await Farm.update(ctx.author.id, bench=farm_data['bench'], chickens=farm_data['chickens'])
            await send_bot_embed(ctx,description= f":white_check_mark: {ctx.author.display_name}, the **{get_rarity_emoji(farm_data['chickens'][-1]['rarity'])}{farm_data['chickens'][-1]['rarity']} {farm_data['chickens'][-1]['name']}** has been removed from the bench.")
            
    @commands.hybrid_command(name="switchbench", aliases=["sb"], usage="switchb <index_farm> <index_bench>", description="Switch a chicken from the farm to the bench.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def switch_bench(self, ctx: Context, index_farm: int, index_bench_int: int) -> None:
        """
        Switches a chicken from the farm to the bench.

        Args:
            ctx (Context): The context of the command.
            index_farm (int): The index of the chicken in the farm.
            index_bench_int (int): The index of the chicken in the bench.
        
        Returns:
            None
        """
        
        farm_data = ctx.data["farm_data"]
        index_farm -= 1
        index_bench_int -= 1

        if index_farm > len(farm_data['chickens']) or index_farm < 0 or index_bench_int > len(farm_data['bench']) or index_bench_int < 0:
            await send_bot_embed(ctx,description= f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
            return
        
        async with EventData.manage_event_context(ctx.author):
            farm_data['chickens'][index_farm], farm_data['bench'][index_bench_int] = farm_data['bench'][index_bench_int], farm_data['chickens'][index_farm]
            await Farm.update(ctx.author.id, bench=farm_data['bench'], chickens=farm_data['chickens'])
            await send_bot_embed(ctx,description= f":white_check_mark: {ctx.author.display_name}, the chickens have been switched.")

async def setup(bot):
    await bot.add_cog(ChickenBench(bot))