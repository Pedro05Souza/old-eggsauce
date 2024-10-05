"""
This module contains the tasks that are run periodically by the bot.
Clears the cache, listeners, cooldown tracker and steal status dictionary.
"""
from discord.ext import commands
from discord.ext import tasks
from temp import cache_initiator, cooldown_tracker, steal_status
from tools import listener_manager, before_loop_decorator
from logs import log_info

__all__ = ['Tasks']

class Tasks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.tasks = [
            self.cache_clear_task, 
            self.listener_clear_task, 
            self.cooldown_clear_task, 
            self.steal_status_task, 
            ]
        for task in self.tasks:
            task.start()

    def cog_unload(self):
        for task in self.tasks:
            task.cancel()

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
            log_info("Cleared the cooldown tracker.")

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
            log_info("Cleared the steal status.")

async def setup(bot):
    await bot.add_cog(Tasks(bot))