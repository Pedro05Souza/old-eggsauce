from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv
uri = os.getenv("MONGODB_KEY")

# Function to connect to the database

def connect(uri):
    try:
        client = MongoClient(uri)
        client.admin.command('ping')
        print("Sucessfull connection with MongoDB!")
        
        return client
    except Exception as e:
        print("Error encounted while connecting to the database.", e)
        return None    


mongo_client = connect(uri)
db = mongo_client.botDiscord
