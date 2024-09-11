from db.dbConfig import mongo_client
from time import time
from tools.cache import cache_initiator
from tools.shared import update_scheduler, request_threading
from typing import Union
import logging
users_collection = mongo_client.BotDiscord.user
logger = logging.getLogger('botcore')

# This class is responsible for handling user data in the database.

class User:
    
    @staticmethod
    def create(user_id: int, points: int) -> None:
        """Create a user in the database."""
        try:            
            user_data = request_threading(lambda: users_collection.find_one({"user_id": user_id})).result()
            if user_data:
                logger.warning(f"User {user_id} already exists.")
                return None 
            else:
                if not isinstance(points, int):
                    points = 0
                user = {
                    "user_id": user_id,
                    "points": points,
                    "roles" : "",
                    "salary_time": time()
                }
                update_scheduler(lambda: cache_initiator.add_to_user_cache(user_id, user_data=user))
                request_threading(lambda: users_collection.insert_one(user), user_id).result()
                logger.info(f"User {user_id} has been created successfully.")
        except Exception as e:
            logger.error("Error encountered while creating the user.", e)
            return None    
        
    @staticmethod
    def delete(user_id: int) -> None:
        """Delete a user from the database."""
        try:
            user_data = request_threading(lambda: users_collection.find_one({"user_id": user_id})).result()
            if user_data:
                update_scheduler(lambda: cache_initiator.delete_user_cache(user_id))
                request_threading(lambda: users_collection.delete_one({"user_id" : user_id}), user_id).result()
            else:
                logger.warning("User not found.")
        except Exception as e:
            logger.error("Error encountered while deleting the user.", e)
            return None
    
    @staticmethod
    def update_all(user_id: int, points: int, roles: str) -> None:
        """Update a user's status in the database."""
        try:
            user_data = request_threading(lambda: users_collection.find_one({"user_id" : user_id})).result()
            if user_data:
                user_data['points'] = points
                user_data['roles'] = roles
                update_scheduler(lambda: cache_initiator.update_user_cache(user_id, user_data=user_data))
                request_threading(lambda: users_collection.update_one({"user_id": user_id}, {"$set": {"points": points, "roles": roles}}), 
                                  user_id).result()
        except Exception as e:
            logger.error("Error encountered while trying to update user's status.", e)
            return None

    @staticmethod
    def update_points(user_id : int, points : int) -> None:
        """Update a user's points in the database."""
        try:
            if points < 0:
                points = 0
            user_data = request_threading(lambda: users_collection.find_one({"user_id": user_id})).result()
            if user_data:
                user_data['points'] = points
                update_scheduler(lambda: cache_initiator.update_user_cache(user_id, user_data=user_data))
                request_threading(lambda: users_collection.update_one({"user_id": user_id}, {"$set": {"points": points}}), 
                                  user_id).result()
        except Exception as e:
            logger.error("Error encountered while trying to update user's points.", e)
            return None

    @staticmethod
    def update_roles(user_id : int, roles: str) -> None:
        """Update a user's roles in the database."""
        try:
            user_data = request_threading(lambda: users_collection.find_one({"user_id": user_id})).result()
            if user_data:
                user_data['roles'] = roles
                update_scheduler(lambda: cache_initiator.update_user_cache(user_id, user_data=user_data))
                request_threading(lambda: users_collection.update_one({"user_id": user_id}, {"$set": {"roles": roles}}), 
                                  user_id).result()
        except Exception as e:
            logger.error("Error encountered while trying to update user's roles.", e)
            return None

    @staticmethod
    def update_salary_time(user_id : int) -> None:
        """Update a user's salary time in the database."""
        try:
            user_data = request_threading(lambda: users_collection.find_one({"user_id": user_id})).result()
            if user_data:
                user_data['salary_time'] = time()
                update_scheduler(lambda: cache_initiator.update_user_cache(user_id, user_data=user_data))
                request_threading(lambda: users_collection.update_one({"user_id": user_id}, {"$set": {"salary_time": time()}}),
                                  user_id).result()
        except Exception as e:
            logger.error("Error encountered while trying to update user's salary time.", e)
            return None
        
    @staticmethod
    def read(user_id : int) -> Union[dict, None]:
        """Read a user from the database."""
        try:
            user_data = request_threading(lambda: users_collection.find_one({"user_id": user_id})).result()
            if user_data:
                return user_data
            else:
                return None
        except Exception:
            logger.error("Error encountered while trying to read the user.")
            return None
        
    @staticmethod
    def readAll() -> Union[list, None]:
        """Read all users from the database."""
        try:
            users = request_threading(lambda: users_collection.find()).result()
            return users
        except Exception as e:
            logger.error("Error encountered while trying to read all users.", e)
            return None
        
    @staticmethod
    def read_highest_10_points() -> Union[list, None]:
        """Read the top 10 users with the most points from the database."""
        try:
            users = request_threading(lambda: users_collection.find().sort("points", -1).limit(10)).result()
            return users
        except Exception as e:
            logger.error("Error encountered while trying to read the top 10 users with the most points.", e)
            return None

    @staticmethod
    def resetAll() -> None:
        """Resets all users from the database."""
        try:
            request_threading(lambda: users_collection.update_many({}, {"$set": {"points": 0, "roles": ""}})).result()
        except Exception as e:
            logger.error("Error encountered while trying to reset all users.", e)
            return None
    
    @staticmethod
    def count_users() -> Union[int, None]:
        """Counts all users from the database."""
        try:
            count = request_threading(lambda: users_collection.count_documents({})).result()
            return count
        except Exception as e:
            logger.error("Error encountered while trying to count all users.", e)
            return None