from db.dbConfig import mongo_client
toggle_collection = mongo_client.db.toggle

class ToggleDB:

    @staticmethod
    def create(server_id:int, toggle_value: bool):
        """Create a toggle in the database."""
        try:
            toggle_data = toggle_collection.find_one({"toggle_id" : toggle_value})
            if toggle_data:
                print("This toggle already exists.")
                return None
            else:
                toggle = {
                    "server_id": server_id,
                    "toggle": toggle_value,
                }
                toggle_collection.insert_one(toggle)
                print("Toggle created successfully.")
        except Exception as e:
            print("Error encountered while creating a toggle.", e)
            return None
        
    @staticmethod
    def update(server_id: int, toggle_value: bool):
        """Update a toggle in the database."""
        try:
            toggle_data = toggle_collection.find_one({"server_id": server_id})
            if toggle_data:
                toggle_collection.update_one({"server_id": server_id}, {"$set": {"toggle": toggle_value}})
                print("Toggle updated successfully.")
            else:
                print("Toggle not found.")
        except Exception as e:
            print("Error encountered while updating a toggle.", e)
        
    @staticmethod
    def delete(server_id: int):
        """Delete a toggle from the database."""
        try:
            toggle_data = toggle_collection.find_one({"server_id": server_id})
            if toggle_data:
                toggle_collection.delete_one({"server_id" : server_id})
                print("Toggle has been deleted successfully.")
            else:
                print("Toggle not found.")
        except Exception as e:
                print("Error encountered while deleting a toggle.", e)

    @staticmethod
    def read(server_id: int):
        """Read a toggle from the database."""
        try:
            toggle_data = toggle_collection.find_one({"server_id": server_id})
            if toggle_data:
                return toggle_data
            else:
                print("Toggle not found.")
                return None
        except Exception as e:
            print("Error encountered while reading a toggle.", e)
            return None
        