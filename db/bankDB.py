from db.dbConfig import mongo_client
bank_collection = mongo_client.db.bank


class Bank:

    @staticmethod
    def create(user_id: int, points: int):
        """Create a user in the database."""
        try:
            user_data = bank_collection.find_one({"user_id": user_id})
            if user_data:
                print("User already exists.")
                return None
            else:
                if not isinstance(points, int):
                    points = 0
                user = {
                    "user_id": user_id,
                    "bank": points
                }
                bank_collection.insert_one(user)
                print("User has been created successfully.")
        except Exception as e:
            print("Error encountered while creating the user.", e)
            return None
        
    @staticmethod
    def delete(user_id: int):
        """Delete a user from the database."""
        try:
            user_data = bank_collection.find_one({"user_id": user_id})
            if user_data:
                bank_collection.delete_one({"user_id": user_id})
                print("User has been deleted successfully.")
            else:
                print("User not found.")
        except Exception as e:
            print("Error encountered while deleting the user.", e)


    @staticmethod
    def update(user_id: int, points: int):
        """Update a user in the database."""
        try:
            user_data = bank_collection.find_one({"user_id": user_id})
            if user_data:
                bank_collection.update_one({"user_id": user_id}, {"$set": {"bank": points}})
                print("User has been updated successfully.")
            else:
                print("User not found.")
        except Exception as e:
            print("Error encountered while updating the user.", e)
            return None


    @staticmethod
    def read(user_id: int):
        """Read a user from the database."""
        try:
            user_data = bank_collection.find_one({"user_id": user_id})
            if user_data:
                return user_data
        except Exception as e:
            print("Error encountered while trying to read user's status.", e)
            return None
        