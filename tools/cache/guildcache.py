from tools.cache.cache import BotCache
from pympler import asizeof
from typing import Union
import asyncio
import logging
logger = logging.getLogger('botcore')


class GuildCache(BotCache):

    def __init__(self, memory_limit: int):
        super().__init__(memory_limit)

    async def put(self, key: int, **kwargs) -> None:
        allowed_kw = {"prefix", "channel_id", "toggled_modules"}
        if all(kw in allowed_kw for kw in kwargs):
            await super().put(key, **kwargs)
        else:
            raise ValueError("Invalid keyword arguments.")

    async def get_guild_cache_memory_consuption(self) -> int:
        return asizeof.asizeof(self.cache)
    
    async def clear_guild_cache_periodically(self, interval) -> None:
        while True:
            await asyncio.sleep(interval)
            if len(self.cache) > 0:
                await super().clear()
                logger.info("Guild cache cleared.")