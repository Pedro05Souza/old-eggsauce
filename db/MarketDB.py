from db.dbConfig import mongo_client
from time import time
import logging
import uuid
market_collection = mongo_client.db.market
logger = logging.getLogger('botcore')

class Market:

    @staticmethod
    def create(offer_id, chicken, price: int, description: str, author_id):
        """Create an item in the market."""
        try:
            offer_data = market_collection.find_one({"offer_id": offer_id})
            if offer_data:
                logger.warning(f"Offer {offer_id} already exists.")
                return None
            else:
                offer = {
                    "offer_id": str(author_id) + "_" + Market.generate_uuid(),
                    "chicken": chicken,
                    "price": price,
                    "description": description,
                    "author_id": author_id,
                    "created_at": time()
                }
                market_collection.insert_one(offer)
                logger.info(f"Offer has been created successfully.")
        except Exception as e:
            logger.error("Error encountered while creating the offer.", e)
            return None
    
    @staticmethod
    def get(offer_id: int):
        """Get an item from the market."""
        try:
            offer_data = market_collection.find_one({"offer_id": offer_id})
            if offer_data:
                return offer_data
            else:
                logger.warning(f"Offer {offer_id} does not exist.")
                return None
        except Exception as e:
            logger.error("Error encountered while getting the offer.", e)
            return None
        
    @staticmethod
    def update(offer_id: int, **kwargs):
        """Update an item in the market."""
        possible_keywords = ["chicken", "description", "author_id"]
        try:
            offer_data = market_collection.find_one({"offer_id": offer_id})
            if offer_data:
                if kwargs:
                    for key, value in kwargs.items():
                        if key in possible_keywords:
                            market_collection.update_one({"offer_id": offer_id}, {"$set": {key: value}})
                else:
                    logger.warning("Keyword arguments aren't being passed.")
            else:
                logger.warning(f"Offer {offer_id} does not exist.")
        except Exception as e:
            logger.error("Error encountered while updating the offer.", e)
            return None
    
    @staticmethod
    def delete(offer_id: int):
        """Delete an item from the market."""
        try:
            offer_data = market_collection.find_one({"offer_id": offer_id})
            if offer_data:
                market_collection.delete_one({"offer_id": offer_id})
                logger.info(f"Offer {offer_id} has been deleted successfully.")
            else:
                logger.warning(f"Offer {offer_id} does not exist.")
        except Exception as e:
            logger.error("Error encountered while deleting the offer.", e)
            return None
    
    @staticmethod
    def get_user_offers(author_id: int):
        """Get all offers from a user."""
        try:
            offers = market_collection.find({"author_id": author_id})
            if offers:
                return list(offers)
            else:
                logger.warning(f"User {author_id} has no offers.")
                return None
        except Exception as e:
            logger.error("Error encountered while getting the offers.", e)
            return None
                
    @staticmethod
    def get_chicken_offers(**kwargs):
        """Get all offers with specific parameters."""
        query = {}
        possible_keywords = ["chicken_rarity", "upkeep_rarity", "price", "author_id"]
        for key, value in kwargs.items():
            if key not in possible_keywords:
                logger.warning(f"Keyword {key} is not a valid keyword.")
                return None
            if value:
                if key == "upkeep_rarity":
                    query["chicken.upkeep_multiplier"] = value
                    min_upkeep = value - 0.15 if value - 0.15 > 0 else 0
                    max_upkeep = value + 0.15 if value + 0.15 < 1 else 1
                    query["chicken.upkeep_multiplier"] = {"$gte": min_upkeep, "$lte": max_upkeep}
                elif key == "price":
                    query["price"] = value
                    min_price = value * .5 if value * .5 > 0 else 0
                    max_price = value * 1.5 if value * 1.5 < 25000 else 25000
                    query["price"] = {"$gte": min_price, "$lte": max_price}
                elif key == "author_id":
                    query["author_id"] = value
                else:
                    query["chicken.rarity"] = value
        try:
            offers = market_collection.find(query).sort("price", 1).limit(10)
            if offers:
                return list(offers)
            else:
                logger.warning(f"No offers found with the parameters provided.")
                return None
        except Exception as e:
            logger.error("Error encountered while getting the offers.", e)
            return None
        
    @staticmethod    
    def count_all_offers():
        """Count all offers in the market."""
        try:
            count = market_collection.count_documents({})
            return count
        except Exception as e:
            logger.error("Error encountered while counting the offers.", e)
            return None
        
    @staticmethod
    def create_many(chickenlist, author_id):
        """Create multiple items in the market."""
        try:
            market_collection.insert_many(chickenlist)
            logger.info(f"Offers have been created successfully.")
        except Exception as e:
            logger.error("Error encountered while creating the offers.", e)
            return None
        
    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4())