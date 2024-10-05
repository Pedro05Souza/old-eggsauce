"""
This module contains the event listeners for the bot.
"""
from discord.ext.commands import Context
from discord.interactions import Interaction
from tools.listener_manager import listener_manager
from tools.shared_state import get_shared_event

__all__ = ['on_user_transaction', 'on_awaitable']

async def on_user_transaction(ctx: Context | Interaction , quantity: int, flag: int) -> None:
    """
    This function is called whenever an user transaction is executed.
    The flag parameter that indicates the context of the transaction.
    It receives the context of the command, the quantity of the transaction and the flag which is:
    0 for gain
    1 for loss

    Args:
        ctx (Context): The context of the command.
        quantity (int): The quantity of the transaction.
        flag (int): The flag of the transaction.

    Returns:
        None
    """
    if flag not in {0, 1}: 
        raise ValueError("Flag parameter must be 0 or 1")
    await listener_manager.listener_result(on_user_transaction.__name__, ctx, quantity, flag)

async def on_awaitable(author_id: int, user_id: int = None) -> None:
    """
    This function is called whenever an awaitable event is executed.

    Args:
        author_id (int): The id of the author.
        user_id (int): The id of the user.

    Returns:
        None
    """
    event_author = await get_shared_event(author_id)
    event_author.set()
    if user_id:
        event_user = await get_shared_event(user_id)
        event_user.set()