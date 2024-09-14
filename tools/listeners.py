"""
This module contains the event listeners for the bot.
"""
from typing import Union
from discord.ext.commands import Context
from discord.interactions import Interaction
import logging
logger = logging.getLogger('botcore')

class ListenerManager():

    def __init__(self, user_id: int = None, specific_listener: str = None) -> None:
        """
        Initialize the listener manager.
        Args:
            user_id (int): specifies an user id that the listener manager will attempt to listen to.
            specific_listener (str): specifies a specific listener that the listener manager is listening to.

        Returns:
            None
        """
        self.store_last_listener = {
            "on_user_transaction": [],
        }
        self.__user_id = user_id
        self.__specific_listener = specific_listener

    @property
    def user_id(self) -> Union[int, None]:
        return self.__user_id
    
    @property
    def specific_listener(self) -> Union[str, None]:
        return self.__specific_listener
    
    async def listener_result(self, listener: str, *args) -> None:
        """
        This function is called whenever a listener is executed.

        Args:
            listener (str): The name of the listener that was called.
            *args: The arguments passed to the listener.

        Returns:
            None
        """
        if self.specific_listener and listener != self.specific_listener:
            return
        if self.user_id and args[0].author.id != self.user_id:
            return
        self.store_last_listener[listener] = args

listener_manager = ListenerManager()

async def on_user_transaction(ctx: Context | Interaction , quantity: int, flag: int) -> None:
    """
    This function is called whenever a user transaction is executed.
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
        raise ValueError("Flag parameter must be 0, 1 or 2.")
    await listener_manager.listener_result(on_user_transaction.__name__, ctx, quantity, flag)