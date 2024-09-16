from db.dbsetup import mongo_client
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
        """
        Creates an user in the user collection.

        Args:
            user_id (int): The id of the user to create.
            points (int): The points of the user to create.

        Returns:
            None
        """
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
        """
        Deletes an user from the user collection.

        Args:
            user_id (int): The id of the user to delete.
        
        Returns:
            None
        """
        try:
            user_data = request_threading(lambda: users_collection.find_one({"user_id": user_id})).result()
            if user_data:
                update_scheduler(lambda: cache_initiator.delete_from_user_cache(user_id))
                request_threading(lambda: users_collection.delete_one({"user_id" : user_id}), user_id).result()
            else:
                logger.warning("User not found.")
        except Exception as e:
            logger.error("Error encountered while deleting the user.", e)
            return None
    
    @staticmethod
    def update_all(user_id: int, points: int, roles: str) -> None:
        """
        Updates an user's attributes in the user collection.

        Args:
            user_id (int): The id of the user to update.
            points (int): The points of the user to update.
            roles (str): The roles of the user to update.

        Returns:
            None
        """
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
    def update_points(user_id: int, points: int) -> None:
        """
        Update n user's points in the user collection.

        Args:
            user_id (int): The id of the user to update.
            points (int): The points of the user to update.

        Returns:
            None
        """
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
    def update_roles(user_id: int, roles: str) -> None:
        """
        Updates a user's roles in the user collection.

        Args:
            user_id (int): The id of the user to update.
            roles (str): The roles of the user to update.

        Returns:
            None
        """
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
    def update_salary_time(user_id: int) -> None:
        """
        Updates a user's salary time in the user collection.

        Args:
            user_id (int): The id of the user to update.

        Returns:
            None
        """
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
    def read(user_id: int) -> Union[dict, None]:
        """
        Reads a user from the user collection.

        Args:
            user_id (int): The id of the user to read.

        Returns:
            Union[dict, None]
        """
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
    def resetAll() -> None:
        """
        Resets all users from the user collection.

        Returns:
            None
        """
        try:
            request_threading(lambda: users_collection.update_many({}, {"$set": {"points": 0, "roles": ""}})).result()
        except Exception as e:
            logger.error("Error encountered while trying to reset all users.", e)
            return None
    
    @staticmethod
    def count_users() -> Union[int, None]:
        """
        Counts all users from the user collection.

        Returns:
            Union[int, None]
        """
        try:
            count = request_threading(lambda: users_collection.count_documents({})).result()
            return count
        except Exception as e:
            logger.error("Error encountered while trying to count all users.", e)
            return None