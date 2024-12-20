"""
This module contains the database functions for the market collection.
"""
from db.db_setup import mongo_client
from time import time
from typing import Union
from logs import log_info, log_warning, log_error
import uuid
market_collection = mongo_client.BotDiscord.market

__all__ = ['Market']

class Market:

    @staticmethod
    async def create(offer_id, chicken, price: int, description: str, author_id) -> None:
        """
        Create an offer in the market collection.

        Args:
            offer_id (int): The id of the offer to create.
            chicken (dict): The chicken to create the offer with.
            price (int): The price of the offer.
            description (str): The description of the offer.
            author_id (int): The id of the author of the offer.

        Returns:
            None
        """
        try:
            offer_data = await market_collection.find_one({"offer_id": offer_id})
            if offer_data:
                log_warning(f"Offer {offer_id} already exists.")
                return None
            else:
                offer = {
                    "offer_id": str(author_id) + "_" + await  Market.generate_uuid(),
                    "chicken": chicken,
                    "price": price,
                    "description": description,
                    "author_id": author_id,
                    "created_at": time()
                }
                await market_collection.insert_one(offer)
                log_info(f"Offer has been created successfully with id {offer_id}.")
        except Exception as e:
            log_error(f"Error encountered while creating the offer {offer_id}.", e)
            return None
    
    @staticmethod
    async def get(offer_id: int) -> Union[dict, None]:
        """
        Get an offer from the market collection.

        Args:
            offer_id (int): The id of the offer to get.
        
        Returns:
            Union[dict, None]
        """
        try:
            offer_data = await market_collection.find_one({"offer_id": offer_id})
            if offer_data:
                return offer_data
            else:
                log_warning(f"Offer {offer_id} does not exist.")
                return None
        except Exception as e:
            log_error(f"Error encountered while getting the offer {offer_id}.", e)
            return None
        
    @staticmethod
    async def update(offer_id: int, **kwargs) -> None:
        """
        Updates an offer in the market collection.

        Args:
            offer_id (int): The id of the offer to update.
            **kwargs: The keyword arguments to update the offer with.

        Returns:
            None
        """
        possible_keywords = ["chicken", "description", "author_id"]
        query = {}
        try:
            offer_data = await market_collection.find_one({"offer_id": offer_id})
            if offer_data:
                if kwargs:
                    for key, value in kwargs.items():
                        if key in possible_keywords:
                            query[key] = value
                    if query:
                        await market_collection.update_one({"offer_id": offer_id}, {"$set": query})
                        log_info(f"Offer {offer_id} has been updated successfully.")
                else:
                    log_warning(f"Keyword arguments aren't being passed for {offer_id}.")
            else:
                log_warning(f"Offer {offer_id} does not exist.")
        except Exception as e:
            log_error("Error encountered while updating the offer {offer_id}.", e)
            return None
    
    @staticmethod
    async def delete(offer_id: str) -> None:
        """
        Deletes an item from the market.

        Args:
            offer_id (int): The id of the offer to delete.

        Returns:
            None
        """
        try:
            offer_data = await market_collection.find_one({"offer_id": offer_id})
            if offer_data:
                await market_collection.delete_one({"offer_id": offer_id})
                log_info(f"Offer {offer_id} has been deleted successfully.")
            else:
                log_warning(f"Offer {offer_id} does not exist.")
        except Exception as e:
            log_error(f"Error encountered while deleting the offer {offer_id}.", e)
            return None
        
    @staticmethod
    async def bulk_delete(*offer_ids: str) -> None:
        """
        Deletes multiple offers from the market.

        Args:
            *offer_ids: The ids of the offers to delete.

        Returns:
            None
        """
        try:
            for offer_id in offer_ids:
                await market_collection.delete_one({"offer_id": offer_id})
            log_info(f"Offers {offer_ids} have been deleted successfully.")
        except Exception as e:
            log_error(f"Error encountered while deleting the offers {offer_ids}.", e)
            return None
    
    @staticmethod
    async def get_user_offers(author_id: int) -> Union[list, None]:
        """
        Get all offers from a user in the market collection.

        Args:
            author_id (int): The id of the user to get the offers from.

        Returns:
            Union[list, None]
        """
        try:
            offers = market_collection.find({"author_id": author_id}).sort("price", 1).limit(10)
            offers = await offers.to_list(length=10)
            if offers:
                return offers
            else:
                log_warning(f"User {author_id} has no offers.")
                return None
        except Exception as e:
            log_error(f"Error encountered while getting the offers for user {author_id}.", e)
            return None
                
    @staticmethod
    async def get_chicken_offers(**kwargs) -> Union[list, None]:
        """
        Performs search in the market collection based on the parameters provided.

        Args:
            **kwargs: The keyword arguments to search the offers with.

        Returns:
            Union[list, None]
        """
        query = {}
        possible_keywords = ["chicken_rarity", "upkeep_rarity", "price", "author_id"]
        for key, value in kwargs.items():
            if key not in possible_keywords:
                log_warning(f"Keyword {key} is not a valid keyword.")
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
            offers = await offers.to_list(length=10)
            if offers:
                return offers
            else:
                log_warning(f"No offers found with the parameters provided for the search.")
                return None
        except Exception as e:
            log_error(f"Error encountered while getting the offers with the parameters provided.", e)
            return None
        
    @staticmethod    
    async def count_all_offers() -> Union[int, None]:
        """
        Counts all offers in the market.

        Returns:
            Union[int, None]
        """
        try:
            count = await market_collection.count_documents({})
            return count
        except Exception as e:
            log_error("Error encountered while counting the offers.", e)
            return None
        
    @staticmethod
    async def generate_uuid() -> str:
        return str(uuid.uuid4())