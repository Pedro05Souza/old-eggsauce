from discord.ext import commands
from tools.shared import guild_cache_retriever, user_cache_retriever
from db.userdb import User
import discord
import time
import math
import logging
logger = logging.getLogger("botcore")

class PointsManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.message_cache = {}
        self.join_time = {}
        self.init_time = math.ceil(time.time())

    async def check_if_user_in_message_cache(self, user_id: int) -> bool:
        """
        Check if the user is in the message cache.

        Args:
            user_id (int): The id of the user to check.

        Returns:
            bool
        """
        return user_id in self.message_cache

    async def reward_points_if_possible(self, user_id: int, user_data: dict) -> int | None:
        """
        Rewards the user with points in the bot cache's system if he is in the message cache.

        Args:
            user_id (int): The id of the user to reward.

        Returns:
            int | None
        """
        if not await self.check_if_user_in_message_cache(user_id):
            return None
        
        current_time = math.ceil(time.time())
        message_time = self.message_cache[user_id]
        time_difference = current_time - message_time
        time_passed = min(time_difference // 20, 1)
        if time_passed > 0:
            time_passed = int(time_passed)
            self.message_cache.pop(user_id)
            User.update_points(user_id, user_data["points"] + time_passed)
    
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
            User.update_points(user.id, user_data["points"] + total_points)
            user_data["points"] += total_points
    
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
        User.update_points(user.id, user_data["points"] + total_points)
        self.join_time.pop(user.id)
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, user: discord.Member, before, after):
        """
        Listens to the voice state update event.
        """
        guild_data = await guild_cache_retriever(user.guild.id)

        if not guild_data['toggled_modules'] == "N":

            user_data = await user_cache_retriever(user.id)
            user_data = user_data["user_data"]

            if user.bot:
                return
            if user_data and before.channel is None and after.channel is not None:
                await self.count_points(user)
            elif user_data and before.channel is not None and after.channel is None:
                await self.on_user_leaving_voice(user)
            
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Listens to the message event.
        """
        if message.author.bot:
            return
        
        guild_data = await guild_cache_retriever(message.guild.id)

        if guild_data['toggled_modules'] == "N":
            return
        
        user_data = await user_cache_retriever(message.author.id)
        user_data = user_data["user_data"]

        if not user_data:
            return
        
        if message.author.id not in self.message_cache:
            self.message_cache[message.author.id] = time.time()

        await self.reward_points_if_possible(message.author.id, user_data)

async def setup(bot):
    await bot.add_cog(PointsManager(bot))
