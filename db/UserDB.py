from db.dbConfig import mongo_client
users_collection = mongo_client.db.usuario

# This class is responsible for handling user data in the database.

class Usuario:
    @staticmethod
    def create(user_id : int, points : int):
        try:            
            user_data = users_collection.find_one({"user_id": user_id})
            if user_data:
                print("User already exists.")
                return None 
            else:
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
        try:
            user_data = users_collection.find_one({"user_id" : user_id})
            if user_data:
                users_collection.update_one({"user_id": user_id}, {"$set": {"points": points, "roles": roles}})#agr vai funcionar 😁
        except Exception as e:
            print("Error encountered while trying to update user's status.", e)
        
    @staticmethod
    def read(user_id : int):
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
    def readAll() -> list:
        try:
            users = users_collection.find()
            return users
        except Exception as e:
            print("Error encountered while reading users.", e)
            return None

    @staticmethod
    def deleteAll():
        try:
            users_collection.delete_many({})
        except Exception as e:
            print("Error encountered while deleting users.", e)
            return None
    
    @staticmethod
    def updateAll(role : str):
        try:
            users_collection.update_many({}, {"$set": {"roles": role}})
        except Exception as e:
            print("Error encountered while updating users.", e)
            return None

    

        
        

