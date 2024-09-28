from temp.cache import BotCache

__all__ = ['cache_initiator']

cache_initiator = BotCache(8388608, 16777216)