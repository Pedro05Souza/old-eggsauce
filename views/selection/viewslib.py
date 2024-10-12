"""
Module containing general functions for the selection views.
"""
from discord import SelectOption
from lib.chickenlib import get_rarity_emoji, get_chicken_price

__all__ = ['chicken_options_initializer']

async def chicken_options_initializer(chickens: list, author_cached_data: dict, prohibited_rarities: list = []) -> list:
    """
    Initializes the options for the chicken selection.

    Args:
        chickens (list): A list of chickens to create the options for.
        author_cached_data (dict): The cached data of the author.
        prohibited_rarities (list): A list of prohibited rarities to not be included in the options.

    Returns:
        list
    """
    options = [
        SelectOption(
            label=f"{chicken['rarity']} {chicken['name']}",
            description=f"Price: {await get_chicken_price(chicken, author_cached_data['farm_data']['farmer'])}",
            value=str(index), 
            emoji=await get_rarity_emoji(chicken['rarity'])

        )
        for index, chicken in enumerate(chickens) if chicken['rarity'] not in prohibited_rarities
    ]
    return options
