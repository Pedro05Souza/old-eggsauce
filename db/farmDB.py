from db.dbsetup import mongo_client
from time import time
from tools.cache import cache_initiator
from tools.shared import update_scheduler, request_threading
from discord.ext.commands import Context
from typing import Union
import logging
farm_collection = mongo_client.BotDiscord.farm
logger = logging.getLogger('botcore')

class Farm:

    @staticmethod
    def create(user_id: int, ctx: Context) -> None:
        """
        Creates a farm for the user in the farm collection.

        Args:
            user_id (int): The id of the user to create the farm for.
            ctx (commands.Context): The context of the command.

        Returns:
            None
        """
        try:
            farm_data = request_threading(lambda: farm_collection.find_one({"user_id": user_id})).result()
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
                    "bench": [],
                    "eggs_generated": 0,
                    "farmer": None,
                    "corn_limit": 200,
                    "plot": 1,
                    "last_chicken_drop": time(),
                    "last_corn_drop": time(),
                    "last_market_drop": time(),
                    "mmr": 0,
                    "highest_mmr": 0,
                    "wins": 0,
                    "losses": 0,
                    "redeemables": [],
                    "last_roll_drop": time()
                }
                update_scheduler(lambda: cache_initiator.add_to_user_cache(user_id, farm_data=farm))
                request_threading(lambda: farm_collection.insert_one(farm), user_id).result()
                logger.info(f"Farm for {user_id} has been created successfully.")
        except Exception as e:
            logger.error("Error encountered while creating the farm.", e)
            return None
    
    @staticmethod
    def delete(user_id: int) -> None:
        """
        Deletes a farm from the farm collection.

        Args:
            user_id (int): The id of the user to delete.

        Returns:
            None
        """
        try:
            farm_data = request_threading(lambda: farm_collection.find_one({"user_id": user_id})).result()
            if farm_data:
                update_scheduler(lambda: cache_initiator.delete_from_user_cache(user_id))
                request_threading(farm_collection.delete_one({"user_id": user_id}), user_id).result()
                logger.info("Farm has been deleted successfully.")
            else:
                logger.warning("Farm not found.")
        except Exception as e:
            logger.error("Error encountered while deleting the farm.", e)

    @staticmethod
    def update(user_id: int, **kwargs) -> None:
        """
        Updates a farm's status in the farm collection.

        Args:
            user_id (int): The id of the user to update.
            **kwargs: The data to update the farm with.

        Returns:
            None
        """
        possible_keywords = {"farm_name", "plant_name", "corn", "chickens", "eggs_generated", "farmer", "corn_limit", "plot", "bench", "mmr", "highest_mmr", "wins", "losses", "redeemables", "last_roll_drop"} 
        try:
            query = {}
            farm_data = request_threading(lambda: farm_collection.find_one({"user_id": user_id})).result()
            if farm_data:
                if kwargs:
                    for key, value in kwargs.items():
                        if key in possible_keywords:
                            query[key] = value
                            farm_data[key] = value
                    if query:
                        update_scheduler(lambda: cache_initiator.update_user_cache(user_id, farm_data=farm_data))
                        request_threading(lambda: farm_collection.update_one({"user_id": user_id}, {"$set": query}), user_id).result()
                else:
                    logger.warning("Keyword arguments aren't being passed.")
        except Exception as e:
            logger.error("Error encountered while trying to update user farm.", e)
            
    @staticmethod
    def update_chicken_drop(user_id: int) -> None:
        """
        Updates a farm's last drop in the farm collection.

        Args:
            user_id (int): The id of the user to update the farm for.

        Returns:
            None
        """
        try:
            farm_data = request_threading(lambda: farm_collection.find_one({"user_id": user_id})).result()
            if farm_data:
                farm_data['last_chicken_drop'] = time()
                update_scheduler(lambda: cache_initiator.update_user_cache(user_id, farm_data=farm_data))
                request_threading(lambda: farm_collection.update_one({"user_id": user_id}, {"$set": {"last_chicken_drop": time()}}),
                                  user_id).result()
        except Exception as e:
            logger.error(f"Error encountered while trying to update farm's last drop. {e}")
            return None
        
    @staticmethod
    def update_farmer_drop(user_id: int) -> None:
        """
        Update a farm's last drop in the farm collection.

        Args:
            user_id (int): The id of the user to update the farm for.

        Returns:
            None
        """
        try:
            farm_data = request_threading(lambda: farm_collection.find_one({"user_id": user_id})).result()
            if farm_data:
                farm_data['last_farmer_drop'] = time()
                update_scheduler(lambda: cache_initiator.update_user_cache(user_id, farm_data=farm_data))
                request_threading(lambda: farm_collection.update_one({"user_id": user_id}, {"$set": {"last_farmer_drop": time()}}), 
                                  user_id).result()
        except Exception as e:
            logger.error("Error encountered while trying to update farm's last drop.", e)
            return
        
    @staticmethod
    def update_corn_drop(user_id: int) -> None:
        """
        Updates a farm's last drop in the farm collection.

        Args:
            user_id (int): The id of the user to update the farm for.

        Returns:
            None
        """
        try:
            farm_data = request_threading(lambda: farm_collection.find_one({"user_id": user_id})).result()
            if farm_data:
                farm_data['last_corn_drop'] = time()
                update_scheduler(lambda: cache_initiator.update_user_cache(user_id, farm_data=farm_data))
                request_threading(lambda: farm_collection.update_one({"user_id": user_id}, {"$set": {"last_corn_drop": time()}}), 
                                  user_id).result()
        except Exception as e:
            logger.error("Error encountered while trying to update farm's last drop.", e)
            return None

    @staticmethod
    def read(user_id: int) -> Union[dict, None]:
        """
        Reads a farm's data from the farm collection.

        Args:
            user_id (int): The id of the user to read the farm for.

        Returns:
            dict | None
        """
        try:
            farm_data = request_threading(lambda: farm_collection.find_one({"user_id": user_id})).result()
            if farm_data:
                return farm_data
            else:
                logger.warning("Farm not found.")
                return None
        except Exception as e:
            logger.error("Error encountered while reading the farm.", e)
            return None
        
    @staticmethod
    def reset_mmr() -> None:
        """
        Resets all farms' mmr in the database.

        Returns:
            None
        """
        try:
            farms = request_threading(lambda: farm_collection.find()).result()
            if farms:
                for farm in farms:
                    farm_collection.update_one({"user_id": farm["user_id"]}, {"$set": {"mmr": 0, "highest_mmr": 0}})
                logger.info("All farms' mmr have been reset successfully.")
            else:
                logger.warning("No farms found.")
        except Exception as e:
            logger.error("Error encountered while resetting all farms' mmr.", e)
            return None
        
    @staticmethod
    def add_last_farm_drop_attribute(user_id: int) -> None:
        """
        Add last farm drop attribute to a farm in the farm collection. This method is ONLY called
        when a player acquires the sustainable farmer.

        Args:
            user_id (int): The id of the user to add the attribute for.

        Returns:
            None
        """
        try:
            farm_data = request_threading(lambda: farm_collection.find_one({"user_id": user_id})).result()
            if farm_data:
                farm_data['last_farmer_drop'] = time()
                update_scheduler(lambda: cache_initiator.update_user_cache(user_id, farm_data=farm_data))
                request_threading(lambda: farm_collection.update_one({"user_id": user_id}, {"$set": {"last_farmer_drop": time()}}), 
                                  user_id).result()
        except Exception as e:
            logger.error("Error encountered while trying to add last farm drop attribute.", e)
            return None
        
    @staticmethod
    def remove_last_farm_drop_attribute(user_id: int) -> None:
        """
        Remove last farm drop attribute from a farm in the farm collection. This method is ONLY called
        when a player switches from the sustainable farmer to another farmer.

        Args:
            user_id (int): The id of the user to remove the attribute for.

        Returns:
            None
        """
        try:
            farm_data = request_threading(lambda: farm_collection.find_one({"user_id": user_id})).result()
            if farm_data:
                farm_data.pop('last_farmer_drop')
                update_scheduler(lambda: cache_initiator.update_user_cache(user_id, farm_data=farm_data))
                request_threading(lambda: farm_collection.update_one({"user_id": user_id}, {"$unset": {"last_farmer_drop": ""}}), 
                                  user_id).result()
        except Exception as e:
            logger.error("Error encountered while trying to remove last farm drop attribute.", e)
            return None
        
    @staticmethod
    def update_last_market_drop(user_id: int) -> None:
        """
        Update a farm's last drop in the farm collection.

        Args:
            user_id (int): The id of the user to update the farm for.

        Returns:
            None
        """
        try:
            farm_data = request_threading(lambda: farm_collection.find_one({"user_id": user_id})).result()
            if farm_data:
                farm_data['last_market_drop'] = time()
                update_scheduler(lambda: cache_initiator.update_user_cache(user_id, farm_data=farm_data))
                request_threading(lambda: farm_collection.update_one({"user_id": user_id}, {"$set": {"last_market_drop": time()}}), 
                                  user_id).result()
        except Exception as e:
            logger.error("Error encountered while trying to update farm's last drop.", e)
            return None
        
    