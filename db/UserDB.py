from db.dbConfig import mongo_client
users_collection = mongo_client.db.usuario

# This class is responsible for handling user data in the database.

class Usuario:
    @staticmethod
    def create(user_id : int, points : int):
        """Create a user in the database."""
        try:            
            user_data = users_collection.find_one({"user_id": user_id})
            if user_data:
                print("User already exists.")
                return None 
            else:
                if not isinstance(points, int):
                    points = 0
                user = {
                    "user_id": user_id,
                    "points": points,
                    "roles" : ""
                }
                users_collection.insert_one(user)
                print("User has been created successfully.")
        except Exception as e:
            print("Error encountered while creating the user.", e)
            return None    
        
    @staticmethod
    def delete(user_id : int):
        """Delete a user from the database."""
        try:
            user_data = users_collection.find_one({"user_id": user_id})
            if user_data:
                users_collection.delete_one({"user_id" : user_id})
                print("User has been deleted successfully.")
            else:
                print("User not found.")
        except Exception as e:
                print("Error encountered while deleting the user.", e)
    
    @staticmethod
    def update(user_id : int, points : int, roles: str):
        """Update a user's status in the database."""
        try:
            user_data = users_collection.find_one({"user_id" : user_id})
            if user_data:
                if not isinstance(points, int): 
                    points = 0
                users_collection.update_one({"user_id": user_id}, {"$set": {"points": points, "roles": roles}})
        except Exception as e:
            print("Error encountered while trying to update user's status.", e)
        
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
            print("Error encountered while finding user.")
            return None
        
    @staticmethod
    def readAll():
        """Read all users from the database."""
        try:
            users = users_collection.find()
            return users
        except Exception as e:
            print("Error encountered while reading users.", e)
            return None

    @staticmethod
    def resetAll():
        """Resets all users from the database."""
        try:
            users_collection.update_many({}, {"$set": {"points": 0, "roles": ""}})
        except Exception as e:
            print("Error encountered while deleting users.", e)
            return None
        
    @staticmethod
    def read_all_members_with_role():
        """Read all users from the database."""
        try:
            users = users_collection.find({"roles": {"$ne": ""}})
            return users
        except Exception as e:
            print("Error encountered while reading users.", e)
            return None
    
    @staticmethod
    def updateAll(role : str):
        """Update all users in the database."""
        try:
            users_collection.update_many({}, {"$set": {"roles": role}})
        except Exception as e:
            print("Error encountered while updating users.", e)
            return None

    

        
        

