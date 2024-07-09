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
                    "plant_name": f"{ctx.author.display_name}'s CornField",
                    "corn": 0,
                    "chickens": [],
                    "eggs_generated": 0,
                    "farmer": None,
                    "corn_limit": 100,
                    "plot": 1
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
    def update(user_id:int, farm_name:str, chickens: list, eggs_generated: int):
        """Update a farm's status in the database."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                farm_collection.update_one({"user_id": user_id}, {"$set": {"chickens": chickens,"farm_name": farm_name,"eggs_generated": eggs_generated}})
        except Exception as e:
            print("Error encountered while trying to update farm's status.", e)
    
    @staticmethod
    def update_farmer(user_id:int, farmer: str):
        """Update a farm's farmer in the database."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                farm_collection.update_one({"user_id": user_id}, {"$set": {"farmer": farmer}})
        except Exception as e:
            print("Error encountered while trying to update farm's farmer.", e)

    @staticmethod
    def update_chickens(user_id:int, chickens: list):
        """Update a farm's chickens in the database."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                farm_collection.update_one({"user_id": user_id}, {"$set": {"chickens": chickens}})
        except Exception as e:
            print("Error encountered while trying to update farm's chickens.", e)
    
    @staticmethod
    def update_corn(user_id:int, corn:int):
        """Update a farm's corn in the database."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                farm_collection.update_one({"user_id": user_id}, {"$set": {"corn": corn}})
        except Exception as e:
            print("Error encountered while trying to update farm's corn.", e)
    
    @staticmethod
    def update_plot(user_id: int, plot: int):
        """Update a farm's plot in the database."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                farm_collection.update_one({"user_id": user_id}, {"$set": {"plot": plot}})
        except Exception as e:
            print("Error encountered while trying to update farm's plot.", e)
    
    @staticmethod
    def update_corn_limit(user_id: int, corn_limit: int):
        """Update a farm's corn limit in the database."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                farm_collection.update_one({"user_id": user_id}, {"$set": {"corn_limit": corn_limit}})
        except Exception as e:
            print("Error encountered while trying to update farm's corn limit.", e)

    @staticmethod
    def update_plant_name(user_id: int, plant_name: str):
        """Update a farm's plant name in the database."""
        try:
            farm_data = farm_collection.find_one({"user_id": user_id})
            if farm_data:
                farm_collection.update_one({"user_id": user_id}, {"$set": {"plant_name": plant_name}})
        except Exception as e:
            print("Error encountered while trying to update farm's plant name.", e)

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
        
    @staticmethod
    def readAll():
        """Read all farms from the database."""
        try:
            farms = farm_collection.find()
            if farms:
                return farms
            else:
                print("No farms found.")
                return False
        except Exception as e:
            print("Error encountered while reading all farms.", e)
            return None
    
    @staticmethod
    def deleteAll():
        """Delete all farms from the database."""
        try:
            farm_collection.delete_many({})
            print("All farms have been deleted successfully.")
        except Exception as e:
            print("Error encountered while deleting all farms.", e)
            return None
    
        

    
