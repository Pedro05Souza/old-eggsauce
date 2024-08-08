# This file contains the cache for the bot. It is used to store data that is frequently accessed by the bot.
# The cache is used to reduce the number of database queries and improve the bot's performance.

guild_cache = {}

async def modify_guild_cache(server_id, **kwargs):
    allowed_kw = ["prefix", "channel_id", "toggled_modules"]
    if all(kw in allowed_kw for kw in kwargs.keys()):
        guild_cache[server_id].update(kwargs)
        return True
    raise ValueError("Invalid keyword argument.")

async def add_to_guild_cache(server_id, server_data):
    guild_cache[server_id] = server_data
    return True

async def get_guild_cache(server_id):
    return guild_cache.get(server_id, None)
