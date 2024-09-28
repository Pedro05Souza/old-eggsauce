import asyncio

shared_events = {}

__all__ = ['get_shared_event']

async def get_shared_event(user_id: int) -> asyncio.Event:
    """
    Get a shared event.
    
    Args:
        user_id (int): The id of the user.
    
    Returns:
        asyncio.Event
    """
    if not shared_events.get(user_id):
        shared_events[user_id] = asyncio.Event()
    return shared_events[user_id]