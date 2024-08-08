# This file contains the cache for the bot. It is used to store data that is frequently accessed by the bot.
# The cache is used to reduce the number of database queries and improve the bot's performance.

from sys import getsizeof
from collections import OrderedDict
import logging
logger = logging.getLogger('botcore')

class LRUGuildCache():

    def __init__(self, memory_limit):
        self.cache = OrderedDict()
        self.memory_limit = memory_limit

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if getsizeof(self.cache) > self.memory_limit:
            self._evict_if_needed()

    def update(self, guild_id, **kwargs):
        allowed_kw = ["prefix", "channel_id", "toggled_modules"]
        if all(kw in allowed_kw for kw in kwargs):
            for key, value in kwargs.items():
                self.cache[guild_id][key] = value
            logger.info(f"Updated guild cache with {kwargs}.")
        else:
            raise ValueError("Invalid keyword arguments.")

    def _evict_if_needed(self):
        while getsizeof(self.cache) > self.memory_limit:
            evicted_key, _ = self.cache.popitem(last=False)
            logger.info(f"Evicting {evicted_key} from guild cache to free up memory.")
    
    def clear(self):
        self.cache.clear()
        logger.info("Cache cleared.")

guild_cache = LRUGuildCache(1000000) # can hold up to 1MB of data, equivalent to 62.5k guilds

def get_guild_cache(guild_id):
    return guild_cache.get(guild_id)

def add_to_guild_cache(guild_id, guild_data):
    guild_cache.put(guild_id, guild_data)
    logger.info(f"Added {guild_id} to guild cache.")

def update_guild_cache(guild_id, guild_data, **kwargs):
    if guild_cache.get(guild_id) is None:
        add_to_guild_cache(guild_id, guild_data)
    else:
        guild_cache.update(guild_id, **kwargs)
        logger.info(f"Updated {guild_id} in guild cache.")

        
