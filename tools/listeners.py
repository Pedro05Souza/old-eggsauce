"""
This module contains the event listeners for the bot.
"""
import logging
from typing import Union

logger = logging.getLogger('botcore')
class ListenerManager():
    """
    This class manages the listeners data and stores the last listener called.
    """
    def __init__(self, user_id = None, specific_listener = None) -> None:
        """
        Initialize the listener manager.
        Params: user_id, specific_listener
        Where user_id specifies an user id that the listener manager will attempt to listen to.
        Where specific_listener specifies a specific listener that the listener manager is listening to.
        """
        self.store_last_listener = {
            "on_user_transaction": [],
            "on_chicken_sold": [],
            "on_bank_transaction": [],
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
        params: listener, args where args is a tuple of the listener arguments.
        It stores the last listener called with its arguments.
        """
        if self.specific_listener and listener != self.specific_listener:
            return
        if self.user_id and args[0] != self.user_id:
            return
        logger.info(f"Listener {listener} activated with args {args}")
        self.store_last_listener[listener] = args

listener_manager = ListenerManager()

async def on_user_transaction(user_id: int, quantity: int, flag: int) -> None:
    """
    This function is called whenever a user transaction is executed.
    The flag parameter that indicates the context of the transaction.
    0 for gain
    1 for loss
    2 for not guaranteed if gain or loss
    """
    if flag not in {0, 1, 2}: 
        raise ValueError("Flag parameter must be 0, 1 or 2.")
    await listener_manager.listener_result(on_user_transaction.__name__, user_id, quantity, flag)

async def on_chicken_sold(user_id: int) -> None:
    """
    This function is called whenever a chicken is sold to the market.
    """
    await listener_manager.listener_result(on_chicken_sold.__name__, user_id)

async def on_bank_transaction(user_id: int, quantity: int, flag: int) -> None:
    """
    This function is called whenever a bank transaction is executed.
    The flag parameter that indicates the context of the transaction.
    0 for withdrawal
    1 for deposit
    """
    if flag not in {0, 1}: 
        raise ValueError("Flag parameter must be 0 or 1.")
    await listener_manager.listener_result(on_bank_transaction.__name__, user_id, quantity, flag)