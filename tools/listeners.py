"""
This module contains the event listeners for the bot.
"""

class ListenerManager():
    """
    This class manages the listeners and stores the last listener called.
    """
    def __init__(self):
        self.store_last_listener = {
            on_user_transaction.__name__: [],
            on_chicken_sold.__name__: [],
            on_bank_transaction.__name__: [],
            on_market_transaction.__name__: []
        }
    
    async def listener_result(self, listener: str, *args) -> None:
        """
        This function is called whenever a listener is executed.
        params: listener, args where args is a tuple of the listener arguments.
        It stores the last listener called with its arguments.
        """
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

async def on_bank_transaction(user_id: int, command: str) -> None:
    """
    This function is called whenever a bank transaction is executed.
    """
    await listener_manager.listener_result(on_bank_transaction.__name__, user_id, command)

async def on_market_transaction(user_id: int, chicken_rarity_type: str) -> None:
    """
    This function is called whenever a player buys a chicken from the market.
    """
    await listener_manager.listener_result(on_market_transaction.__name__, user_id, chicken_rarity_type)



