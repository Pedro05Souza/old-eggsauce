from discord.ext.commands import Context
from discord.interactions import Interaction
from typing import Union
from lib import format_date
import logging
import random

logger = logging.getLogger('bot_logger')

__all__ = ['ListenerManager', 'listener_manager']

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
        self.store_last_listener_per_user = {}
        self.__user_id = user_id
        self.__specific_listener = specific_listener

    @property
    def user_id(self) -> Union[int, None]:
        return self.__user_id
    
    @property
    def specific_listener(self) -> Union[str, None]:
        return self.__specific_listener
    
    async def handle_adding_data(self, listener: str, ctx: Context, quantity: int, flag: int) -> None:
        """
        This function is called whenever an user is added to the listener manager.

        Args:
            listener (str): The name of the listener that was added.
            *args: The arguments passed to the listener.

        Returns:
            None
        """
        user_id = None
        if isinstance(ctx, Interaction):
            user_id = ctx.user.id
            
        else:
            user_id = ctx.author.id
        self.store_last_listener_per_user.setdefault(user_id, [])
        if len(self.store_last_listener_per_user[user_id]) < 5:
            self.store_last_listener_per_user[user_id].append(
                {
                    "listener": listener,
                    "context": ctx,
                    "spent": quantity,
                    "profit": flag
                }
            )
        else:
            self.store_last_listener_per_user[user_id].pop(0)
            self.store_last_listener_per_user[user_id].append(
                {
                    "listener": listener,
                    "context": ctx,
                    "spent": 0,
                    "profit": 0
                }
            )
    
    async def listener_result(self, listener: str, ctx: Context, quantity: int, flag: int) -> None:
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
        if self.user_id and ctx.author.id != self.user_id:
            return
        await self.handle_adding_data(listener, ctx, quantity, flag)

    async def clear_listeners(self) -> None:
        """
        This function is called whenever the listeners are cleared.

        Returns:
            None
        """
        if len(self.store_last_listener_per_user) > 0:
            self.store_last_listener_per_user.clear()
            logger.info("Listeners cleared.")

    async def get_last_listener(self, user_id: int) -> Union[dict, None]:
        """
        This function is called whenever the last listener is retrieved.

        Args:
            user_id (int): The id of the user.

        Returns:
            Union[dict, None]: The last listener of the user.
        """
        if not self.store_last_listener_per_user.get(user_id, None):
            return None
        return self.store_last_listener_per_user.get(user_id, None)[-1]
    
    async def get_n_last_listeners(self, user_id: int, n: int) -> Union[list, None]:
        """
        This function is called whenever the last n listeners are retrieved.

        Args:
            user_id (int): The id of the user.
            n (int): The number of listeners to retrieve.

        Returns:
            Union[list, None]: The last n listeners of the user.
        """
        if n > 5:
            raise ValueError("n must be less than 5")
        return self.store_last_listener_per_user.get(user_id, None)[:n]
    
    async def get_random_n_listeners(self, n: int) -> Union[list, None]:
        """
        This function is called whenever the random n listeners are retrieved.

        Args:
            n (int): The number of listeners to retrieve.

        Returns:
            Union[list, None]: The random n listeners.
        """
        if n > 5:
            raise ValueError("n must be less than 5")
        
        listeners = list(self.store_last_listener_per_user.values())

        if not listeners:
            return None

        if n > len(listeners):
            n = len(listeners)

        return random.sample(listeners, n)

    async def return_listener_description(self, listener: dict) -> str:
        """
        This function is called whenever the description of the listener is returned.

        Args:
            listener (dict): The listener to return the description for.

        Returns:
            str: The description of the listener.
        """
        return f"""
                    📢 **Listener name:** {listener['listener']}
                    👤 **User:** {listener['context'].author.name}
                    📝 **Command name:** {listener['context'].command.name}
                    🔢 **Quantity:** {listener['spent']}
                    💰 **Profit:** {"Yes" if listener['profit'] == 0 else "No"}
                    🕒 **Sent:** {await format_date(listener['context'].message.created_at)}
                    🏰 **Guild:** {listener['context'].guild}
                    """
    
listener_manager = ListenerManager()