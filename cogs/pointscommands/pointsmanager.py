"""
This module contains the PointsManager class which is responsible for managing and giving points to the users in the bot.
"""
from discord.ext import commands
from lib import user_cache_retriever
from db import User
from tools import listener_checks
import discord
import time
import math

__all__ = ['PointsManager']

class PointsManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.message_cache = {}
        self.join_time = {}
        self.init_time = math.ceil(time.time())

    async def reward_points_if_possible(self, user_id: int, user_data: dict) -> int | None:
        """
        Rewards the user with points in the bot cache's system if he is in the message cache.

        Args:
            user_id (int): The id of the user to reward.

        Returns:
            int | None
        """        
        current_time = math.ceil(time.time())
        message_time = self.message_cache[user_id]
        time_difference = current_time - message_time
        time_passed = min(time_difference // 20, 1)
        
        if time_passed > 0:
            time_passed = int(time_passed)
            self.message_cache.pop(user_id)
            await User.update_points(user_id, user_data["points"] + time_passed)
    
    async def count_points(self, user: discord.Member) -> None:
        """
        Counts the points of the user every time he enters a voice channel.

        Args:
            user (discord.Member): The user to count the points.

        Returns:
            None
        """
        if user.bot:
            return
        if user.id not in self.join_time.keys():
            self.join_time[user.id] = math.ceil(time.time())
        else:
            return
    
    async def update_points(self, user: discord.Member) -> int:
        """
        Updates the points of the user every 10 seconds.

        Args:
            user (discord.Member): The user to update the points.
        """
        total_points = 0
        if user.voice:
            total_points = await self.add_points(user)
            self.join_time[user.id] = math.ceil(time.time())
        return total_points
        
    async def add_points(self, user: discord.Member) -> int:
        """
        Adds points to the user based on the time he has been in the voice channel.

        Args:
            user (discord.Member): The user to add the points.

        Returns:
            int
        """
        if user.id not in self.join_time and user.voice:
            self.join_time[user.id] = self.init_time

        total_points = (math.ceil(time.time()) - self.join_time[user.id]) // 10
        total_points = int(total_points)
        return total_points
    
    async def update_user_points_in_voice(self, user: discord.Member, user_data: dict) -> None:
        """
        Updates the points of the user currently in a voice channel while doing a bot command.

        Args:
            user (discord.Member): The user to update the points.

        Returns:
            None
        """
        total_points = await self.update_points(user)
        if total_points > 0:
            await User.update_points(user.id, user_data["points"] + total_points)
    
    async def on_user_leaving_voice(self, user: discord.Member) -> None:
        """
        Updates the points of the user when he leaves the voice channel.

        Args:
            user (discord.Member): The user to update the points.

        Returns:
            None
        """
        if user.id not in self.join_time:
            self.join_time[user.id] = self.init_time
        total_points = await self.add_points(user)
        cache = await user_cache_retriever(user.id)
        user_data = cache["user_data"]
        await User.update_points(user.id, user_data["points"] + total_points)
        self.join_time.pop(user.id)
        
    @listener_checks()
    @commands.Cog.listener()
    async def on_voice_state_update(self, user: discord.Member, before, after):
        """
        Listens to the voice state update event.
        """
        cache = await user_cache_retriever(user.id)

        if not user_data:
            return

        if user.bot:
            return
        
        user_data = cache["user_data"]
        
        if before.channel is None and after.channel is not None:
            await self.count_points(user)

        elif before.channel is not None and after.channel is None:
            await self.on_user_leaving_voice(user)

    @listener_checks()        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Listens to the message event.
        """
        if message.author.bot:
            return
        
        cache = await user_cache_retriever(message.author.id)

        if not user_data:
            return
        
        user_data = cache["user_data"]

        if message.author.id not in self.message_cache:
            self.message_cache[message.author.id] = time.time()

        await self.reward_points_if_possible(message.author.id, user_data)

async def setup(bot):
    await bot.add_cog(PointsManager(bot))
