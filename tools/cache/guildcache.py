from tools.cache.cache import BotCache
from pympler import asizeof


class GuildCache(BotCache):
    def __init__(self, memory_limit: int):
        super().__init__(memory_limit)

    async def get(self, key):
        return await super().get(key)

    async def put(self, key, **kwargs):
        allowed_kw = ["prefix", "channel_id", "toggled_modules"]
        if all(kw in allowed_kw for kw in kwargs):
            await super().put(key, **kwargs)
        else:
            raise ValueError("Invalid keyword arguments.")


    async def _evict_if_needed(self):
        await super()._evict_if_needed()

    async def clear(self):
        await super().clear()

    async def get_guild_cache_memory_consuption(self):
        return asizeof.asizeof(self.cache)