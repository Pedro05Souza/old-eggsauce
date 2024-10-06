"""
Library module chickens.
"""
from random import randint, uniform, choice
from lib.chickenlib.chicken_info import *
from lib import send_bot_embed
from resources import *
from uuid import uuid4
from typing import Union
from random import randint
from discord.ext.commands import Context
import discord

__all__ = [
    "determine_chicken_upkeep", "get_chicken_egg_value", "get_chicken_price", 
    "load_farmer_upgrades", "get_rarity_emoji", "determine_upkeep_rarity_text", 
    "get_max_chicken_limit", "get_max_bench_limit", "get_user_bench", 
    "rank_determiner", "create_chicken", "generate_chicken_id", 
    "define_chicken_overrall_score", "devolve_chicken", "preview_corn_produced",
    "quick_sell_chicken", "decrease_chicken_happiness", "check_if_author", 
    "is_non_tradable_chicken", "get_non_tradable_chickens", "is_non_evolvable_chicken", 
    "get_non_evolvable_chickens", "is_non_market_place_chicken", "get_non_market_place_chickens", "is_non_devolvable_chicken", 
    "farm_maintence_tax"
    ]
            
async def determine_chicken_upkeep(chicken: dict) -> float:
    """
    Determine the chicken upkeep. Use this method to define a value for the chicken upkeep.

    Args:
        chicken (dict): The chicken to determine the upkeep for.

    Returns:
        float
    """
    percentage = uniform(0, .75)
    percentage = round(percentage, 2)
    chicken['upkeep_multiplier'] = percentage
    return chicken['upkeep_multiplier']

async def get_chicken_egg_value(chicken: dict) -> int:
    """
    Gets the chicken egg value.

    Args:
        chicken (dict): The chicken to get the egg value for.

    Returns:
        int
    """
    return ChickenMultiplier[chicken['rarity']].value

def get_chicken_price(chicken: dict, farmer: str = None) -> int:
    """
    Gets the chicken price.

    Args:
        chicken (dict): The chicken to get the price for.
        *args: The optinal farmer argument.

    Returns:
        int
    """	
    if farmer:  
        if farmer == 'Executive Farmer':
            farmer_upgrades = load_farmer_upgrades(farmer)
            discount_value = farmer_upgrades[1]
            default_discount = CHICKEN_DEFAULT_VALUE * (discount_value / 100)
            default_discount = int(default_discount)
            chicken_discount = CHICKEN_DEFAULT_VALUE - default_discount
            return ChickenRarity[chicken['rarity']].value * chicken_discount
        
    return ChickenRarity[chicken['rarity']].value * CHICKEN_DEFAULT_VALUE

def load_farmer_upgrades(farmer) -> Union[list, int]:
    """
    Loads the farmer upgrades

    Args:
        farmer (str): The farmer to load the upgrades for.

    Returns:
        Union[list, int]
    """
    farmer_dict = {
        "Rich Farmer": [15, 20],
        "Guardian Farmer": 5,
        "Executive Farmer" : [8, 20],
        "Warrior Farmer": 2,
        "Generous Farmer": [3],
        'Sustainable Farmer': [14600, [5, 40]]
    }
    return farmer_dict[farmer]
        
def get_rarity_emoji(rarity) -> str:
    """
    Gets the rarity emoji for the chicken.

    Args:
        rarity (str): The rarity of the chicken.

    Returns:
        str
    """
    return defineRarityEmojis[rarity]
        
def determine_upkeep_rarity_text(upkeep_multiplier: float) -> str:
        """
        Determines the text that will be displayed for the upkeep rarity.

        Args:
            upkeep_multiplier (float): The upkeep multiplier to determine the rarity for.

        Returns:
            str
        """
        chicken_upkeep = upkeep_multiplier
        for rarity, value in chicken_rarities.items():
            if chicken_upkeep >= value:
                return rarity
                 
def get_max_chicken_limit(farm_data: dict) -> int:
        """
        Gets the maximum chicken limit that can be stored in the farm.

        Args:
            farm_data (dict): The farm data to get the limit for.

        Returns:
            int
        """
        if farm_data['farmer'] == 'Warrior Farmer':
            return DEFAULT_FARM_SIZE + load_farmer_upgrades('Warrior Farmer')
        else:
            return DEFAULT_FARM_SIZE

async def get_max_bench_limit() -> int:
    """
    Gets the maximum bench limit that can be stored in the farm.

    Returns:
        int
    """
    return MAX_BENCH
        
async def get_user_bench(ctx: Context, farm_data: dict, user: discord.Member) -> discord.Embed:
    """
    Display the user's bench.

    Args:
        ctx (Context): The context of the command.
        farm_data (dict): The farm data to get the bench from.
        user (discord.Member): The user to get the bench for.

    Returns:
        discord.Embed
    """
    bench = farm_data['bench']
    await send_bot_embed(ctx, title=f":chair: {user.display_name}'s bench:", description="\n\n".join([f"{get_rarity_emoji(chicken['rarity'])} **{index + 1}**. **{chicken['rarity']} {chicken['name']}\n :gem: Upkeep rarity: {determine_upkeep_rarity_text(chicken['upkeep_multiplier'])} **" for index, chicken in enumerate(bench)])) if bench else await send_bot_embed(ctx, description="You have no chickens in your bench.")

async def rank_determiner(mmr: int) -> str:
    """
    Determines the text that will be displayed for the player's rank.

    Args:
        mmr (int): The mmr to determine the rank for.

    Returns:
        str
    """
    for key, value in reversed(chicken_ranking.items()):
        if mmr >= value:
            return key
    return len(chicken_ranking) - 1

async def create_chicken(rarity: str, author: str) -> Union[dict, None]:
    """"
    Creates a chicken dictionary.

    Args:
        rarity (str): The rarity of the chicken to create.
        author (str): which command is creating the chicken.

    Returns:
        Union[dict, None]
    """
    if rarity in ChickenRarity.__members__:

        chicken = {
                    "rarity": rarity,
                    "name": "Chicken",
                    "eggs_generated": 0,
                    "upkeep_multiplier": 0,
                    "chicken_id": await generate_chicken_id()
                    }
        
        if author == "bot":
            chicken["happiness"] = 100
        else:
            chicken["happiness"] = randint(60, 100)
        
        if rarity == "ETHEREAL":
            chicken['upkeep_multiplier'] = 0
        else:
            chicken['upkeep_multiplier'] = await determine_chicken_upkeep(chicken)

        return chicken
    return None

async def generate_chicken_id() -> int:
    """
    Generates a chicken id.

    Returns:
        int
    """
    return str(uuid4())

async def define_chicken_overrall_score(chickens: list) -> int:
        """
        Defines player's chickens overrall score.

        Args:
            chickens (list): The chickens to define the score for.

        Returns:
            int
        """
        chicken_overrall_score = 0

        for chicken in chickens:
            chicken_overrall_score += rarities_weight[chicken['rarity']]
            chicken_overrall_score += upkeep_weight[determine_upkeep_rarity_text(chicken['upkeep_multiplier'])]
        chicken_overrall_score -= farm_size_weights[len(chickens)]
        if chicken_overrall_score < 0:
            chicken_overrall_score = 0
        return chicken_overrall_score
            
async def devolve_chicken(chicken: dict) -> None:
        """
        10% chance of devolving a chicken if its happiness is at 0%.

        Args:
            chicken (dict): The chicken to devolve.

        Returns:
            None
        """
        devolveChance = randint(1, 10)
        cr = chicken['rarity']

        if await is_non_devolvable_chicken(cr):
            return

        if devolveChance == 1 and chicken['happiness'] <= 0:
            rarity_list = list(ChickenRarity)
            index = rarity_list.index(ChickenRarity[cr])
            devolded_rarity = rarity_list[index - 1].name
            chicken['happiness'] = 100
            chicken['rarity'] = devolded_rarity
            chicken['upkeep_multiplier'] = await determine_chicken_upkeep(chicken)
            return
        elif cr == 'COMMON' and chicken['happiness'] <= 0 and devolveChance == 1:
            chicken['rarity'] = 'DEAD'
            chicken['happiness'] = 0
            chicken['upkeep_multiplier'] = 0
            return

async def preview_corn_produced(farm_data: dict) -> int:
    """
    Previews the corn produced by the farm.

    Args:
        farm_data (dict): The farm data to preview the corn for.

    Returns:
        int
    """
    return farm_data['plot'] * CORN_PER_PLOT
             
async def quick_sell_chicken(ctx: Context, farm_data: dict, debt: int) -> int:
    """
    Quick sells a chicken to pay the debt.

    Args:
        ctx (Context): The context of the command.
        farm_data (dict): The farm data to sell the chicken from.
        debt (int): The debt to pay.

    Returns:
        int
    """
    random_chicken = choice(farm_data['chickens'])
    farm_data['chickens'].remove(random_chicken)
    money_earned = get_chicken_price(random_chicken)
    money_earned -= debt
    money_earned = max(0, money_earned)
    description =f":exclamation: Your {get_rarity_emoji(random_chicken['rarity'])} **{random_chicken['rarity']} {random_chicken['name']}** has been sold to pay the **{debt}** debt."
    if money_earned > 0:
        description += f"\n:moneybag: You have earned **{money_earned}**."
    await send_bot_embed(ctx, description=description)
    return money_earned

async def decrease_chicken_happiness(chicken: dict, hours_passed: int) -> dict:
    """
    Decreases the chicken happiness.

    Args:
        chicken (dict): The chicken to decrease the happiness for.
        hours_passed (int): The hours passed.

    Returns:
        dict
    """
    happiness_decreased = sum([randint(1, 3) for _ in range(hours_passed)])
    chicken['happiness'] = max(chicken['happiness'] - happiness_decreased, 0)
    return chicken

async def check_if_author(author_id: int, user_interaction_id: int, ctx: Context | discord.Interaction) -> None:
    """
    Checks if the author is the same as the user interaction.

    Args:
        author_id (int): The author id.
        user_interaction_id (int): The user interaction id.

    Returns:
        bool
    """
    if author_id != user_interaction_id:
        await send_bot_embed(ctx, ephemeral=True, description=":no_entry_sign: You can't interact with another user's chickens.")
        return False
    return True

async def is_non_tradable_chicken(chicken_rarity: str) -> bool:
    """
    Checks if the chicken is negotiable. (If the chicken can be sold to the market or traded with another user.)

    Args:
        chicken_rarity (str): The chicken rarity to check.

    Returns:
        bool
    """
    return chicken_rarity in non_trandable_chickens

async def get_non_tradable_chickens() -> set:
    """
    Gets the transferable chickens.

    Returns:
        set
    """
    return non_trandable_chickens

async def is_non_evolvable_chicken(chicken_rarity: str) -> bool:
    """
    Checks if the chicken is evolvable.

    Args:
        chicken_rarity (str): The chicken rarity to check.

    Returns:
        bool
    """
    return chicken_rarity in non_evolveable_chickens

async def get_non_evolvable_chickens() -> set:
    """
    Gets the evolvable chickens.

    Returns:
        set
    """
    return non_evolveable_chickens

async def is_non_market_place_chicken(chicken_rarity: str) -> bool:
    """
    Checks if the chicken can be placed in the player market.

    Args:
        chicken_rarity (str): The chicken rarity to check.

    Returns:
        bool
    """
    return chicken_rarity in non_marketplace_chickens

async def get_non_market_place_chickens() -> set:
    """
    Gets the non market place chickens.

    Returns:
        set
    """
    return non_marketplace_chickens

async def is_non_devolvable_chicken(chicken_rarity: str) -> bool:
    """
    Checks if the chicken can be devolved.

    Args:
        chicken_rarity (str): The chicken rarity to check.

    Returns:
        bool
    """
    return chicken_rarity in non_devolvable_chickens    

async def farm_maintence_tax(farm_data: Context, hours_passed=None) -> int:
    """
    Calculates the farm maintence tax.

    Args:
        farm_data (dict): The farm data to calculate the tax for.
        hours_passed (int): The hours passed that have passed.

    Returns:
        int
    """
    
    if not hours_passed:
        hours_passed = 1
    
    else:
        hours_passed = min(hours_passed, 24)

    player_plot = farm_data['plot']
    plot_delta_multiplier = player_plot / MAX_PLOT_LIMIT 
    plot_tax = MAX_PLOT_TAX_VALUE * plot_delta_multiplier

    player_corn_size = farm_data['corn_limit']
    corn_limit_delta_multiplier = player_corn_size / MAX_CORN_LIMIT
    corn_tax =  MAX_CORN_TAX_VALUE * corn_limit_delta_multiplier 

    chicken_rarity_weight = sum([rarities_weight[chicken['rarity']] for chicken in farm_data['chickens']])

    if chicken_rarity_weight <= 150:
         return 0
    
    chicken_rarity_weight /= 2200
    chicken_tax = chicken_rarity_weight
    chicken_tax = MAX_FARM_TAX_VALUE * chicken_tax
    
    total_tax = plot_tax + corn_tax + chicken_tax

    total_tax *= hours_passed

    if farm_data['farmer'] == 'Guardian Farmer':
        total_tax = total_tax - (total_tax * load_farmer_upgrades('Guardian Farmer') / 100)

    return int(total_tax) 