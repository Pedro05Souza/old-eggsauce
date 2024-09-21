from discord.ext import commands
from tools.decorators import before_loop_decorator
from discord.ext import tasks
from tools.cache import cache_initiator
from tools.listeners import listener_manager
from tools.shared import cooldown_tracker


class Tasks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cache__clear_task.start()
        self.listener__clear_task.start()
        self.cooldown__clear_task.start()

    @before_loop_decorator
    @tasks.loop(hours=1)
    async def cache__clear_task(self) -> None:
        """
        Periodically clears the cache.

        Returns:
            None
        """
        await cache_initiator.clear_cache_periodically()

    @before_loop_decorator
    @tasks.loop(hours=2)
    async def listener__clear_task(self) -> None:
        """
        Periodically clears the listeners.

        Returns:
            None
        """
        await listener_manager.clear_listeners()

    @before_loop_decorator
    @tasks.loop(hours=2)
    async def cooldown__clear_task(self) -> None:
        """
        Periodically clears the cooldown tracker.

        Returns:
            None
        """
        cooldown_tracker.clear()

async def setup(bot):
    await bot.add_cog(Tasks(bot))

    

    

    