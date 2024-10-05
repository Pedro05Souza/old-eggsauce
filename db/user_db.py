"""
This module contains the database functions for the user collection.
"""
from db.db_setup import mongo_client
from time import time
from temp import cache_initiator
from typing import Union
from logs import log_info, log_error, log_warning
users_collection = mongo_client.BotDiscord.user
__all__ = ['User']

# This class is responsible for handling user data in the database.

class User:
    
    @staticmethod
    async def create(user_id: int, points: int) -> None:
        """
        Creates an user in the user collection.

        Args:
            user_id (int): The id of the user to create.
            points (int): The points of the user to create.

        Returns:
            None
        """
        try:            
            user_data = await users_collection.find_one({"user_id": user_id})
            if user_data:
                log_warning(f"User {user_id} already exists.")
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
                await cache_initiator.put_user(user_id, user_data=user)
                await users_collection.insert_one(user)
                log_info(f"User {user_id} has been created successfully.")
        except Exception as e:
            log_error(f"Error encountered while creating the user {user_id}.", e)
            return None    
        
    @staticmethod
    async def delete(user_id: int) -> None:
        """
        Deletes an user from the user collection.

        Args:
            user_id (int): The id of the user to delete.
        
        Returns:
            None
        """
        try:
            user_data = await users_collection.find_one({"user_id": user_id})
            if user_data:
                await cache_initiator.delete(user_id)
                await users_collection.delete_one({"user_id" : user_id})
            else:
                log_warning(f"User not found with id {user_id}.")
        except Exception as e:
            log_error(f"Error encountered while deleting the user {user_id}.", e)
            return None
    
    @staticmethod
    async def update_all(user_id: int, points: int, roles: str) -> None:
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
            user_data = await users_collection.find_one({"user_id" : user_id})
            if user_data:
                user_data['points'] = points
                user_data['roles'] = roles
                await cache_initiator.put_user(user_id, user_data=user_data)
                await users_collection.update_one({"user_id": user_id}, {"$set": {"points": points, "roles": roles}})
        except Exception as e:
            log_error(f"Error encountered while trying to update user's status {user_id}.", e)
            return None

    @staticmethod
    async def update_points(user_id: int, points: int) -> None:
        """
        Update n user's points in the user collection.

        Args:
            user_id (int): The id of the user to update.
            points (int): The points of the user to update.
            user_cache (dict): The user cache to update.

        Returns:
            None
        """
        try:
            if points < 0:
                points = 0
            user_data = await users_collection.find_one({"user_id": user_id})
            if user_data:
                user_data['points'] = points
                await cache_initiator.put_user(user_id, user_data=user_data)
                await users_collection.update_one({"user_id": user_id}, {"$set": {"points": points}})
        except Exception as e:
            log_error(f"Error encountered while trying to update user's points {user_id}.", e)
            return None
        
    @staticmethod
    async def update_roles(user_id: int, roles: str) -> None:
        """
        Updates a user's roles in the user collection.

        Args:
            user_id (int): The id of the user to update.
            roles (str): The roles of the user to update.

        Returns:
            None
        """
        try:
            user_data = await users_collection.find_one({"user_id": user_id})
            if user_data:
                user_data['roles'] = roles
                cache_initiator.put_user(user_id, user_data=user_data)
                await users_collection.update_one({"user_id": user_id}, {"$set": {"roles": roles}})
        except Exception as e:
            log_error(f"Error encountered while trying to update user's roles {user_id}.", e)
            return None

    @staticmethod
    async def update_salary_time(user_id: int) -> None:
        """
        Updates a user's salary time in the user collection.

        Args:
            user_id (int): The id of the user to update.

        Returns:
            None
        """
        try:
            user_data = await users_collection.find_one({"user_id": user_id})
            if user_data:
                user_data['salary_time'] = time()
                await cache_initiator.put_user(user_id, user_data=user_data)
                await users_collection.update_one({"user_id": user_id}, {"$set": {"salary_time": time()}})
        except Exception as e:
            log_error(f"Error encountered while trying to update user's salary time {user_id}.", e)
            return None
        
    @staticmethod
    async def read(user_id: int) -> Union[dict, None]:
        """
        Reads a user from the user collection.

        Args:
            user_id (int): The id of the user to read.

        Returns:
            Union[dict, None]
        """
        try:
            user_data = await users_collection.find_one({"user_id": user_id})
            if user_data:
                return user_data
            else:
                return None
        except Exception as e:
            log_error(f"Error encountered while trying to read the user {user_id}.", e)
            return None
        
    @staticmethod
    async def resetAll() -> None:
        """
        Resets all users from the user collection.

        Returns:
            None
        """
        try:
            await users_collection.update_many({}, {"$set": {"points": 0, "roles": ""}})
        except Exception as e:
            log_error(f"Error encountered while trying to reset all users", e)
            return None
    
    @staticmethod
    async def count_users() -> Union[int, None]:
        """
        Counts all users from the user collection.

        Returns:
            Union[int, None]
        """
        try:
            count = await users_collection.count_documents({})
            return count
        except Exception as e:
            log_error(f"Error encountered while trying to count all users.", e)
            return None