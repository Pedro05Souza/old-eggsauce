from temp import BotCache

__all__ = ['cache_initiator', 'cooldown_tracker', 'steal_status', 'message_cache']

cache_initiator = BotCache(8388608, 16777216)

cooldown_tracker = {}
steal_status = {}
message_cache = {}