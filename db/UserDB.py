from db.dbConfig import mongo_client
from time import time
import logging
users_collection = mongo_client.db.usuario

logger = logging.getLogger('botcore')

# This class is responsible for handling user data in the database.

class User:
    @staticmethod
    def create(user_id : int, points : int):
        """Create a user in the database."""
        try:            
            user_data = users_collection.find_one({"user_id": user_id})
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
                users_collection.insert_one(user)
                logger.info(f"User {user_id} has been created successfully.")
        except Exception as e:
            logger.error("Error encountered while creating the user.", e)
            return None    
        
    @staticmethod
    def delete(user_id : int):
        """Delete a user from the database."""
        try:
            user_data = users_collection.find_one({"user_id": user_id})
            if user_data:
                users_collection.delete_one({"user_id" : user_id})
            else:
                logger.warning("User not found.")
        except Exception as e:
            logger.error("Error encountered while deleting the user.", e)
            return None
    
    @staticmethod
    def update_all(user_id : int, points : int, roles: str):
        """Update a user's status in the database."""
        try:
            user_data = users_collection.find_one({"user_id" : user_id})
            if user_data:
                if not isinstance(points, int): 
                    points = 0
                users_collection.update_one({"user_id": user_id}, {"$set": {"points": points, "roles": roles}})
        except Exception as e:
            logger.error("Error encountered while trying to update user's status.", e)
            return None

    @staticmethod
    def update_points(user_id : int, points : int):
        """Update a user's points in the database."""
        try:
            user_data = users_collection.find_one({"user_id": user_id})
            if user_data:
                if not isinstance(points, int):
                    points = 0
                users_collection.update_one({"user_id": user_id}, {"$set": {"points": points}})
        except Exception as e:
            logger.error("Error encountered while trying to update user's points.", e)
            return None

    @staticmethod
    def update_roles(user_id : int, roles: str):
        """Update a user's roles in the database."""
        try:
            user_data = users_collection.find_one({"user_id": user_id})
            if user_data:
                users_collection.update_one({"user_id": user_id}, {"$set": {"roles": roles}})
        except Exception as e:
            logger.error("Error encountered while trying to update user's roles.", e)
            return None

    @staticmethod
    def update_salary_time(user_id : int):
        """Update a user's salary time in the database."""
        try:
            user_data = users_collection.find_one({"user_id": user_id})
            if user_data:
                users_collection.update_one({"user_id": user_id}, {"$set": {"salary_time": time()}})
        except Exception as e:
            logger.error("Error encountered while trying to update user's salary time.", e)
            return None
        
    @staticmethod
    def read(user_id : int):
        """Read a user from the database."""
        try:
            user_data = users_collection.find_one({"user_id": user_id})
            if user_data:
                return user_data
            else:
                return None
        except Exception:
            logger.error("Error encountered while trying to read the user.")
            return None
        
    @staticmethod
    def readAll():
        """Read all users from the database."""
        try:
            users = users_collection.find()
            return users
        except Exception as e:
            logger.error("Error encountered while trying to read all users.", e)
            return None

    @staticmethod
    def resetAll():
        """Resets all users from the database."""
        try:
            users_collection.update_many({}, {"$set": {"points": 0, "roles": ""}})
        except Exception as e:
            logger.error("Error encountered while trying to reset all users.", e)
            return None
        
