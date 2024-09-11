from discord.ext import commands
from tools.shared import guild_cache_retriever, user_cache_retriever
from db.userDB import User
from tools.settings import user_salary_drop
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
        """Check if the user is in the message cache."""
        return user_id in self.message_cache

    async def reward_points_if_possible(self, user_id: int) -> None:
        """Rewards the user with points if he is in the message cache."""
        current_time = math.ceil(time.time())
        message_time = self.message_cache[user_id]
        time_difference = current_time - message_time
        time_passed = min(time_difference // 10, 1)
        if time_passed > 0:
            time_passed = int(time_passed)
            user_data = await user_cache_retriever(user_id)
            user_data = user_data["user_data"]
            user_data["points"] += time_passed
            self.message_cache.pop(user_id)
            logger.info(f"{user_id} has received {time_passed} eggbux from sending messages.")
            User.update_points(user_id, user_data["points"])
        else:
            return
    
    async def count_points(self, user: discord.Member) -> None:
        """Counts the points of the user every time he enters a voice channel."""
        userId = user.id
        if user.bot:
            return
        if userId not in self.join_time.keys():
            self.join_time[userId] = math.ceil(time.time())
        else:
            return
    
    async def update_points(self, user: discord.Member) -> int:
        """Updates the points of the user every 10 seconds."""
        userId = user.id

        if not user.voice and userId in self.join_time.keys():
            total_points = await self.add_points(self.join_time[userId], userId)
            self.join_time.pop(userId)
            return total_points
        
        if userId in self.join_time.keys():
            total_points = await self.add_points(self.join_time[userId], userId)
            self.join_time[userId] = math.ceil(time.time())
            return total_points
        
        if userId not in self.join_time.keys() and user.voice:
           total_points = await self.add_points(self.init_time, userId)
           self.join_time[userId] = math.ceil(time.time())
           return total_points

    async def add_points(self, type: int, user_id: int) -> int:
        add_points = (math.ceil(time.time()) - type) // 10
        user_data = await user_cache_retriever(user_id)
        user_data = user_data["user_data"]
        total_points = user_data["points"] + add_points
        User.update_points(user_id, total_points)
        return total_points
    
    async def update_user_points(self, user: discord.Member, data: dict) -> dict:
        """
        Updates the user's points when any command is used.
        """
        user_data = data['user_data']
        if user_data:
            points = await self.update_points(user)
            salary_gain = await self.get_salary_points(user, user_data)
            if points:
                user_data['points'] = points
            else:
                return user_data, salary_gain
            User.update_points(user.id, user_data['points'])
            return user_data, salary_gain
        
    async def get_salary_points(self, user: discord.Member, user_data: dict) -> int:
        """
        Calculates the salary of the user based on their roles.
        """
        last_title_drop = time.time() - user_data["salary_time"]
        hours_passed = min(last_title_drop // user_salary_drop, 12)
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
        """Returns the salary of a user based on their roles."""
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
        """Listens to the voice state update event."""
        guild_data = await guild_cache_retriever(user.guild.id)
        if not guild_data['toggled_modules'] == "N":
            user_data = await user_cache_retriever(user.id)
            user_data = user_data["user_data"]
            if user.bot:
                return
            if user.id not in self.locks:
                self.locks[user.id] = asyncio.Lock()
            async with self.locks[user.id]:
                if user_data and before.channel is None and after.channel is not None:
                    await self.count_points(user)
                elif user_data and before.channel is not None and after.channel is None:
                    await self.update_points(user)
                    self.locks.pop(user.id)
                else:
                    pass
            
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listens to the message event."""
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
        
        async with self.locks[message.author.id]:
            if message.author.id not in self.message_cache:
                self.message_cache[message.author.id] = time.time()
            else:
                await self.reward_points_if_possible(message.author.id)

async def setup(bot):
    await bot.add_cog(PointsManager(bot))
