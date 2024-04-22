from db.dbConfig import mongo_client
channels_collection = mongo_client.db.channel

class ChannelDB:

    @staticmethod
    def create(server_id:int, channel_id: int):
        try:
            channel_data = channels_collection.find_one({"channel_id" : channel_id})
            if channel_data:
                print("Esse canal já está setado")
                return None
            else:
                channel = {
                    "server_id": server_id,
                    "channel_id": channel_id,
                }
                channels_collection.insert_one(channel)
                print("Canal registrado com sucesso")
        except Exception as e:
            print("Erro ao criar usuário", e)
            return None
    
    @staticmethod
    def delete(channel_id: int):
        try:
            channel_data = channels_collection.find_one({"channel_id": channel_id})
            if channel_data:
                channels_collection.delete_one({"channel_id" : channel_id})
                print("Canal excluído com sucesso")
            else:
                print("Canal não encontrado")
        except Exception as e:
                print("Erro ao excluir o canal", e)

                
    @staticmethod
    def read(channel_id: int):
        try:
            channel_data = channels_collection.find_one({"channel_id": channel_id})
            if channel_data:
                return channel_data
            else:
                print("Canal não encontrado")
                return None
        except Exception as e:
            print("Erro ao encontrar o canal", e)
            return None

    @staticmethod
    def read(server_id: int):
        try:
            channel_data = channels_collection.find_one({"server_id": server_id})
            if channel_data:
                return channel_data
            else:
                print("Servidor não encontrado.")
                return None
        except Exception as e:
            print("Erro ao encontrar o canal", e)
            return None
        

    @staticmethod
    def update(channel_id: int):
        try:
            channel_data = channels_collection.find_one({"channel_id" : channel_id})
            if channel_data:
                channels_collection.update_one({"server_id": channel_data["server_id"]}, {"$set": {"channel_id": channel_id}})
                print("Canal atualizado com sucesso")
            else:
                print("Canal não encontrado")
                return None
        except Exception as e:
            print("Erro ao atualizar o canal", e)
    
    @staticmethod
    def readAll():
        try:
            channels = channels_collection.find({"channel_id": { "$exists": True } })
            return channels
        except Exception as e:
            print("Erro ao encontrar os canais", e)
            return None
            