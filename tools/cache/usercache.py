from pympler import asizeof
from tools.cache.cache import BotCache
import logging
import asyncio
logger = logging.getLogger('botcore')

class UserCache(BotCache):

    def __init__(self, memory_limit):
        super().__init__(memory_limit)
    
    async def put(self, key: int, **kwargs) -> None:
        """
        Puts a value in the cache and validate the keyword arguments.
        Args:
            key (int): The key to put the value for.
            **kwargs: The data to put in the cache.

        Returns:
            None
        """
        allowed_kw = {"farm_data", "bank_data", "user_data"}
        if all(kw in allowed_kw for kw in kwargs):
            await super().put(key, **kwargs)
        else:
            raise ValueError("Invalid keyword arguments.")
        
    async def clear_users_cache_periondically(self, interval) -> None:
        """
        Periodically clears the user cache.

        Args:
            interval (int): The interval to clear the cache.

        Returns:
            None
        """
        while True:
            await asyncio.sleep(interval)
            if len(self.cache) > 0:
                await super().clear()
                logger.info("User cache cleared.")

    async def get_user_cache_memory_consuption(self) -> int:
        """
        Gets the memory consumption of the user cache.

        Returns:
            int
        """
        return asizeof.asizeof(self.cache)