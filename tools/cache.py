# This file contains the cache for the bot. It is used to store data that is frequently accessed by the bot.
# The cache is used to reduce the number of database queries and improve the bot's performance.
# The cache is implemented as an LRU (Least Recently Used) cache, which evicts the least recently used items when the cache is full.

from pympler import asizeof
from collections import OrderedDict
from dataclasses import dataclass, field
import logging
logger = logging.getLogger('botcore')

@dataclass
class LRUGuildCache():
    memory_limit: int
    cache: OrderedDict = field(default_factory=OrderedDict)

    async def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    async def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if asizeof.asizeof(self.cache) > self.memory_limit:
            self._evict_if_needed()

    async def update(self, guild_id, **kwargs):
        allowed_kw = ["prefix", "channel_id", "toggled_modules"]
        if all(kw in allowed_kw for kw in kwargs):
            for key, value in kwargs.items():
                self.cache[guild_id][key] = value
            self.cache.move_to_end(guild_id)
            logger.info(f"Updated guild cache with {kwargs}.")
        else:
            raise ValueError("Invalid keyword arguments.")

    async def _evict_if_needed(self):
        while asizeof.asizeof(self.cache) > self.memory_limit:
            evicted_key, _ = self.cache.popitem(last=False)
            logger.info(f"Evicting {evicted_key} from guild cache to free up memory.")
    
    async def clear(self):
        self.cache.clear()
        logger.info("Cache cleared.")

guild_cache = LRUGuildCache(5000000) # 5MB, can hold up to 1k guilds.

async def get_guild_cache(guild_id):
    return await guild_cache.get(guild_id)

async def add_to_guild_cache(guild_id, guild_data):
    await guild_cache.put(guild_id, guild_data)
    logger.info(f"Added {guild_id} to guild cache.")

async def update_guild_cache(guild_id, guild_data, **kwargs):
    if guild_cache.get(guild_id) is None:
        await add_to_guild_cache(guild_id, guild_data)
    else:
        guild_cache.update(guild_id, **kwargs)
        logger.info(f"Updated {guild_id} in guild cache.")