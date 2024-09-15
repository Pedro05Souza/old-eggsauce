from tools.cache.cache import BotCache
from pympler import asizeof
import asyncio
import logging
logger = logging.getLogger('botcore')


class GuildCache(BotCache):

    def __init__(self, memory_limit: int):
        super().__init__(memory_limit)

    async def put(self, key: int, **kwargs) -> None:
        """
        Put a value in the cache and validate the keyword arguments.
        Args:
            key (int): The key to put the value for.
            **kwargs: The data to put in the cache.

        Returns:
            None
        """
        allowed_kw = {"prefix", "channel_id", "toggled_modules"}
        if all(kw in allowed_kw for kw in kwargs):
            await super().put(key, **kwargs)
        else:
            raise ValueError("Invalid keyword arguments.")

    async def get_guild_cache_memory_consuption(self) -> int:
        """
        Get the memory consumption of the guild cache.

        Returns:
            int
        """
        return asizeof.asizeof(self.cache)
    
    async def clear_guild_cache_periodically(self, interval) -> None:
        """
        Periodically clear the guild cache.

        Args:
            interval (int): The interval to clear the cache.

        Returns:
            None
        """
        if len(self.cache) > 0:
            await super().clear()
            logger.info("Guild cache cleared.")