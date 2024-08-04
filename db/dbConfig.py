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
# current_schema = {
#     "$jsonSchema":{
#         "bsonType": "object",
#         "required": ["user_id"],
#         "properties": {
#             "user_id": {
#                 "bsonType": "long",
#                 "description": "must be a long."
#             },
#             "farm_name": {
#                 "bsonType": "string",
#                 "description": "must be a string."
#             },
#             "plant_name": {
#                 "bsonType": "string",
#                 "description": "must be a string."
#             },
#             "corn": {
#                 "bsonType": "int",
#                 "description": "must be an integer."
#             },
#             "chickens": {
#                 "bsonType": "array",
#                 "description": "must be an array."
#             },
#             "eggs_generated": {
#                 "bsonType": "int",
#                 "description": "must be an integer."
#             },
#             "farmer": {
#                 "bsonType": ["string", "null"],
#                 "description": "must be a string."
#             },
#             "corn_limit": {
#                 "bsonType": "int",
#                 "description": "must be an integer."
#             },
#             "plot": {
#                 "bsonType": "int",
#                 "description": "must be an integer."
#             },
#             "last_chicken_drop": {
#                 "bsonType": "double",
#                 "description": "must be a double"
#             },
#             "last_corn_drop": {		
#                 "bsonType": "double",
#                 "description": "must be a double"
#             },
#             "last_farmer_drop": {
#                 "bsonType": "double",
#                 "description": "must be a double"
#             },
#             "bench" : {
#                 "bsonType": "array",
#                 "description": "must be an array."
#             },
#             "mmr": {
#                 "bsonType": "int",
#                 "description": "must be an integer."
#             },
#             "highest_mmr": {
#                 "bsonType": "int",
#                 "description": "must be an integer."
#             },
#             "losses": {
#                 "bsonType": "int",
#                 "description": "must be an integer."
#             },
#             "wins": {
#                 "bsonType": "int",
#                 "description": "must be an integer."
#             },
#             "redeemables": {
#                 "bsonType": "array",
#                 "description": "must be an array."	

#         }
#     }
# }
# }

# mongo_client.db.command ("collMod", "farm", validator=current_schema)
# for collection in mongo_client.db.list_collection_names():
#     collection_info = mongo_client.db.list_collections(filter={"name": collection})
#     for info in collection_info:
#         schema = info.get("options", {}).get("validator", {})
#         print(f"Schema for collection '{collection}': {schema}\n")