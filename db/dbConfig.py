from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv
uri = os.getenv("MONGODB_KEY")

def connect(uri):
    try:
        client = MongoClient(uri)
        client.admin.command('ping')
        print("Conexão bem-sucedida com o cliente MongoDB!")
        
        return client
    except Exception as e:
        print("Erro ao conectar com o banco de dados", e)
        return None    


mongo_client = connect(uri)
db = mongo_client.botDiscord
