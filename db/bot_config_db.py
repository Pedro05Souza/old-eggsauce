"""
This module contains the database functions for the bot config collection.
"""
from db.db_setup import mongo_client
from temp import cache_initiator
from typing import Union
from logs import log_info, log_warning, log_error
config_collection = mongo_client.BotDiscord.botcfg

__all__ = ['BotConfig']

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
                log_warning(f"This server {server_id} already exists.")
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
                log_info(f"Server {server_id} created successfully.")
        except Exception as e:
            log_error(f"Error encountered while creating a server {server_id}.", e)
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
                log_warning(f"This toggle already exists for server {server_id}.")
                return None
            else:
                toggle = {
                    "server_id": server_id,
                    "toggle_modules": toggled_modules,
                }
                await config_collection.insert_one(toggle)
                await cache_initiator.put_guild(server_id, toggled_modules=toggled_modules)
                log_info(f"Toggle sucessfully created for server {server_id}.")
        except Exception as e:
            log_error(f"Error encountered while creating a toggle for server {server_id}.", e)
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
                log_warning(f"This channel already exists for server {server_id}.")
                return None
            else:
                toggle = {
                    "server_id": server_id,
                    "channel_id": channel_id,
                }
                await config_collection.insert_one(toggle)
                await cache_initiator.put_guild(server_id, channel_id=channel_id)
                log_info(f"Channel created successfully for server {server_id}.")
        except Exception as e:
            log_error(f"Error encountered while creating a channel for server {server_id}.", e)
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
                log_warning(f"This prefix already exists for server {server_id}.")
                return None
            else:
                prefix = {
                    "server_id": server_id,
                    "prefix": prefix,
                }
                await config_collection.insert_one(prefix)
                await cache_initiator.put_guild(server_id, prefix=prefix)
                log_info(f"Prefix created successfully for server {server_id}.")
        except Exception as e:
            log_error(f"Error encountered while creating a prefix for server {server_id}.", e)
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
                prefix_data["prefix"] = prefix
                await config_collection.update_one({"server_id": server_id}, {"$set": {"prefix": prefix}})
                await cache_initiator.put_guild(server_id, prefix=prefix_data['prefix'])
                log_info(f"Prefix updated for server {server_id}.")
            else:
                log_warning(f"Prefix not found for server {server_id}.")
        except Exception as e:
            log_error(f"Error encountered while updating a prefix for server {server_id}.", e)
        
    @staticmethod
    async def update_toggled_modules(server_id: int, toggled_modules: str) -> None:
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
                toggle_data["toggled_modules"] = toggled_modules
                await config_collection.update_one({"server_id": server_id}, {"$set": {"toggled_modules": toggled_modules}})
                await cache_initiator.put_guild(server_id, toggled_modules=toggle_data['toggled_modules'])
                log_info(f"Toggle updated successfully for server {server_id}.")
            else:
                log_warning(f"Toggle not found for server {server_id}.")
                
        except Exception as e:
            log_error(f"Error encountered while updating a toggle for server {server_id}.", e)
    
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
                log_info(f"Channel updated successfully for server {server_id}.")
            else:
                log_warning(f"Channel not found for server {server_id}.")
        except Exception as e:
            log_error(f"Error encountered while updating a channel for server {server_id}.", e)
        
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
                log_info(f"Server deleted successfully for server {server_id}.")
            else:
                log_warning(f"Server not found for server {server_id}.")
        except Exception as e:
                log_error(f"Error encountered while deleting a server {server_id}.", e)
    
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
            log_error(f"Error encountered while reading a server {server_id}.", e)
            return None