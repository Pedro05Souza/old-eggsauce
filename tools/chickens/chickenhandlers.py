"""
This module contains a handler that stops any player in participating in an event if they are already in one.
Also, it contains a handler that limits the amount of rolls a player can do in a certain time frame.
"""
from contextlib import asynccontextmanager
from discord.ext.commands import Context
from tools.chickens.shared_state import get_shared_event
from lib.shared import send_bot_embed
import asyncio
import discord
import logging

logger = logging.getLogger('bot_logger')
    
class RollLimit:
    obj_list = {}

    @classmethod
    def read(cls, user_id: int) -> object:
        """
        Checks if a user is in the current object list.

        Args:
            user_id (int): The id of the user to read.

        Returns:
            object
        """
        return cls.obj_list.get(user_id)
    

    @classmethod
    def read_key(cls, key: int) -> bool:
        """
        Reads the current object for a user.

        Args:
            key (int): The key to read.

        Returns:
            bool
        """
        if key in cls.obj_list.keys():
            return True
        return False

    @classmethod
    def remove(cls, user_id: int) -> None:
        """
        Removes a user from the object list.

        Args:
            user_id (int): The id of the user to remove.
        
        Returns:
            None
        """
        try:
            cls.obj_list.pop(user_id)
        except Exception as e:
            logger.error("Error removing object from list.", e)
    
    @classmethod
    def update(cls, user_id: int, current: int) -> None:
        """
        Updates the current object for a user.

        Args:
            user_id (int): The id of the user to update.
            current (int): The current object to update with.

        Returns:    
            None
        """
        obj = cls.obj_list.get(user_id)
        if obj:
            cls.obj_list[user_id] = current
        else:
            cls.obj_list[user_id] = current

    @classmethod
    def create(cls, user_id: int, current: int) -> None:
        """
        Creates an object for a user.

        Args:
            user_id (int): The id of the user to create the object for.
            current (int): The current object to create.

        Returns:
            None
        """
        cls.obj_list[user_id] = current

    @classmethod
    def remove_all(cls) -> None:
        """
        Removes all objects from the list.

        Returns:
            None
        """
        cls.obj_list.clear()

class EventData():
    event_users = {}

    @staticmethod
    async def check_user_in_event(author_id: int, optional_user: int = None) -> bool:
        """
        Check if a user is in an active event.

        Args:
            user_id (int): The id of the user to check.
            optional_user (int): An optional user to check against.
        
        Returns:
            bool
        """
        if author_id in EventData.event_users or (optional_user and optional_user in EventData.event_users):
            return True
        return False
        
    @asynccontextmanager
    @staticmethod
    async def manage_event_context(author: discord.Member, optional_user: discord.Member = None, awaitable: bool = False):
        """
        Context manager for handling user events.

        Args:
            ctx (Context): The context of the command.
            author (discord.Member): The author of the command.
            optional_user (discord.Member): An optional user to check against.
            awaitable (bool): flag to determine if the event is awaitable. (If the context manager should wait for the event to finish.)

        Returns:
            None
        """
        try:
            EventData.event_users[author.id] = author

            if optional_user:
                EventData.event_users[optional_user.id] = optional_user 

            yield

            if awaitable:
                await EventData.awaitable_handler(author, optional_user)
        finally:
            EventData.event_users.pop(author.id)
            if optional_user:
                EventData.event_users.pop(optional_user.id)

    @staticmethod
    async def awaitable_handler(author: discord.Member, optional_user: discord.Member = None):
        """
        Handles awaitable events.

        Args:
            ctx (Context): The context of the command.
            author (discord.Member): The author of the command.
            optional_user (discord.Member): An optional user to check against.

        Returns:
            None
        """
        event_author = await get_shared_event(author.id)
        event_user = await get_shared_event(optional_user.id) if optional_user else None

        try:
            await asyncio.wait_for(event_author.wait(), timeout=120)
            if optional_user:
                await asyncio.wait_for(event_user.wait(), timeout=120)
        except asyncio.TimeoutError:
            return
        
    @staticmethod
    async def is_yieldable(ctx: Context, author: discord.Member, optional_user: discord.Member = None) -> bool:
        """
        Check if the context manager is yieldable given the current context.

        Returns:
            bool
        """
        if await EventData.check_user_in_event(author.id, optional_user):
            await send_bot_embed(ctx, description=":no_entry_sign: You are already in an event. Please wait for it to finish.")
            return False
        return True