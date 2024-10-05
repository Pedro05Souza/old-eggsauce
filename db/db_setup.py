"""
This module is responsible for establishing a connection to the database.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from logs import log_info, log_error

uri = "mongodb://db:27017/"

def connect(uri):
    """
    Establishes a connection to the database.

    Args:
        uri (str): The uri of the database.

    Returns:
        MongoClient | None
    """
    try:
        client = AsyncIOMotorClient(uri)
        log_info("Connected to the database.")
        return client
    except Exception as e:
        log_error(f"Could not connect to the database: {e}")
    return None
    
mongo_client = connect(uri)