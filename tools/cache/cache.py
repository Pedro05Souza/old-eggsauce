# This file contains the cache for the bot. It is used to store data that is frequently accessed by the bot.
# The cache is used to reduce the number of database queries and improve the bot's performance.
# The cache is implemented as an LRU (Least Recently Used) cache, which evicts the least recently used items when the cache is full.

from pympler import asizeof
from collections import OrderedDict
from dataclasses import dataclass, field
import logging
import asyncio
logger = logging.getLogger('botcore')

@dataclass
class BotCache():
    memory_limit: int
    cache: OrderedDict = field(default_factory=OrderedDict)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock) # Lock to prevent data discrepancies

    async def get(self, key):
        async with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    async def put(self, id, **kwargs):
        async with self.lock:
            if id not in self.cache:
                self.cache[id] = {}
            for key, value in kwargs.items():
                self.cache[id][key] = value
                self.cache.move_to_end(id)
            if asizeof.asizeof(self.cache) > self.memory_limit:
                await self._evict_if_needed()
        
    async def delete(self, key):
        async with self.lock:
            dict_value = self.cache.pop(key, None)
            if dict_value is None:
                logger.warning(f"Key {key} not found in cache.")
            else:
                logger.info(f"Deleted {key} from cache.")

    async def _evict_if_needed(self):
        async with self.lock:
            while asizeof.asizeof(self.cache) > self.memory_limit:
                evicted_key, _ = self.cache.popitem(last=False)
                logger.info(f"Evicting {evicted_key} cache to free up memory.")
    
    async def clear(self):
        self.cache.clear()
        logger.info("Cache cleared.")