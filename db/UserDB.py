from db.dbConfig import mongo_client

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
                    "points": points,
                    "roles" : ""
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
    def update(user_id : int, points : int, roles: str):
        try:
            user_data = users_collection.find_one({"user_id" : user_id})
            if user_data:
                users_collection.update_one({"user_id": user_id}, {"$set": {"points": points, "roles": roles}})#agr vai funcionar 😁
        except Exception as e:
            print("Erro ao atualizar os pontos do usuário", e)
        
    @staticmethod
    def read(user_id : int):
        try:
            user_data = users_collection.find_one({"user_id": user_id})
            if user_data:
                return user_data
            else:
                return None
        except Exception:
            print("Erro ao buscar usuário")
            return None
        
    @staticmethod
    def readAll() -> list:
        try:
            users = users_collection.find()
            return users
        except Exception as e:
            print("Erro ao buscar usuários", e)
            return None

    @staticmethod
    def deleteAll():
        try:
            users_collection.delete_many({})
        except Exception as e:
            print("Erro ao excluir todos os usuários", e)
            return None
    
    @staticmethod
    def updateAll(role : str):
        try:
            users_collection.update_many({}, {"$set": {"roles": role}})
        except Exception as e:
            print("Erro ao atualizar todos os usuários", e)
            return None

    

        
        

