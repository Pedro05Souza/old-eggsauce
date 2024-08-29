from tools.cache.guildcache import GuildCache
from tools.cache.usercache import UserCache
from typing import Union
import logging

logger = logging.getLogger('botcore')


class CacheInitiator:

    def __init__(self, memory_limit_user: int, memory_limit_guild: int):
        self.user_cache = UserCache(memory_limit_user)
        self.guild_cache = GuildCache(memory_limit_guild)

    async def start_cache_clearing_for_users(self) -> None:
        """
        Periodically clear the user cache.
        """
        await self.user_cache.clear_users_cache_periondically(1800) # 30 minutes
        
    async def get_user_cache(self, user_id: int) -> Union[dict, None]:
        """
        Get the user cache.
        """
        return await self.user_cache.get(user_id)

    async def add_to_user_cache(self, user_id: int, **kwargs) -> None:
        """
        Add to the user cache.
        """
        await self.user_cache.put(user_id, **kwargs)

    async def update_user_cache(self, user_id: int, **kwargs) -> None:
        """
        Update the user cache.
        """
        if not await self.user_cache.get(user_id):
            await self.add_to_user_cache(user_id, **kwargs)
        else:
            await self.user_cache.put(user_id, **kwargs)

    async def delete_from_user_cache(self, user_id: int) -> None:
        """
        Delete the user cache.
        """
        await self.user_cache.delete(user_id)

    async def delete_user_cache(self, user_id: int) -> None:
        """
        Delete the user cache
        """
        await self.delete_from_user_cache(user_id)

    async def get_guild_cache(self, guild_id: int) -> Union[dict, None]:
        """
        Get the guild cache.
        """
        return await self.guild_cache.get(guild_id)

    async def add_to_guild_cache(self, guild_id: int, **kwargs) -> None:
        """
        Add to the guild cache.
        """
        await self.guild_cache.put(guild_id, **kwargs)

    async def update_guild_cache(self, guild_id: int, **kwargs) -> None:
        """
        Update the guild cache.
        """
        if await self.guild_cache.get(guild_id) is None:
            await self.add_to_guild_cache(guild_id, **kwargs)
        else:
            await self.guild_cache.put(guild_id, **kwargs)

    async def remove_from_guild_cache(self, guild_id: int) -> None:
        """
        Remove the guild cache.
        """
        await self.guild_cache.delete(guild_id)

    async def get_memory_usage(self) -> tuple:
        """
        Get the memory usage.
        """
        return await self.user_cache.get_user_cache_memory_consuption(), await self.guild_cache.get_guild_cache_memory_consuption()
    
    async def start_cache_clearing_for_guilds(self) -> None:
        """
        Periodically clear the guild cache.
        """
        await self.guild_cache.clear_guild_cache_periodically(1800)  # 30 minutes
    
cache_initiator = CacheInitiator(16777216, 8388608)  # 16MB, 8MB # can hold up to 7.8k guilds and 1.6k users

