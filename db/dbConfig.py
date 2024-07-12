from pymongo import MongoClient
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger('botcore')


load_dotenv
uri = os.getenv("MONGODB_KEY")


def connect(uri):
    """Connect to the MongoDB database."""
    try:
        client = MongoClient(uri)
        client.admin.command('ping')
        logger.info("Connected to the database.")
        
        return client
    except Exception as e:
        logger.critical(f"Error connecting to the database: {e}")
        return None    


mongo_client = connect(uri)
db = mongo_client.botDiscord
