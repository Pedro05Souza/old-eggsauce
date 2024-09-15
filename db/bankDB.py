"""
This module contains the database functions for the bank collection.
"""

from db.dbsetup import mongo_client
from tools.cache import cache_initiator
from tools.shared import update_scheduler, request_threading
from typing import Union
import logging
bank_collection = mongo_client.BotDiscord.bank
logger = logging.getLogger('botcore')

class Bank:

    @staticmethod
    def create(user_id: int, points: int, upgrades: int) -> None:
        """
        Creates a user in the database.

        Args:
            user_id (int): The id of the user to create.
            points (int): The amount of points to create the user with.

        Returns:
            None
        """
        try:
            user_data = request_threading(lambda: bank_collection.find_one({"user_id": user_id})).result()
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
                update_scheduler(lambda: cache_initiator.add_to_user_cache(user_id, bank_data=user))
                request_threading(lambda: bank_collection.insert_one(user), user_id).result()
                logger.info(f"User {user_id} has been created successfully.")
        except Exception as e:
            logger.error("Error encountered while creating the user.", e)
            return None
        
    @staticmethod
    def delete(user_id: int) -> None:
        """
        Deletes a user from the bank collection.

        Args:
            user_id (int): The id of the user to delete.

        Returns:
            None
        """
        try:
            user_data = request_threading(lambda: bank_collection.find_one({"user_id": user_id})).result()
            if user_data:
                update_scheduler(lambda: cache_initiator.delete_from_user_cache(user_id))
                request_threading(lambda: bank_collection.delete_one({"user_id": user_id}), user_id).result()
                logger.info("User has been deleted successfully.")
            else:
                logger.warning("User not found.")
        except Exception as e:
            logger.error("Error encountered while deleting the user.", e)
            return None
        
    @staticmethod
    def update(user_id: int, points: int) -> None:
        """
        Updates a user in the database.

        Args:
            user_id (int): The id of the user to update.
            points (int): The amount of points to update the user with.
        """
        try:
            user_data = request_threading(lambda: bank_collection.find_one({"user_id": user_id})).result()
            if user_data:
                user_data['bank'] = points
                update_scheduler(lambda: cache_initiator.update_user_cache(user_id, bank_data=user_data))
                request_threading(lambda: bank_collection.update_one({"user_id": user_id}, {"$set": {"bank": points}}), user_id).result()
                logger.info("User has been updated successfully.")
            else:
                logger.warning("User not found.")
        except Exception as e:
            logger.error("Error encountered while updating the user.", e)
            return None
        
    @staticmethod
    def update_upgrades(user_id: int, upgrades: int) -> None:
        """
        Updates a user in the bank collection with upgrades.

        Args:
            user_id (int): The id of the user to update.
            upgrades (int): The amount of upgrades to update the user with.

        Returns:
            None
        """
        try:
            user_data = request_threading(lambda: bank_collection.find_one({"user_id": user_id})).result()
            if user_data:
                user_data['upgrades'] = upgrades
                update_scheduler(lambda: cache_initiator.update_user_cache(user_id, bank_data=user_data))
                request_threading(lambda: bank_collection.update_one({"user_id": user_id}, {"$set": {"upgrades": upgrades}}), user_id).result()
                logger.info("User has been updated successfully.")
            else:
                logger.warning("User not found.")
        except Exception as e:
            logger.error("Error encountered while updating the user.", e)
            return None
        
    @staticmethod
    def read(user_id: int) -> Union[dict, None]:
        """
        Reads a user from the bank collection.

        Args:
            user_id (int): The id of the user to read.

        Returns:
            dict | None
        """
        try:
            user_data = request_threading(lambda: bank_collection.find_one({"user_id": user_id})).result()
            if user_data:
                return user_data
        except Exception as e:
            logger.error("Error encountered while trying to read the user.", e)
            return None