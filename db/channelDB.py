from db.dbConfig import mongo_client
channels_collection = mongo_client.db.channel

class ChannelDB:

    @staticmethod
    def create(server_id:int, channel_id: int):
        """Create a channel in the database."""
        try:
            channel_data = channels_collection.find_one({"channel_id" : channel_id})
            if channel_data:
                print("This channel already exists.")
                return None
            else:
                channel = {
                    "server_id": server_id,
                    "channel_id": channel_id,
                }
                channels_collection.insert_one(channel)
                print("Channel created successfully.")
        except Exception as e:
            print("Error encountered while creating a channel.", e)
            return None
    
    @staticmethod
    def delete(channel_id: int):
        """Delete a channel from the database."""
        try:
            channel_data = channels_collection.find_one({"channel_id": channel_id})
            if channel_data:
                channels_collection.delete_one({"channel_id" : channel_id})
                print("Channel has been deleted successfully.")
            else:
                print("Channel not found.")
        except Exception as e:
                print("Error encountered while deleting a channel.", e)

    @staticmethod
    def read(server_id: int):
        """Read a channel from the database."""
        try:
            channel_data = channels_collection.find_one({"server_id": server_id})
            if channel_data:
                return channel_data
            else:
                print("Guild not found.")
                return None
        except Exception as e:
            print("Error encountered while reading a guild.", e)
            return None

    @staticmethod
    def update(server_id: int,channel_id: int):
        """Update a channel in the database."""
        print(f"balls: {channel_id}")
        try:
            channel_data = channels_collection.find_one({"server_id" : server_id})
            if channel_data:
                channels_collection.update_one({"server_id": channel_data["server_id"]}, {"$set": {"channel_id": channel_id}})
                print("Channel updated successfully.")
            else:
                print("Channel not found.")
                return None
        except Exception as e:
            print("Something went wrong while updating the channel.", e)
    
    @staticmethod
    def readAll():
        """Read all channels from the database."""
        try:
            channels = channels_collection.find({"channel_id": { "$exists": True } })
            return channels
        except Exception as e:
            print("Erro ao encontrar os canais", e)
            return None
            