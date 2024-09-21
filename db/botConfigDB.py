"""
This module contains the class BotConfig which is responsible for creating, updating, deleting, and reading server configurations from the database.
"""
from db.dbsetup import mongo_client
from tools.cache import cache_initiator
from typing import Union
import logging
config_collection = mongo_client.BotDiscord.botcfg
logger = logging.getLogger('botcore')


class BotConfig:

    @staticmethod
    async def create(server_id: int, toggled_modules: list = None, channel_id: int = None, prefix: str = None) -> None:
        """
        Creates a server in the bot config collection.

        Args:
            server_id (int): The id of the server to create.
            toggled_modules (list): The modules to toggle.
            channel_id (int): The id of the channel to create.
            prefix (str): The prefix to create.

        Returns:
            None
        """
        try:
            toggle_data = await config_collection.find_one({"server_id": server_id})
            if toggle_data:
                logger.warning("This server already exists.")
                return None
            else:
                toggle = {
                    "server_id": server_id,
                    "toggled_modules": toggled_modules,
                    "channel_id": channel_id,
                    "prefix": prefix,
                }
                await cache_initiator.put_guild(server_id, prefix="!", toggled_modules=toggled_modules, channel_id=channel_id)
                await config_collection.insert_one(toggle)
                logger.info("Server created successfully.")
        except Exception as e:
            logger.error("Error encountered while creating a server.", e)
            return None
        
    @staticmethod
    async def create_toggle(server_id: int, toggled_modules: list) -> None:
        """
        Creates a toggle in the bot config collection.

        Args:
            server_id (int): The id of the server to create.
            toggled_modules (list): The modules to toggle.

        Returns:
            None
        """
        try:
            toggle_data = await config_collection.find_one({"server_id": server_id})
            if toggle_data:
                logger.warning("This toggle already exists.")
                return None
            else:
                toggle = {
                    "server_id": server_id,
                    "toggle_modules": toggled_modules,
                }
                await config_collection.insert_one(toggle)
                await cache_initiator.put_guild(server_id, toggled_modules=toggled_modules)
                logger.info("Toggle created successfully.")
        except Exception as e:
            logger.error("Error encountered while creating a toggle.", e)
            return None
        
    @staticmethod
    async def create_channel(server_id: int, channel_id: int) -> None:
        """
        Creates a channel in the bot config collection.

        Args:
            server_id (int): The id of the server to create.
            channel_id (int): The id of the channel to create.

        Returns:
            None
        """
        try:
            toggle_data = await config_collection.find_one({"server_id": server_id})
            if toggle_data:
                logger.warning("This channel already exists.")
                return None
            else:
                toggle = {
                    "server_id": server_id,
                    "channel_id": channel_id,
                }
                await config_collection.insert_one(toggle)
                await cache_initiator.put_guild(server_id, channel_id=channel_id)
                logger.info("Channel created successfully.")
        except Exception as e:
            logger.error("Error encountered while creating a channel.", e)
            return
        
    @staticmethod
    async def create_prefix(server_id: int, prefix: str) -> None:
        """
        Creates a prefix in the bot config collection.

        Args:
            server_id (int): The id of the server to create.
            prefix (str): The prefix to create.

        Returns:
            None
        """
        try:
            prefix_data = await config_collection.find_one({"server_id": server_id})
            if prefix_data:
                logger.warning("This prefix already exists.")
                return None
            else:
                prefix = {
                    "server_id": server_id,
                    "prefix": prefix,
                }
                await config_collection.insert_one(prefix)
                await cache_initiator.put_guild(server_id, prefix=prefix)
                logger.info("Prefix created successfully.")
        except Exception as e:
            logger.error("Error encountered while creating a prefix.", e)
            return None
        
    @staticmethod
    async def update_prefix(server_id: int, prefix: str) -> None:
        """
        Update a prefix in the bot config collection.

        Args:
            server_id (int): The id of the server to update.
            prefix (str): The prefix to update.

        Returns:
            None
        """
        try:
            prefix_data = await config_collection.find_one({"server_id": server_id})
            if prefix_data:
                await config_collection.update_one({"server_id": server_id}, {"$set": {"prefix": prefix}})
                await cache_initiator.put_guild(server_id, prefix=prefix)
                logger.info(f"Prefix updated for server {server_id}.")
            else:
                logger.warning("Prefix not found.")
        except Exception as e:
            logger.error("Error encountered while updating a prefix.", e)
        
    @staticmethod
    async def update_toggled_modules(server_id: int, toggled_modules: list) -> None:
        """
        Update a toggle in the database.

        Args:
            server_id (int): The id of the server to update.
            toggled_modules (list): The modules to toggle.

        Returns:
            None
        """
        try:
            toggle_data = await config_collection.find_one({"server_id": server_id})
            if toggle_data:
                await config_collection.update_one({"server_id": server_id}, {"$set": {"toggled_modules": toggled_modules}})
                await cache_initiator.put_guild(server_id, toggled_modules=toggled_modules)
                logger.info("Toggle updated successfully.")
            else:
                logger.warning("Toggle not found.")
        except Exception as e:
            logger.error("Error encountered while updating a toggle.", e)
    
    @staticmethod
    async def update_channel_id(server_id: int, channel_id: int) -> None: 
        """
        Updates a channel in the database.

        Args:
            server_id (int): The id of the server to update.
            channel_id (int): The id of the channel to update.

        Returns:
            None
        """
        try:
            toggle_data = await config_collection.find_one({"server_id": server_id})
            if toggle_data:
                await config_collection.update_one({"server_id": toggle_data["server_id"]}, {"$set": {"channel_id": channel_id}})
                await cache_initiator.put_guild(server_id, channel_id=channel_id)
                logger.info("Channel updated successfully.")
            else:
                logger.warning("Channel not found.")
        except Exception as e:
            logger.error("Error encountered while updating a channel.", e)
        
    @staticmethod
    async def delete(server_id: int) -> None:
        """
        Deletes a toggle from the database.

        Args:
            server_id (int): The id of the server to delete.

        Returns:
            None
        """
        try:
            config_data = await config_collection.find_one({"server_id": server_id})
            if config_data:
                await config_collection.delete_one({"server_id" : server_id})
                await cache_initiator.delete(server_id)
                logger.info("Server deleted successfully.")
            else:
                logger.warning("Server not found.")
        except Exception as e:
                logger.error("Error encountered while deleting a server.", e)
    
    @staticmethod
    async def read(server_id: int) -> Union[dict, None]:
        """
        Reads a server from the database.

        Args:
            server_id (int): The id of the server to read.
        """
        try:
            config_data = await config_collection.find_one({"server_id": server_id})
            if config_data:
                return config_data
            else:
                await BotConfig.create(server_id)
                config_data = await config_collection.find_one({"server_id": server_id})
                return config_data
        except Exception as e:
            logger.error("Error encountered while reading a server.", e)
            return None