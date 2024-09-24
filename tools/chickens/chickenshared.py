"""
This module provides essential functions and utilities that support the core operations of the chicken management system.
"""
from random import randint, uniform, choice
from time import time
from db.bankdb import Bank
from db.farmdb import Farm
from db.userdb import User
from db.marketdb import Market
from tools.chickens.chickenhandlers import EventData
from tools.chickens.chickeninfo import *
from tools.shared import send_bot_embed, make_embed_object, format_number
from tools.listeners import on_user_transaction
from tools.settings import *
from tools.tips import tips
from typing import Union
from random import randint
from discord.ext.commands import Context
import discord
import logging
logger = logging.getLogger('botcore')

# Shared functions between the chicken commands
            
def determine_chicken_upkeep(chicken: dict) -> float:
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

async def get_usr_farm(ctx: Context, user: discord.Member, data) -> discord.Embed:
        """
        Gets the user's farm.

        Args:
            ctx (Context): The context of the command.
            user (discord.Member): The user to get the farm for.
            data (dict): The data to get the farm from.

        Returns:
            discord.Embed
        """
        farm_data = data['farm_data']
        
        if farm_data:

            farm_data = await get_player_chicken_from_market(ctx, user, data)

            if len(farm_data['chickens']) == 0:
                return

            if farm_data['farmer'] == 'Sustainable Farmer':
                await update_farmer(user, data)

            msg = await make_embed_object(
                title=
                f":chicken: {farm_data['farm_name']}\n:egg: **Eggs generated**: {await format_number(farm_data['eggs_generated'])}\n:farmer: Farmer: {farm_data['farmer'] if farm_data['farmer'] else 'No Farmer.'}",
                description="\n".join([
                f"{get_rarity_emoji(chicken['rarity'])}  **{index + 1}.** **{chicken['rarity']} {chicken['name']}** \n:partying_face: Happiness: **{chicken['happiness']}%**\n :gem: Upkeep rarity: **{determine_upkeep_rarity_text(chicken['upkeep_multiplier'])}**\n"
                for index, chicken in enumerate(farm_data['chickens'])
            ]))
            msg.set_thumbnail(url=user.display_avatar)
            msg.set_footer(text=tips[randint(0, len(tips) - 1)])
            return msg
        else:
            return None
        
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
        
async def verify_events(ctx: Context, user: discord.Member):
        """Verify if the user is in an event. This method should be called whenever a user is performing critical actions
        that could duplicate the chicken data.
        Example: Selling a chicken and starting a trade with another user, if you trade before selling the chicken, the chicken duplicates.

        Args:
            ctx (Context): The context of the command.
            user (discord.Member): The user to verify the event for.

        Returns:
            bool
        """
        if EventData.check_user_in_event(user.id):
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} is already in an event.")
            return True
        return False
      
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
                    }
        
        if author == "bot":
            chicken["happiness"] = 100
        else:
            chicken["happiness"] = randint(60, 100)
        
        if rarity == "ETHEREAL":
            chicken['upkeep_multiplier'] = 0
        else:
            chicken['upkeep_multiplier'] = determine_chicken_upkeep(chicken)

        return chicken
    return None

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

# updates

async def drop_egg_for_player(farm_data: dict, hours_passed: int) -> Union[dict, int]:
        """
        Calculates the eggs generated by the farm.

        Args:
            farm_data (dict): The farm data to calculate the eggs for.
            hours_passed (int): The hours passed.

        Returns:
            Union[dict, int]
        """
        total_profit, farm_data = await give_total_farm_profit(farm_data.copy(), hours_passed)
        if total_profit > 0:
            farm_data['eggs_generated'] += min(total_profit, MAX_EGG_GENERATED)
        return farm_data, total_profit
                    
async def feed_eggs_auto(farm_data: dict, bank_amount: int) -> int:
    """
    Feeds the chickens automatically.

    Args:
        farm_data (dict): The farm data to feed the chickens for.
        bank_amount (int): The bank amount to feed the chickens with.

    Returns:
        int
    """
    total_upkeep = 0

    if farm_data['farmer'] == "Sustainable Farmer":
        random_range = load_farmer_upgrades('Sustainable Farmer')[1]
        for chicken in farm_data['chickens']:
            if chicken['happiness'] == 100:
                continue
            generated_happiness = randint(random_range[0], random_range[1])
            cHappiness = chicken['happiness'] + generated_happiness
            if cHappiness > 100:
                cHappiness = 100
            chicken['happiness'] = cHappiness
            chicken_cost = int(await get_chicken_egg_value(chicken) * chicken['upkeep_multiplier'])
            total_upkeep += chicken_cost

        if bank_amount < total_upkeep:
            return 0
        
        return total_upkeep

async def update_user_farm(ctx: Context, user: discord.Member, data: dict) -> tuple[dict, int]:
    """
    Updates the user's farm.

    Args:
        ctx (Context): The context of the command.
        user (discord.Member): The user to update the farm for.
        data (dict): The data to update the farm from.

    Returns:
        Union[dict, None]
    """
    if not data['farm_data']:
        return None, 0
    
    farm_data = data['farm_data']

    if len(farm_data['chickens']) == 0:
        return farm_data, 0
    
    last_drop_time = time() - farm_data['last_chicken_drop']
    updated_farm_data = farm_data
    hours_passed_since_last_egg_drop = min((last_drop_time // FARM_DROP), 24)
    hours_passed_since_last_egg_drop = int(hours_passed_since_last_egg_drop)
    total_profit = 0

    if hours_passed_since_last_egg_drop != 0:
        user_data = data['user_data']
        updated_farm_data, total_money_earned_without_tax = await drop_egg_for_player(farm_data, hours_passed_since_last_egg_drop)
        farm_data = updated_farm_data
        taxes = await farm_maintence_tax(farm_data, hours_passed_since_last_egg_drop)
        total_profit = await update_user_points(ctx, user_data, data['bank_data'], updated_farm_data, taxes, total_money_earned_without_tax)
        await Farm.update_chicken_drop(user.id)
        await Farm.update(user.id, chickens=updated_farm_data['chickens'], eggs_generated=updated_farm_data['eggs_generated'])

    return updated_farm_data, total_profit

async def update_farmer(user: discord.Member, data: dict) -> None:
    """
    Feeds the chickens automatically for the sustainable farmer.

    Args:
        user (discord.Member): The user to update the farmer for.
        data (dict): The data to update the farmer from.

    Returns:
        None
    """
    farm_data = data['farm_data']
    last_drop_time = time() - farm_data['last_farmer_drop']
    hours_passed_since_feed = 0
    bank_data = data['bank_data']
    bank_amount = bank_data['bank']
    if farm_data['farmer'] == "Sustainable Farmer":
        hours_passed_since_feed = min(last_drop_time // load_farmer_upgrades('Sustainable Farmer')[0], 2)
        for _ in range(int(hours_passed_since_feed)):
            total_upkeep = await feed_eggs_auto(farm_data, bank_amount)
            bank_amount -= total_upkeep
            if total_upkeep == 0:
                break
            if bank_amount < total_upkeep:
                break
        if hours_passed_since_feed != 0:
            await Bank.update(farm_data['user_id'], bank_amount)
            await Farm.update(farm_data['user_id'], chickens=farm_data['chickens'], eggs_generated=farm_data['eggs_generated'])
            await Farm.update_farmer_drop(user.id)
            
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
            chicken['upkeep_multiplier'] = determine_chicken_upkeep(chicken)
            return
        elif cr == 'COMMON' and chicken['happiness'] <= 0 and devolveChance == 1:
            chicken['rarity'] = 'DEAD'
            chicken['happiness'] = 0
            chicken['upkeep_multiplier'] = 0
            return

async def update_player_corn(user: discord.Member, data: dict) -> int:
    """
    Updates the player's corn.

    Args:
        user (discord.Member): The user to update the corn for.
        data (dict): The data to update the corn from.

    Returns:
        int
    """
    if not data:
        return 0
    farm_data = data
    last_drop_time = time() - farm_data['last_corn_drop']
    hours_passed_since_last_drop = min(last_drop_time // FARM_DROP, 24)
    corn_produced = 0
    current_corn = farm_data['corn']
    if hours_passed_since_last_drop != 0:
        corn_produced = await calculate_corn(farm_data, hours_passed_since_last_drop)
        current_corn += corn_produced
        current_corn = min(current_corn, farm_data['corn_limit'])
        await Farm.update_corn_drop(user.id)
        await Farm.update(user.id, corn=current_corn)
    return current_corn, corn_produced

async def calculate_corn(farm_data: dict, hours_passed: int) -> int:
    """
    Calculates the corn generated by the farm.

    Args:
        farm_data (dict): The farm data to calculate the corn for.
        hours_passed (int): The hours passed.

    Returns:
        int
    """
    corn_produced = farm_data['plot'] * CORN_PER_PLOT   
    corn_produced *= hours_passed
    if farm_data['farmer'] == 'Rich Farmer':
        corn_produced += corn_produced * load_farmer_upgrades('Rich Farmer')[1] / 100
    corn_produced = int(corn_produced)
    return corn_produced

async def preview_corn_produced(farm_data: dict) -> int:
    """
    Previews the corn produced by the farm.

    Args:
        farm_data (dict): The farm data to preview the corn for.

    Returns:
        int
    """
    return farm_data['plot'] * CORN_PER_PLOT
        
async def get_player_chicken_from_market(ctx: Context, user: discord.Member, data):
    """
     Retrieves the player's chickens from market offers.

    Args:
        ctx (Context): The context of the command.
        user (discord.Member): The user to get the chickens for.
        data (dict): The data to get the chickens from.

    Returns:
        dict
    """
    farm_data = data['farm_data']
    market_data = await Market.get_user_offers(user.id)
    offers_list = []

    if not market_data:
        return farm_data
    for offer in market_data:
        last_offer_time = time() - offer['created_at']
        if last_offer_time // 3600 > OFFER_EXPIRE_TIME:
                offers_list.append(offer)
    if offers_list:
        await chicken_retriever_handler(ctx, user, farm_data, offers_list)

    return farm_data

async def chicken_retriever_handler(ctx: Context, user: discord.Member, farm_data: dict, offers_list: list) -> None:
    """
    Retrieves the player's chickens from market offers if they are expired.

    Args:
        ctx (Context): The context of the command.
        user (discord.Member): The user to get the chickens for.
        farm_data (dict): The farm data to get the chickens for.
        offers_list (list): The offers list to get the chickens from.

    Returns:
        None
    """
    offers_to_process = offers_list.copy()
    chickens_added = []
    for offer in offers_to_process:
        chicken = offer['chicken']
        var = farm_data['chickens'] + [chicken]
        if len(var) > get_max_chicken_limit(farm_data):
            break
        farm_data['chickens'] = var
        offers_list.remove(offer)
        chickens_added.append(chicken)
        await Market.delete(offer['offer_id'])
    if chickens_added:
        chicken_desc = "\n\n".join([f" {get_rarity_emoji(chicken['rarity'])} **{chicken['rarity']} {chicken['name']}**" for chicken in chickens_added])
        await send_bot_embed(ctx, description=f":white_check_mark: {user.display_name}, you have successfully added the following chickens to your farm: \n\n{chicken_desc}\n Those chickens have been removed from the market.")
        await Farm.update(user.id, chickens=farm_data['chickens'])
    if offers_list:
        chicken_desc = "\n\n".join([f" {get_rarity_emoji(chicken['rarity'])} **{chicken['rarity']} {chicken['name']}**" for offer in offers_list for chicken in [offer['chicken']]])
        await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name}, you can't add the following chickens to your farm: \n\n{chicken_desc}\n They have been automatically put back in the market.")

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

async def update_user_points(ctx: Context, user_data: dict, bank_data: dict, farm_data: dict, taxes: int, total_profit: int) -> int:
    """
    Updates the user's points after the farm has been calculated.

    Args:
        ctx (Context): The context of the command.
        user_data (dict): The user data to update the points for.
        bank_data (dict): The bank data to update the points for.
        farm_data (dict): The farm data to update the points for.
        taxes (int): The taxes to pay.
        total_profit (int): The total profit.

    Returns:
        int
    """
    user_data['points'] += total_profit
    profit_with_taxes = total_profit - taxes

    if user_data['points'] >= taxes:
        user_data['points'] -= taxes
        await User.update_points(user_data['user_id'], user_data['points'])
    elif bank_data['bank'] >= taxes:
        bank_data['bank'] -= taxes
        await Bank.update(user_data['user_id'], bank_data['bank'])
    elif user_data['points'] + bank_data['bank'] >= taxes:
        difference = taxes - user_data['points']
        user_data['points'] = 0
        bank_data['bank'] -= difference
        await Bank.update(user_data['user_id'], bank_data['bank'])
        await User.update_points(user_data['user_id'], user_data['points'])
    else:
        debt = taxes - user_data['points'] - bank_data['bank']
        money_earned = await quick_sell_chicken(ctx, farm_data, debt)
        await User.update_points(user_data['user_id'], user_data['points'] + money_earned)
        return 0
     
    await on_user_transaction(ctx, profit_with_taxes, 0 if profit_with_taxes > 0 else 1)
    return profit_with_taxes
     
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

async def give_total_farm_profit(farm_data_copy: dict, hours_passed: int) -> int:
    """
    Gives the total farm profit.

    Args:
        farm_data_copy (dict): The copy of a farm data to give the profit for.
        hours_passed (int): The hours passed.

    Returns:
        int
    """
    total_profit = 0
    for chicken in farm_data_copy['chickens']:

        if chicken['rarity'] == 'DEAD':
            continue

        egg_value = await get_chicken_egg_value(chicken)
        chicken_loss = int(egg_value * chicken['upkeep_multiplier'])
        chicken_profit = egg_value - chicken_loss
        total_profit += ((chicken_profit * chicken['happiness']) * hours_passed) // 100
        chicken['eggs_generated'] += chicken_profit
        chicken = await decrease_chicken_happiness(chicken, hours_passed)

        if chicken['happiness'] == 0:
            await devolve_chicken(chicken)

    if farm_data_copy['farmer'] == 'Rich Farmer':
        to_increase = (total_profit * load_farmer_upgrades('Rich Farmer')[0]) // 100
        total_profit += to_increase

    return total_profit, farm_data_copy

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
     