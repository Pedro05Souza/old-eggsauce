"""
This file contains the cache for the bot. It is used to store data that is frequently accessed by the bot.
The cache is used to reduce the number of database queries and improve the bot's performance.
The cache is implemented as an LRU (Least Recently Used) cache, which evicts the least recently used items when the cache is full.
"""

from pympler import asizeof
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Union
import logging
import asyncio
import zlib
import pickle
logger = logging.getLogger('botcore')

@dataclass
class BotCache():
    memory_limit_bytes: int
    cache: OrderedDict = field(default_factory=OrderedDict)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

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
                compressed_value = self.cache[key]
                return {k: pickle.loads(zlib.decompress(v)) for k, v in compressed_value.items()}
            return None
    
    async def put(self, id: int, **kwargs) -> None:
        """
        Put a value in the cache.

        Args:
            id (int): The id to put the value for.
            **kwargs: The data to put in the cache.

        Returns:
            None
        """
        async with self.lock:
            if id not in self.cache:
                self.cache[id] = {}
            for key, value in kwargs.items():
                compressed_value = zlib.compress(pickle.dumps(value), level=9)
                self.cache[id][key] = compressed_value
            self.cache.move_to_end(id)
        if asizeof.asizeof(self.cache) > self.memory_limit_bytes:
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
            dict_value = self.cache.pop(key, None)
            if dict_value is None:
                logger.warning(f"Key {key} not found in cache.")
            else:
                logger.info(f"Deleted {key} from cache.")

    async def _evict_if_needed(self) -> None:
        """
        Evicts the least recently used item from the cache if the cache size exceeds the memory limit.

        Returns:
            None
        """
        async with self.lock:
            while asizeof.asizeof(self.cache) > self.memory_limit_bytes:
                evicted_key, _ = self.cache.popitem(last=False)
                logger.info(f"Evicting {evicted_key} cache to free up memory.")
    
    async def clear(self) -> None:
        self.cache.clear()