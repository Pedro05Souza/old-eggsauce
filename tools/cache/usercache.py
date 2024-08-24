from pympler import asizeof
from tools.cache.cache import BotCache
import logging
import asyncio
logger = logging.getLogger('botcore')

class UserCache(BotCache):

    def __init__(self, memory_limit):
        super().__init__(memory_limit)
    
    async def put(self, key: int, **kwargs) -> None:
        allowed_kw = {"farm_data", "bank_data", "user_data"}
        if all(kw in allowed_kw for kw in kwargs):
            await super().put(key, **kwargs)
        else:
            raise ValueError("Invalid keyword arguments.")
        
    async def clear_users_cache_periondically(self, interval) -> None:
        """
        Periodically clear the user cache.
        """
        while True:
            await asyncio.sleep(interval)
            if len(self.cache) > 0:
                await super().clear()
                logger.info("User cache cleared.")

    async def get_user_cache_memory_consuption(self) -> int:
        """
        Get the memory consumption of the user cache.
        """
        return asizeof.asizeof(self.cache)
    
    async def delete(self, key) -> None:
        await super().delete(key)