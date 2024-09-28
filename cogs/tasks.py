"""
This module contains the tasks that are run periodically by the bot.
Clears the cache, listeners, cooldown tracker and steal status dictionary.
"""
from discord.ext import commands
from discord.ext import tasks
from temp import cache_initiator
from tools import listener_manager, before_loop_decorator
from lib import cooldown_tracker
from cogs.pointscommands.interactive import steal_status
import logging

logger = logging.getLogger('bot_logger')

__all__ = ['Tasks']

class Tasks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cache_clear_task.start()
        self.listener_clear_task.start()
        self.cooldown_clear_task.start()
        self.steal_status_task.start()

    def cog_unload(self):
        self.cache_clear_task.cancel()
        self.listener_clear_task.cancel()
        self.cooldown_clear_task.cancel()
        self.steal_status_task.cancel()

    @before_loop_decorator
    @tasks.loop(hours=2)
    async def cache_clear_task(self) -> None:
        """
        Periodically clears the cache.

        Returns:
            None
        """
        await cache_initiator.clear_cache_periodically()

    @before_loop_decorator
    @tasks.loop(hours=4)
    async def listener_clear_task(self) -> None:
        """
        Periodically clears the listeners.

        Returns:
            None
        """
        await listener_manager.clear_listeners()

    @before_loop_decorator
    @tasks.loop(hours=4)
    async def cooldown_clear_task(self) -> None:
        """
        Periodically clears the cooldown tracker for the users.

        Returns:
            None
        """
        if len(cooldown_tracker) > 0:
            cooldown_tracker.clear()
            logger.info("Cleared the cooldown tracker.")

    @before_loop_decorator
    @tasks.loop(hours=4)
    async def steal_status_task(self) -> None:
        """
        Periodically clears the steal status.

        Returns:
            None
        """
        if len(steal_status) > 0:
            steal_status.clear()
            logger.info("Cleared the steal status.")

async def setup(bot):
    await bot.add_cog(Tasks(bot))