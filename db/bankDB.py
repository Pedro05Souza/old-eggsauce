from db.dbConfig import mongo_client
import logging
bank_collection = mongo_client.db.bank
logger = logging.getLogger('botcore')

class Bank:
    @staticmethod
    def create(user_id: int, points: int):
        """Create a user in the database."""
        try:
            user_data = bank_collection.find_one({"user_id": user_id})
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
                bank_collection.insert_one(user)
                logger.info(f"User {user_id} has been created successfully.")
        except Exception as e:
            logger.error("Error encountered while creating the user.", e)
            return None
        
    @staticmethod
    def delete(user_id: int):
        """Delete a user from the database."""
        try:
            user_data = bank_collection.find_one({"user_id": user_id})
            if user_data:
                bank_collection.delete_one({"user_id": user_id})
                logger.info("User has been deleted successfully.")
            else:
                logger.warning("User not found.")
        except Exception as e:
            logger.error("Error encountered while deleting the user.", e)
            return None


    @staticmethod
    def update(user_id: int, points: int):
        """Update a user in the database."""
        try:
            user_data = bank_collection.find_one({"user_id": user_id})
            if user_data:
                bank_collection.update_one({"user_id": user_id}, {"$set": {"bank": points}})
                logger.info("User has been updated successfully.")
            else:
                logger.warning("User not found.")
        except Exception as e:
            logger.error("Error encountered while updating the user.", e)
            return None
        
    @staticmethod
    def update_upgrades(user_id: int, upgrades: int):
        """Update a user in the database."""
        try:
            user_data = bank_collection.find_one({"user_id": user_id})
            if user_data:
                bank_collection.update_one({"user_id": user_id}, {"$set": {"upgrades": upgrades}})
                logger.info("User has been updated successfully.")
            else:
                logger.warning("User not found.")
        except Exception as e:
            logger.error("Error encountered while updating the user.", e)
            return None


    @staticmethod
    def read(user_id: int):
        """Read a user from the database."""
        try:
            user_data = bank_collection.find_one({"user_id": user_id})
            if user_data:
                return user_data
        except Exception as e:
            logger.error("Error encountered while trying to read the user.", e)
            return None
        
    @staticmethod
    def read_highest_10_bank():
        """Read a user from the database."""
        try:
            user_data = bank_collection.find().sort("bank", -1).limit(10)
            if user_data:
                return user_data
        except Exception as e:
            logger.error("Error encountered while trying to read the user.", e)
    
    @staticmethod
    def readAll():
        """Read all users from the database."""
        try:
            user_data = bank_collection.find()
            if user_data:
                return user_data
        except Exception as e:
            logger.error("Error encountered while trying to read all users.", e)
            return None
        