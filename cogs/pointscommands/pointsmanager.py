from discord.ext import commands
from tools.shared import guild_cache_retriever, user_cache_retriever
from db.userdb import User
from tools.settings import USER_SALARY_DROP
import discord
import time
import math
import logging
import asyncio
logger = logging.getLogger("botcore")

class PointsManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.message_cache = {}
        self.join_time = {}
        self.init_time = math.ceil(time.time())
        self.locks = {}

    async def check_if_user_in_message_cache(self, user_id: int) -> bool:
        """
        Check if the user is in the message cache.

        Args:
            user_id (int): The id of the user to check.

        Returns:
            bool
        """
        return user_id in self.message_cache

    async def reward_points_if_possible(self, user_id: int, data: dict) -> int | None:
        """
        Rewards the user with points in the bot cache's system if he is in the message cache.

        Args:
            user_id (int): The id of the user to reward.
            data (dict): The data of the user.

        Returns:
            int | None
        """
        if not await self.check_if_user_in_message_cache(user_id):
            return None
        current_time = math.ceil(time.time())
        message_time = self.message_cache[user_id]
        time_difference = current_time - message_time
        time_passed = min(time_difference // 10, 1)
        if time_passed > 0:
            time_passed = int(time_passed)
            self.message_cache.pop(user_id)
            logger.info(f"{user_id} has received {time_passed} eggbux from sending messages.")
            return time_passed
        else:
            return None
    
    async def count_points(self, user: discord.Member) -> None:
        """
        Counts the points of the user every time he enters a voice channel.

        Args:
            user (discord.Member): The user to count the points.

        Returns:
            None
        """
        userId = user.id
        if user.bot:
            return
        if userId not in self.join_time.keys():
            self.join_time[userId] = math.ceil(time.time())
        else:
            return
    
    async def update_points(self, user: discord.Member) -> int:
        """
        Updates the points of the user every 10 seconds.

        Args:
            user (discord.Member): The user to update the points.
        """
        userId = user.id

        if not user.voice and userId in self.join_time.keys():
            total_points = await self.add_points(self.join_time[userId])
            self.join_time.pop(userId)
            return total_points
        
        if userId in self.join_time.keys():
            total_points = await self.add_points(self.join_time[userId])
            self.join_time[userId] = math.ceil(time.time())
            return total_points
        
        if userId not in self.join_time.keys() and user.voice:
           total_points = await self.add_points(self.init_time)
           self.join_time[userId] = math.ceil(time.time())
           return total_points

    async def add_points(self, type: int) -> int:
        """
        Adds points to the user based on the time he has been in the voice channel.

        Args:
            type (int): The time the user joined the voice channel.

        Returns:
            int
        """
        total_points = (math.ceil(time.time()) - type) // 10
        total_points = int(total_points)
        return total_points
    
    async def update_user_points(self, user: discord.Member, data: dict) -> dict:
        """
        Updates the user's points when any command is used.

        Args:
            user (discord.Member): The user to update the points.
            data (dict): The data of the user.
        """
        user_data = data['user_data']
        salary_gain = await self.get_salary_points(user, user_data)
        if not user.id in self.locks: # means that the user havent joined voice or sent a message
            return user_data, salary_gain
        async with self.locks[user.id]:
            voice_points = await self.update_points(user)
            message_points = await self.reward_points_if_possible(user.id, data)
            points = (voice_points or 0) + (message_points or 0)
            if points == 0:
                return user_data, salary_gain
            User.update_points(user.id, user_data["points"] + points)
            return user_data, salary_gain
        
    async def get_salary_points(self, user: discord.Member, user_data: dict) -> int:
        """
        Calculates the salary of the user based on their roles.

        Args:
            user (discord.Member): The user to calculate the salary.
            user_data (dict): The data of the user.

        Returns:
            int
        """
        last_title_drop = time.time() - user_data["salary_time"]
        hours_passed = min(last_title_drop // USER_SALARY_DROP, 12)
        hours_passed = int(hours_passed)
        salary = await self.salary_role(user_data)
        if hours_passed > 0 and user_data["roles"] != "":
            points_gain = salary * hours_passed
            user_data['points'] += points_gain
            User.update_salary_time(user.id)
            logger.info(f"{user.display_name} has received {salary * hours_passed} eggbux from their title.")
            return points_gain
        return 0
    
    async def salary_role(self, user_data: dict) -> int:
        """
        Returns the salary of a user based on their roles.

        Args:
            user_data (dict): The data of the user.

        Returns:
            int
        """
        salarios = {
            "T": 20,
            "L": 40,
            "M": 60,
            "H": 80
        }
        if user_data['roles'] != "":
            return salarios[user_data["roles"][-1]]
        else:
            return 0
        
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
            if user.id not in self.locks:
                self.locks[user.id] = asyncio.Lock()
            if user_data and before.channel is None and after.channel is not None:
                await self.count_points(user)
            elif user_data and before.channel is not None and after.channel is None:
                await self.update_points(user)
                self.locks.pop(user.id)
            else:
                pass
            
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
        
        if message.author.id not in self.locks:
            self.locks[message.author.id] = asyncio.Lock()
        
        if message.author.id not in self.message_cache:
            self.message_cache[message.author.id] = time.time()

async def setup(bot):
    await bot.add_cog(PointsManager(bot))
