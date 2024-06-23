from db.dbConfig import mongo_client
farm_collection = mongo_client.db.farm

class Farm:
    @staticmethod
    def create(user_id: int, ctx):
        """Create a farm for the user."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                print("Farm already exists.")
                return None
            else:
                farm = {
                    "user_id": user_id,
                    "farm_name": f"{ctx.author.display_name}'s Farm",
                    "chickens": [],
                    "eggs": 0,
                    "eggs_generated": 0
                }
                farm_collection.insert_one(farm)
                print("Farm has been created successfully.")
        except Exception as e:
            print("Error encountered while creating the farm.", e)
            return None
    
    @staticmethod
    def delete(user_id: int):
        """Delete a farm from the database."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                farm_collection.delete_one({"user_id": user_id})
                print("Farm has been deleted successfully.")
            else:
                print("Farm not found.")
        except Exception as e:
            print("Error encountered while deleting the farm.", e)

    @staticmethod
    def update(user_id:int, farm_name:str, chickens: list, eggs: int, eggs_generated: int):
        """Update a farm's status in the database."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                farm_collection.update_one({"user_id": user_id}, {"$set": {"chickens": chickens,"farm_name": farm_name,"eggs": eggs, "eggs_generated": eggs_generated}})
        except Exception as e:
            print("Error encountered while trying to update farm's status.", e)


    @staticmethod
    def read(user_id: int):
        """Read a farm's data from the database."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                return farm_data
            else:
                print("Farm not found.")
                return False
        except Exception as e:
            print("Error encountered while reading the farm.", e)
            return None