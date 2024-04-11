from db.dbConfig import mongo_client
from db.dbConfig import db
from pymongo.collection import Collection

users_collection = mongo_client.db.usuario

class Usuario:
   
    @staticmethod
    def create(user_id : int, points : int):
        try:            
            user_data = users_collection.find_one({"user_id": user_id})
            if user_data:
                print("Usuário já existe")
                return None 
            else:
                user = {
                    "user_id": user_id,
                    "points": points
                }
                users_collection.insert_one(user)
                print("Usuário criado com sucesso")
        except Exception as e:
            print("Erro ao criar usuário", e)
            return None    
        
    @staticmethod
    def delete(user_id : int):
        try:
            user_data = users_collection.find_one({"user_id": user_id})
            if user_data:
                users_collection.delete_one({"user_id" : user_id})
                print("Usuário excluído com sucesso")
            else:
                print("Usuário não encontrado")
        except Exception as e:
                print("Erro ao excluir o usuário", e)
    
    @staticmethod
    def update(user_id : int, points : int):
        try:
            user_data = users_collection.find_one({"user_id" : user_id})
            if user_data:
                users_collection.update_one({"user_id": user_id}, {"$set": {"points": points}})
        except Exception as e:
            print("Erro ao atualizar os pontos do usuário", e)
        
    @staticmethod
    def read(user_id : int):
        try:
            user_data = users_collection.find_one({"user_id": user_id})
            if user_data:
                return user_data
            else:
                print("Usuário não encontrado")
                return None
        except Exception as e:
            print("Erro ao buscar usuário", e)
            return None
        
    @staticmethod
    def readAll() -> list:
        try:
            users = users_collection.find()
            return users
        except Exception as e:
            print("Erro ao buscar usuários", e)
            return None
        
        

