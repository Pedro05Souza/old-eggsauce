"""
This module contains the event listeners for the bot.
"""
import logging
from typing import Union
from discord.ext.commands import Context
from discord.interactions import Interaction
logger = logging.getLogger('botcore')

class ListenerManager():
    """
    This class manages the listeners data and stores the last listener called.
    """
    def __init__(self, user_id: int = None, specific_listener: str = None) -> None:
        """
        Initialize the listener manager.
        Params: user_id, specific_listener
        Where user_id specifies an user id that the listener manager will attempt to listen to.
        Where specific_listener specifies a specific listener that the listener manager is listening to.
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
        param: listener which is the listener that activated.
        param: args where args is a tuple of the listener arguments.
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
    """
    if flag not in {0, 1}: 
        raise ValueError("Flag parameter must be 0, 1 or 2.")
    await listener_manager.listener_result(on_user_transaction.__name__, ctx, quantity, flag)