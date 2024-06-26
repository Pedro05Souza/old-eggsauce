from db.dbConfig import mongo_client
config_collection = mongo_client.db.botcfg

class BotConfig:

    @staticmethod
    def create(server_id: int, toggled_modules: list = None, channel_id: int = None):
        """Create a toggle in the database."""
        try:
            toggle_data = config_collection.find_one({"server_id" : toggled_modules})
            if toggle_data:
                print("This channel already exists.")
                return None
            else:
                toggle = {
                    "server_id": server_id,
                    "toggled_modules": toggled_modules,
                    "channel_id": channel_id,
                }
                config_collection.insert_one(toggle)
                print("Server created successfully.")
        except Exception as e:
            print("Error encountered while creating a server.", e)
            return None
        
    @staticmethod
    def create_toggle(server_id:int, toggled_modules: list):
        """Create a toggle in the database."""
        try:
            toggle_data = config_collection.find_one({"server_id": server_id})
            if toggle_data:
                print("This toggle already exists.")
                return None
            else:
                toggle = {
                    "server_id": server_id,
                    "toggle_modules": toggled_modules,
                }
                config_collection.insert_one(toggle)
                print("Toggle created successfully.")
        except Exception as e:
            print("Error encountered while creating a toggle.", e)
            return None
        
    @staticmethod
    def create_channel(server_id:int, channel_id: int):
        """Create a channel in the database."""
        try:
            toggle_data = config_collection.find_one({"server_id": server_id})
            if toggle_data:
                print("This channel already exists.")
                return None
            else:
                toggle = {
                    "server_id": server_id,
                    "channel_id": channel_id,
                }
                config_collection.insert_one(toggle)
                print("Channel created successfully.")
        except Exception as e:
            print("Error encountered while creating a channel.", e)
            return
        
    @staticmethod
    def update_toggled_modules(server_id: int, toggled_modules: list):
        """Update a toggle in the database."""
        try:
            toggle_data = config_collection.find_one({"server_id": server_id})
            if toggle_data:
                config_collection.update_one({"server_id": server_id}, {"$set": {"toggled_modules": toggled_modules}})
                print("Toggle updated successfully.")
            else:
                print("Toggle not found.")
        except Exception as e:
            print("Error encountered while updating a toggle.", e)
    
    @staticmethod
    def update_channel_id(server_id: int, channel_id: int):
        """Update a channel in the database."""
        try:
            toggle_data = config_collection.find_one({"server_id" : server_id})
            print(toggle_data)
            if toggle_data:
                config_collection.update_one({"server_id": toggle_data["server_id"]}, {"$set": {"channel_id": channel_id}})
                print("Channel updated successfully.")
            else:
                print("Channel not found.")
        except Exception as e:
            print("Error encountered while updating a channel.", e)
        
    @staticmethod
    def delete(server_id: int):
        """Delete a toggle from the database."""
        try:
            config_data = config_collection.find_one({"server_id": server_id})
            if config_data:
                config_collection.delete_one({"server_id" : server_id})
                print("Server config has been deleted successfully.")
            else:
                print("Server not found.")
        except Exception as e:
                print("Error encountered while deleting a server.", e)
    
    @staticmethod
    def read_all_channels():
        """Read all channels from the database."""
        try:
            channels = config_collection.find()
            return channels
        except Exception as e:
            print("Error encountered while reading channels.", e)
            return None
    
    @staticmethod
    def read(server_id: int):
        """Read a server from the database."""
        try:
            config_data = config_collection.find_one({"server_id": server_id})
            if config_data:
                return config_data
            else:
                print("Server not found.")
                return None
        except Exception as e:
            print("Error encountered while reading a server.", e)
            return None
        