from db.dbConfig import mongo_client
from time import time
import logging
farm_collection = mongo_client.db.farm
logger = logging.getLogger('botcore')


class Farm:
    @staticmethod
    def create(user_id: int, ctx):
        """Create a farm for the user."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                logger.warning(f"Farm for {user_id} already exists.")
                return None
            else:
                farm = {
                    "user_id": user_id,
                    "farm_name": f"{ctx.author.display_name}'s Farm",
                    "plant_name": f"{ctx.author.display_name}'s CornField",
                    "corn": 0,
                    "chickens": [],
                    "eggs_generated": 0,
                    "farmer": None,
                    "corn_limit": 100,
                    "plot": 1,
                    "last_chicken_drop": time(),
                    "last_farmer_drop": time(),
                    "last_corn_drop": time()
                }
                farm_collection.insert_one(farm)
                logger.info(f"Farm for {user_id} has been created successfully.")
        except Exception as e:
            logger.error("Error encountered while creating the farm.", e)
            return None
    
    @staticmethod
    def delete(user_id: int):
        """Delete a farm from the database."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                farm_collection.delete_one({"user_id": user_id})
                logger.info("Farm has been deleted successfully.")
            else:
                logger.warning("Farm not found.")
        except Exception as e:
            logger.error("Error encountered while deleting the farm.", e)

    @staticmethod
    def update(user_id: int, **kwargs):
        """Update a farm's status in the database."""
        possible_keywords = ["farm_name","plant_name", "corn", "chickens", "eggs_generated", "farmer", "corn_limit", "plot"]
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                if kwargs:
                    for key, value in kwargs.items():
                        if key in possible_keywords:
                            farm_collection.update_one({"user_id": user_id}, {"$set" : {key: value}})
                else:
                    logger.warning("Keyword arguments aren't being passed.")
        except Exception as e:
            logger.error("Error encountered while trying to update user farm.", e)
            
    @staticmethod
    def update_chicken_drop(user_id: int):
        """Update a farm's last drop in the database."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                farm_collection.update_one({"user_id": user_id}, {"$set": {"last_chicken_drop": time()}})
        except Exception as e:
            logger.error("Error encountered while trying to update farm's last drop.", e)
            return None
        
    @staticmethod
    def update_corn_drop(user_id: int):
        """Update a farm's last drop in the database."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                farm_collection.update_one({"user_id": user_id}, {"$set": {"last_corn_drop": time()}})
        except Exception as e:
            logger.error("Error encountered while trying to update farm's last drop.", e)
            return None

    @staticmethod
    def read(user_id: int):
        """Read a farm's data from the database."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                return farm_data
            else:
                logger.warning("Farm not found.")
                return False
        except Exception as e:
            logger.error("Error encountered while reading the farm.", e)
            return None
        
    @staticmethod
    def readAll():
        """Read all farms from the database."""
        try:
            farms = farm_collection.find()
            if farms:
                return farms
            else:
                logger.warning("No farms found.")
                return False
        except Exception as e:
            logger.error("Error encountered while reading all farms.", e)
            return None
    
    @staticmethod
    def deleteAll():
        """Delete all farms from the database."""
        try:
            farm_collection.delete_many({})
            logger.info("All farms have been deleted successfully.")
        except Exception as e:
            logger.error("Error encountered while deleting all farms.", e)
            return None