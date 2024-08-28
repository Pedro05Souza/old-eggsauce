from db.dbConfig import mongo_client
from tools.cache import cache_initiator
from tools.shared import update_scheduler, request_threading
from typing import Union
import logging
bank_collection = mongo_client.db.bank
logger = logging.getLogger('botcore')

class Bank:

    @staticmethod
    def create(user_id: int, points: int) -> None:
        """Create a user in the database."""
        try:
            user_data = request_threading(lambda: bank_collection.find_one({"user_id": user_id})).result()
            if user_data:
                logger.warning(f"User {user_id} already exists.")
                return None
            else:
                if not isinstance(points, int):
                    points = 0
                user = {
                    "user_id": user_id,
                    "bank": points,
                    "upgrades": 1,
                    #"credit_score": 0
                }
                update_scheduler(lambda: cache_initiator.add_to_user_cache(user_id, bank_data=user))
                request_threading(lambda: bank_collection.insert_one(user)).result()
                logger.info(f"User {user_id} has been created successfully.")
        except Exception as e:
            logger.error("Error encountered while creating the user.", e)
            return None
        
    @staticmethod
    def delete(user_id: int) -> None:
        """Delete a user from the database."""
        try:
            user_data = request_threading(lambda: bank_collection.find_one({"user_id": user_id})).result()
            if user_data:
                update_scheduler(lambda: cache_initiator.delete_user_cache(user_id))
                request_threading(lambda: bank_collection.delete_one({"user_id": user_id})).result()
                logger.info("User has been deleted successfully.")
            else:
                logger.warning("User not found.")
        except Exception as e:
            logger.error("Error encountered while deleting the user.", e)
            return None
        
    @staticmethod
    def update(user_id: int, points: int) -> None:
        """Update a user in the database."""
        try:
            user_data = request_threading(lambda: bank_collection.find_one({"user_id": user_id})).result()
            if user_data:
                user_data['bank'] = points
                update_scheduler(lambda: cache_initiator.update_user_cache(user_id, bank_data=user_data))
                request_threading(lambda: bank_collection.update_one({"user_id": user_id}, {"$set": {"bank": points}})).result()
                logger.info("User has been updated successfully.")
            else:
                logger.warning("User not found.")
        except Exception as e:
            logger.error("Error encountered while updating the user.", e)
            return None
        
    @staticmethod
    def update_upgrades(user_id: int, upgrades: int) -> None:
        """Update a user in the database."""
        try:
            user_data = request_threading(lambda: bank_collection.find_one({"user_id": user_id})).result()
            if user_data:
                user_data['upgrades'] = upgrades
                update_scheduler(lambda: cache_initiator.update_user_cache(user_id, bank_data=user_data))
                request_threading(lambda: bank_collection.update_one({"user_id": user_id}, {"$set": {"upgrades": upgrades}})).result()
                logger.info("User has been updated successfully.")
            else:
                logger.warning("User not found.")
        except Exception as e:
            logger.error("Error encountered while updating the user.", e)
            return None
        
    @staticmethod
    def read(user_id: int) -> Union[dict, None]:
        """Read a user from the database."""
        try:
            user_data = request_threading(lambda: bank_collection.find_one({"user_id": user_id})).result()
            if user_data:
                return user_data
        except Exception as e:
            logger.error("Error encountered while trying to read the user.", e)
            return None
        
    @staticmethod
    def read_highest_10_bank() -> Union[dict, None]:
        """Read a user from the database."""
        try:
            user_data = request_threading(lambda: bank_collection.find().sort("bank", -1).limit(10)).result()
            if user_data:
                return user_data
        except Exception as e:
            logger.error("Error encountered while trying to read the user.", e)
    
    @staticmethod
    def readAll() -> Union[dict, None]:
        """Read all users from the database."""
        try:
            user_data = request_threading(lambda: bank_collection.find()).result()
            if user_data:
                return user_data
        except Exception as e:
            logger.error("Error encountered while trying to read all users.", e)
            return None