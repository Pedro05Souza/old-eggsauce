from random import randint, uniform
from time import time
from db.bankDB import Bank
from db.farmDB import Farm
from db.userDB import User
from db.marketDB import Market
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
    """
    percentage = uniform(0, .75)
    percentage = round(percentage, 2)
    chicken['upkeep_multiplier'] = percentage
    return chicken['upkeep_multiplier']

async def get_chicken_egg_value(chicken: dict) -> int:
    """
    Get the chicken egg value.
    """
    egg_value = ChickenMultiplier[chicken['rarity']].value
    return egg_value

def get_chicken_price(chicken: dict, *args) -> int:
    """Get the chicken price."""	
    if args:   
        farmer = args[0]
        if farmer == 'Executive Farmer':
            farmer_upgrades = load_farmer_upgrades(farmer)
            discount_value = farmer_upgrades[1]
            default_discount = chicken_default_value * (discount_value / 100)
            default_discount = int(default_discount)
            chicken_discount = chicken_default_value - default_discount
            chicken_price = (ChickenRarity[chicken['rarity']].value * chicken_discount)
            return chicken_price
    return ChickenRarity[chicken['rarity']].value * chicken_default_value

def load_farmer_upgrades(farmer) -> Union[list, int]:
        """Load the farmer upgrades"""
        farmer_dict = {
            "Rich Farmer": [10, 20],
            "Guardian Farmer": 5,
            "Executive Farmer" : [8, 20],
            "Warrior Farmer": 3,
            "Generous Farmer": [3],
            'Sustainable Farmer': [14600, [5, 40]]
        }
        return farmer_dict[farmer]
        
def get_rarity_emoji(rarity):
    """Get the rarity emoji for the chicken."""
    return defineRarityEmojis[rarity]

async def get_usr_farm(ctx: Context, user: discord.Member, data) -> discord.Embed:
        """Get the user's farm."""
        farm_data = data['farm_data']
        if farm_data:
            if user.id != ctx.author.id:
                 farm_data = await update_user_farm(ctx, user, data)
            farm_data = await get_player_chicken(ctx, user, data)
            if farm_data['farmer'] == 'Sustainable Farmer':
                await update_farmer(user, data)
            if len(farm_data['chickens']) == 0:
                return
            msg = await make_embed_object(
                title=f":chicken: {farm_data['farm_name']}\n:egg: **Eggs generated**: {await format_number(farm_data['eggs_generated'])}\n:farmer: Farmer: {farm_data['farmer'] if farm_data['farmer'] else 'No Farmer.'}",
                description="\n".join([
                f"{get_rarity_emoji(chicken['rarity'])}  **{index + 1}.** **{chicken['rarity']} {chicken['name']}** \n:partying_face: Happiness: **{chicken['happiness']}%**\n :gem: Upkeep rarity: **{determine_upkeep_rarity(chicken['upkeep_multiplier'])}**\n"
                for index, chicken in enumerate(farm_data['chickens'])
            ]))
            msg.set_thumbnail(url=user.display_avatar)
            msg.set_footer(text=tips[randint(0, len(tips) - 1)])
            return msg
        else:
            return None
        
def determine_upkeep_rarity(upkeep_multiplier: float) -> str:
        """
        Determine the text that will be displayed for the upkeep rarity.
        """
        chicken_upkeep = upkeep_multiplier
        for rarity, value in chicken_rarities.items():
            if chicken_upkeep >= value:
                return rarity
                 
def get_max_chicken_limit(farm_data: dict) -> int:
        """
        Get the maximum chicken limit that can be stored in the farm.
        """
        if farm_data['farmer'] == 'Warrior Farmer':
            return default_farm_size + load_farmer_upgrades('Warrior Farmer')
        else:
            return default_farm_size
        
async def verify_events(ctx: Context, user: discord.Member):
        """Verify if the user is in an event. This method should be called whenever a user is performing critical actions
        that could duplicate the chicken data.
        Example: Selling a chicken and starting a trade with another user, if you trade before selling the chicken, the chicken duplicates."""
        if EventData.check_user_in_event(user.id):
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} is already in an event.")
            return True
        return False
      
async def get_user_bench(ctx: Context, farm_data: dict, user: discord.Member) -> discord.Embed:
     """
     Display the user's bench.
     """
     bench = farm_data['bench']
     await send_bot_embed(ctx, title=f":chair: {user.display_name}'s bench:", description="\n\n".join([f"{get_rarity_emoji(chicken['rarity'])} **{index + 1}**. **{chicken['rarity']} {chicken['name']}\n :gem: Upkeep rarity: {determine_upkeep_rarity(chicken['upkeep_multiplier'])} **" for index, chicken in enumerate(bench)])) if bench else await send_bot_embed(ctx, description="You have no chickens in your bench.")

async def rank_determiner(mmr: int) -> str:
     """
     Determines the text that will be displayed for the player's rank.
     """
     for key, value in reversed(chicken_ranking.items()):
         if mmr >= value:
             return key
     return len(chicken_ranking) - 1

async def create_chicken(rarity: str, author: str) -> Union[dict, None]:
     """"
     Create a chicken.
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
        """
        chicken_overrall_score = 0
        for chicken in chickens:
            chicken_overrall_score += rarities_weight[chicken['rarity']]
            chicken_overrall_score += upkeep_weight[determine_upkeep_rarity(chicken['upkeep_multiplier'])]
        chicken_overrall_score -= farm_size_weights[len(chickens)]
        if chicken_overrall_score < 0:
            chicken_overrall_score = 0
        return chicken_overrall_score

# updates

async def drop_egg_for_player(farm_data: dict, hours_passed: int) -> Union[dict, int]:
        """
        Calculate the eggs generated by the farm.
        """
        farm_dictionary = {}
        farm_data_copy = farm_data['chickens'].copy()
        total_profit = await give_total_farm_profit(farm_data, hours_passed)
        if total_profit > 0:
            farm_data['eggs_generated'] += min(total_profit, max_egg_generated)
        farm_data['chickens'] = farm_data_copy
        farm_dictionary = {
                           "chickens" : farm_data['chickens'],
                           "eggs_generated" : farm_data['eggs_generated']
        }
        farm_data['chickens'] = farm_dictionary['chickens']
        farm_data['eggs_generated'] = farm_dictionary['eggs_generated']
        return farm_data, total_profit
                    
async def feed_eggs_auto(farm_data: dict, bank_amount: int) -> int:
    """
    Feed the chickens automatically
    """
    total_upkeep = 0
    random_range = load_farmer_upgrades('Sustainable Farmer')[1]
    if farm_data['farmer'] == "Sustainable Farmer":
        for chicken in farm_data['chickens']:
            if chicken['happiness'] == 100:
                continue
            generated_happiness = randint(random_range[0], random_range[1])
            cHappiness = chicken['happiness'] + generated_happiness
            if cHappiness > 100:
                cHappiness = 100
            chicken['happiness'] = cHappiness
            chicken_loss = int(await get_chicken_egg_value(chicken) * chicken['upkeep_multiplier'])
            total_upkeep += chicken_loss
        if bank_amount < total_upkeep:
            return 0
        return total_upkeep

async def update_user_farm(ctx: Context, user: discord.Member, data: dict) -> Union[dict, None]:
    """
    Update the user's farm.
    """
    if not data['farm_data']:
        return None, 0
    farm_data = data['farm_data']
    if len(farm_data['chickens']) == 0:
        return farm_data, 0
    last_drop_time = time() - farm_data['last_chicken_drop']
    updated_farm_data = farm_data
    hours_passed_since_last_egg_drop = min((last_drop_time // farm_drop), 24)
    total_profit = 0
    if hours_passed_since_last_egg_drop != 0:
        hours_passed_since_last_egg_drop = int(hours_passed_since_last_egg_drop)
        user_data = data['user_data']
        updated_farm_data, total_money_earned_without_tax = await drop_egg_for_player(farm_data, hours_passed_since_last_egg_drop)
        farm_data = updated_farm_data
        taxes = await farm_maintence_tax(farm_data, hours_passed=hours_passed_since_last_egg_drop)
        total_profit = await update_user_points(ctx, user_data, data['bank_data'], updated_farm_data, taxes, total_money_earned_without_tax)
        Farm.update_chicken_drop(user.id)
        Farm.update(user.id, chickens=updated_farm_data['chickens'], eggs_generated=updated_farm_data['eggs_generated'])
    return updated_farm_data, total_profit

async def update_farmer(user: discord.Member, data: dict) -> None:
    """Update the farmer. Needs refactoring."""
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
            Bank.update(farm_data['user_id'], bank_amount)
            Farm.update(farm_data['user_id'], chickens=farm_data['chickens'], eggs_generated=farm_data['eggs_generated'])
            Farm.update_farmer_drop(user.id)
            
async def devolve_chicken(chicken: dict) -> None:
        """ 33% chance of devolving a chicken if its happiness is at 0%."""
        devolveChance = randint(1, 10)
        cr = chicken['rarity']
        if cr in ChickenRarity.__members__ and cr != 'COMMON':
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
    """Update the player's corn."""
    if not data:
        return 0
    farm_data = data
    last_drop_time = time() - farm_data['last_corn_drop']
    hours_passed_since_last_drop = min(last_drop_time // farm_drop, 24)
    corn_produced = 0
    current_corn = farm_data['corn']
    if hours_passed_since_last_drop != 0:
        corn_produced = await calculate_corn(farm_data, hours_passed_since_last_drop)
        current_corn += corn_produced
        current_corn = min(current_corn, farm_data['corn_limit'])
        Farm.update_corn_drop(user.id)
        Farm.update(user.id, corn=current_corn)
    return current_corn, corn_produced

async def calculate_corn(farm_data: dict, hours_passed: int) -> int:
    """Calculate the corn generated by the farm."""
    corn_produced = farm_data['plot'] * corn_per_plot   
    corn_produced *= hours_passed
    if farm_data['farmer'] == 'Rich Farmer':
        corn_produced += corn_produced * load_farmer_upgrades('Rich Farmer')[1] / 100
    corn_produced = int(corn_produced)
    return corn_produced

async def preview_corn_produced(farm_data: dict) -> int:
    """
    Preview the corn produced by the farm.
    """
    return farm_data['plot'] * corn_per_plot
        
async def get_player_chicken(ctx: Context, user: discord.Member, data):
     """Retrieves the player's chickens from market offers."""
     farm_data = data['farm_data']
     market_data = Market.get_user_offers(user.id)
     offers_list = []
     chickens_added = []
     for offer in market_data:
        last_offer_time = time() - offer['created_at']
        if last_offer_time // 3600 > offer_expire_time:
             offers_list.append(offer)
     if offers_list:
            offers_to_process = offers_list.copy()
            for offer in offers_to_process:
                chicken = offer['chicken']
                var = farm_data['chickens'] + [chicken]
                if len(var) > get_max_chicken_limit(farm_data):
                    break
                farm_data['chickens'] = var
                offers_list.remove(offer)
                chickens_added.append(chicken)
                Market.delete(offer['offer_id'])
            if chickens_added:
                chicken_desc = "\n\n".join([f" {get_rarity_emoji(chicken['rarity'])} **{chicken['rarity']} {chicken['name']}**" for chicken in chickens_added])
                await send_bot_embed(ctx, description=f":white_check_mark: {user.display_name}, you have successfully added the following chickens to your farm: \n\n{chicken_desc}\n Those chickens have been removed from the market.")
                Farm.update(user.id, chickens=farm_data['chickens'])
            if offers_list:
                chicken_desc = "\n\n".join([f" {get_rarity_emoji(chicken['rarity'])} **{chicken['rarity']} {chicken['name']}**" for offer in offers_list for chicken in [offer['chicken']]])
                await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name}, you can't add the following chickens to your farm: \n\n{chicken_desc}\n They have been automatically put back in the market.")
     return farm_data

async def farm_maintence_tax(farm_data: Context, **kwargs) -> int:
    """
    Calculates the farm maintence tax.
    """
    hours_passed = None
    
    if kwargs:
        hours_passed = kwargs['hours_passed']

    player_plot = farm_data['plot']
    plot_delta_multiplier = player_plot / max_plot_limit 
    plot_tax = max_plot_tax_value * plot_delta_multiplier

    player_corn_size = farm_data['corn_limit']
    corn_limit_delta_multiplier = player_corn_size / max_corn_limit
    corn_tax =  max_corn_tax_value * corn_limit_delta_multiplier 

    chicken_rarity_weight = sum([rarities_weight[chicken['rarity']] for chicken in farm_data['chickens']])
    if chicken_rarity_weight <= 150:
         return 0
    
    chicken_rarity_weight /= 2200
    chicken_tax = chicken_rarity_weight
    chicken_tax = max_farm_tax_value * chicken_tax
    
    total_tax = plot_tax + corn_tax + chicken_tax

    if hours_passed:
        total_tax *= hours_passed
    if farm_data['farmer'] == 'Guardian Farmer':
        total_tax = total_tax - (total_tax * load_farmer_upgrades('Guardian Farmer') / 100)

    return int(total_tax)

async def update_user_points(ctx: Context, user_data: dict, bank_data: dict, farm_data: dict, taxes: int, total_profit: int) -> int:
    """Update the user's points."""
    user_data['points'] += total_profit
    profit_with_taxes = total_profit - taxes

    if user_data['points'] >= taxes:
         user_data['points'] -= taxes
         User.update_points(user_data['user_id'], user_data['points'])
    elif bank_data['bank'] >= taxes:
        bank_data['bank'] -= taxes
        Bank.update(user_data['user_id'], bank_data['bank'])
    elif user_data['points'] + bank_data['bank'] >= taxes:
        difference = taxes - user_data['points']
        user_data['points'] = 0
        bank_data['bank'] -= difference
        Bank.update(user_data['user_id'], bank_data['bank'])
        User.update_points(user_data['user_id'], user_data['points'])
    else:
        debt = taxes - user_data['points'] - bank_data['bank']
        money_earned = await quick_sell_chicken(ctx, farm_data, debt)
        User.update_points(user_data['user_id'], user_data['points'] + money_earned)
        return 0
     
    await on_user_transaction(ctx, profit_with_taxes, 0 if profit_with_taxes > 0 else 1)
    return profit_with_taxes
     
async def quick_sell_chicken(ctx: Context, farm_data: dict, debt: int) -> int:
    """
    Quick sell a chicken to pay the debt.
    """
    random_chicken = farm_data['chickens'][randint(0, len(farm_data['chickens']) - 1)]
    farm_data['chickens'].remove(random_chicken)
    money_earned = get_chicken_price(random_chicken)
    money_earned -= debt
    money_earned = max(0, money_earned)
    description =f":exclamation: Your {get_rarity_emoji(random_chicken['rarity'])} **{random_chicken['rarity']} {random_chicken['name']}** has been sold to pay the **{debt}** debt."
    if money_earned > 0:
        description += f"\n:moneybag: You have earned **{money_earned}**."
    await send_bot_embed(ctx, description=description)
    return money_earned

async def give_total_farm_profit(farm_data: dict, hours_passed: int) -> int:
     """
     Give the total farm profit.
     """
     total_profit = 0
     for chicken in farm_data['chickens']:
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

     if farm_data['farmer'] == 'Rich Farmer':
            to_increase = (total_profit * load_farmer_upgrades('Rich Farmer')[0]) // 100
            total_profit += to_increase
     return total_profit

async def decrease_chicken_happiness(chicken: dict, hours_passed: int) -> dict:
    """
    Decrease the chicken happiness.
    """
    happiness_decreased = sum([randint(1, 3) for _ in range(hours_passed)])
    chicken['happiness'] = max(chicken['happiness'] - happiness_decreased, 0)
    return chicken
     