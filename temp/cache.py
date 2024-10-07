"""
This file contains the cache for the bot. It is used to store data that is frequently accessed by the bot.
The cache is used to reduce the number of database queries and improve the bot's performance.
The cache is implemented as an LRU (Least Recently Used) cache, which evicts the least recently used items when the cache is full.
"""
from pympler import asizeof
from collections import OrderedDict
from dataclasses import dataclass, field
from asyncio import Lock
from typing import Union
from logs import log_info, log_warning

__all__ = ["BotCache"]

@dataclass
class BotCache():
    memory_limit_bytes_guild: int
    memory_limit_bytes_user: int
    cache: OrderedDict = field(default_factory=OrderedDict)
    lock: Lock = field(default_factory=Lock)

    async def get(self, key: str) -> Union[dict, None]:
        """
        Get a value from the cache.

        Args:
            key (str): The key to get the value for.

        Returns:
            Union[dict, None]
        """
        async with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    async def put_cache(self, identifier: int, **kwargs) -> None:
        """
        Put a value in the cache.

        Args:
            identifier (int): The id to put the value for.
            **kwargs: The data to put in the cache.

        Returns:
            None
        """
        async with self.lock:

            if identifier not in self.cache:
                self.cache[identifier] = {}
 
            for dict_key, value in kwargs.items():

                if dict_key in self.cache[identifier]:
                    if isinstance(value, dict):
                        self.cache[identifier][dict_key].update(value)
                    else:
                        self.cache[identifier][dict_key] = value
                else:
                    self.cache[identifier][dict_key] = value

            self.cache.move_to_end(identifier)
            
        if asizeof.asizeof(self.cache) > self.memory_limit_bytes_guild + self.memory_limit_bytes_user:
            await self._evict_if_needed()
        
    async def delete(self, key: str) -> None:
        """
        Deletes a value from the cache.

        Args:
            key (str): The key to delete the value for.

        Returns:
            None
        """
        async with self.lock:
            if key in self.cache:
                del self.cache[key]

    async def _evict_if_needed(self) -> None:
        """
        Evicts the least recently used item from the cache if the cache size exceeds the memory limit.

        Returns:
            None
        """
        async with self.lock:
            while asizeof.asizeof(self.cache) > self.memory_limit_bytes_guild + self.memory_limit_bytes_user:
                evicted_key, _ = self.cache.popitem(last=False)
                log_warning(f"Evicting {evicted_key} cache to free up memory.")

    async def put_guild(self, key: int, **kwargs) -> None:
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
            await self.put_cache(key, **kwargs)
        else:
            raise ValueError("Invalid keyword arguments.")
            
    async def clear_cache_periodically(self) -> None:
        """
        Periodically clears the cache.

        Returns:
            None
        """
        if len(self.cache) > 0:
            self.cache.clear()
            log_info("Cache has been cleared.")

    async def put_user(self, key: int, **kwargs) -> None:
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
            await self.put_cache(key, **kwargs)
        else:
            raise ValueError("Invalid keyword arguments.")
            
    async def get_cache_memory_consuption(self) -> int:
        """
        Gets the memory consumption of the cache.

        Returns:
            int
        """
        return asizeof.asizeof(self.cache)