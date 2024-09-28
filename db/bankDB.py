"""
This module contains the database functions for the bank collection.
"""
from db.dbsetup import mongo_client
from temp import cache_initiator
from typing import Union
import logging
bank_collection = mongo_client.BotDiscord.bank

logger = logging.getLogger('bot_logger')
__all__ = ['Bank']

class Bank:

    @staticmethod
    async def create(user_id: int, points: int, upgrades: int) -> None:
        """
        Creates a user in the database.

        Args:
            user_id (int): The id of the user to create.
            points (int): The amount of points to create the user with.

        Returns:
            None
        """
        try:
            user_data = await bank_collection.find_one({"user_id": user_id})
            if user_data:
                logger.warning(f"User {user_id} already exists.")
                return None
            else:
                user = {
                    "user_id": user_id,
                    "bank": points,
                    "upgrades": upgrades
                }
                logger.info(f"Creating user {user_id} with {points} points and {upgrades} upgrades.")
                await cache_initiator.put_user(user_id, bank_data=user)
                await bank_collection.insert_one(user)
                logger.info(f"User {user_id} has been created successfully.")
        except Exception as e:
            logger.error("Error encountered while creating the user.", e)
            return None
        
    @staticmethod
    async def delete(user_id: int) -> None:
        """
        Deletes a user from the bank collection.

        Args:
            user_id (int): The id of the user to delete.

        Returns:
            None
        """
        try:
            user_data = await bank_collection.find_one({"user_id": user_id})
            if user_data:
                await cache_initiator.delete(user_id)
                await bank_collection.delete_one({"user_id": user_id})
                logger.info("User has been deleted successfully.")
            else:
                logger.warning("User not found.")
        except Exception as e:
            logger.error("Error encountered while deleting the user.", e)
            return None
        
    @staticmethod
    async def update(user_id: int, points: int) -> None:
        """
        Updates a user in the database.

        Args:
            user_id (int): The id of the user to update.
            points (int): The amount of points to update the user with.
        """
        try:
            user_data = await bank_collection.find_one({"user_id": user_id})
            if user_data:
                user_data['bank'] = points
                await cache_initiator.put_user(user_id, bank_data=user_data)
                await bank_collection.update_one({"user_id": user_id}, {"$set": {"bank": points}})
                logger.info("User has been updated successfully.")
            else:
                logger.warning("User not found.")
        except Exception as e:
            logger.error("Error encountered while updating the user.", e)
            return None
        
    @staticmethod
    async def update_upgrades(user_id: int, upgrades: int) -> None:
        """
        Updates a user in the bank collection with upgrades.

        Args:
            user_id (int): The id of the user to update.
            upgrades (int): The amount of upgrades to update the user with.

        Returns:
            None
        """
        try:
            user_data = await bank_collection.find_one({"user_id": user_id})
            if user_data:
                user_data['upgrades'] = upgrades
                await cache_initiator.put_user(user_id, bank_data=user_data)
                await bank_collection.update_one({"user_id": user_id}, {"$set": {"upgrades": upgrades}})
                logger.info("User has been updated successfully.")
            else:
                logger.warning("User not found.")
        except Exception as e:
            logger.error("Error encountered while updating the user.", e)
            return None
        
    @staticmethod
    async def read(user_id: int) -> Union[dict, None]:
        """
        Reads a user from the bank collection.

        Args:
            user_id (int): The id of the user to read.

        Returns:
            dict | None
        """
        try:
            user_data = await bank_collection.find_one({"user_id": user_id})
            if user_data:
                return user_data
        except Exception as e:
            logger.error("Error encountered while trying to read the user.", e)
            return None