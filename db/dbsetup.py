"""
This module is responsible for establishing a connection to the database.
"""

from pymongo import MongoClient
import logging

logger = logging.getLogger('botcore')

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
        client = MongoClient(uri)
        client.admin.command('ping')
        logger.info("Connected to the database.")
        logger.info(client)
        return client
    except Exception as e:
        logger.error(f"Could not connect to the database: {e}")
    return None    

mongo_client = connect(uri)
if mongo_client is None:
    logger.critical("Could not connect to the database.")
    exit(1)
db = mongo_client['BotDiscord']