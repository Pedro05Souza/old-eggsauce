from random import randint, uniform
from time import time
from db.bankDB import Bank
from db.farmDB import Farm
from db.userDB import User
from db.MarketDB import Market
from tools.chickens.chickenhandlers import EventData
from tools.shared import user_cache_retriever
from tools.chickens.chickeninfo import *
from tools.shared import send_bot_embed, make_embed_object
from tools.tips import tips
from random import randint
import discord
import logging
import math
logger = logging.getLogger('botcore')

# Shared functions for the chicken commands
            
def determine_chicken_upkeep(chicken):
    percentage = uniform(0, .75)
    percentage = round(percentage, 2)
    chicken['upkeep_multiplier'] = percentage
    return chicken['upkeep_multiplier']

async def get_chicken_egg_value(chicken):
     egg_value = ChickenMultiplier[chicken['rarity']].value
     return egg_value

def get_chicken_price(chicken, *args):
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

def load_farmer_upgrades(farmer):
        """Load the farmer upgrades"""
        farmer_dict = {
            "Rich Farmer": [10, 20],
            "Guardian Farmer": 3,
            "Executive Farmer" : [8, 20],
            "Warrior Farmer": 3,
            "Generous Farmer": [3],
            'Sustainable Farmer': [14600, [5, 40]]
        }
        return farmer_dict[farmer]
        
def get_rarity_emoji(rarity):
    return defineRarityEmojis[rarity]

async def get_usr_farm(ctx, user: discord.Member):
        """Get the user's farm"""
        data = await user_cache_retriever(user.id)
        farm_data = await update_user_farm(user, data['farm_data'])
        if farm_data:
            farm_data = await get_player_chicken(ctx, user, farm_data)
            await update_farmer(user, farm_data)
            if len(farm_data['chickens']) == 0:
                return
            msg = await make_embed_object(
                title=f":chicken: {farm_data['farm_name']}\n:egg: **Eggs generated**: {farm_data['eggs_generated']}\n:farmer: Farmer: {farm_data['farmer'] if farm_data['farmer'] else 'No Farmer.'}",
                description="\n".join([
                f"{get_rarity_emoji(chicken['rarity'])}  **{index + 1}.** **{chicken['rarity']} {chicken['name']}** \n:partying_face: Happiness: **{chicken['happiness']}%**\n :gem: Upkeep rarity: **{determine_upkeep_rarity(chicken['upkeep_multiplier'])}**\n"
                for index, chicken in enumerate(farm_data['chickens'])
            ]))
            msg.set_thumbnail(url=user.display_avatar)
            msg.set_footer(text=tips[randint(0, len(tips) - 1)])
            return msg
        else:
            return None
        
def determine_upkeep_rarity(upkeep_multiplier):
        """Determine the upkeep rarity"""
        chicken_upkeep = upkeep_multiplier
        for rarity, value in chicken_rarities.items():
            if chicken_upkeep >= value:
                return rarity
                 
def get_max_chicken_limit(farm_data):
        """Get the maximum chicken limit"""
        if farm_data['farmer'] == 'Warrior Farmer':
            return default_farm_size + load_farmer_upgrades('Warrior Farmer')
        else:
            return default_farm_size
        
async def verify_events(ctx, user: discord.Member):
        """Verify if the user is in an event."""
        if EventData.check_user_in_event(user.id):
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} is already in an event.")
            return True
        return False
     
        
async def get_user_bench(ctx, farm_data, user: discord.Member):
     """Gets the user's bench"""
     bench = farm_data['bench']
     await send_bot_embed(ctx, title=f":chair: {user.display_name}'s bench:", description="\n\n".join([f"{get_rarity_emoji(chicken['rarity'])} **{index + 1}**. **{chicken['rarity']} {chicken['name']}\n :gem: Upkeep rarity: {determine_upkeep_rarity(chicken['upkeep_multiplier'])} **" for index, chicken in enumerate(bench)])) if bench else await send_bot_embed(ctx, description="You have no chickens in your bench.")


async def rank_determiner(mmr):
     """Determines the players rank."""
     for key, value in reversed(chicken_ranking.items()):
         if mmr >= value:
             return key
     return len(chicken_ranking) - 1


async def create_chicken(rarity, author):
     """"Create a chicken"""
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

async def define_chicken_overrall_score(chickens):
        """Defines the chicken overall score."""
        chicken_overrall_score = 0
        for chicken in chickens:
            chicken_overrall_score += rarities_weight[chicken['rarity']]
            chicken_overrall_score += upkeep_weight[determine_upkeep_rarity(chicken['upkeep_multiplier'])]
        chicken_overrall_score -= farm_size_weights[len(chickens)]
        if chicken_overrall_score < 0:
            chicken_overrall_score = 0
        return chicken_overrall_score

# updates

async def drop_egg_for_player(farm_data, user_data):
        """Drops eggs for player"""
        user_dictionary = {}
        farm_dictionary = {}
        total_profit = 0
        if not farm_data['chickens']:
            return farm_data
        farm_data_copy = farm_data['chickens'].copy()
        for chicken in farm_data_copy:
            if chicken['rarity'] == 'DEAD':
                continue
            chicken_loss = int(await get_chicken_egg_value(chicken) * chicken['upkeep_multiplier'])
            chicken_profit = await get_chicken_egg_value(chicken) - chicken_loss
            total_profit += (chicken_profit * chicken['happiness']) // 100
            chicken['happiness'] -= randint(1,3)
            if chicken['happiness'] < 0:
                chicken['happiness'] = 0
            if chicken['happiness'] == 0:
                await devolve_chicken(chicken)
        if farm_data['farmer'] == 'Rich Farmer':
            to_increase = (total_profit * load_farmer_upgrades('Rich Farmer'))[0] // 100
            total_profit += to_increase
        farm_data['eggs_generated'] += total_profit
        user_data['points'] += total_profit
        farm_data['chickens'] = farm_data_copy
        farm_dictionary = {
                           "chickens" : farm_data['chickens'],
                           "eggs_generated" : farm_data['eggs_generated']
        }
        user_dictionary = {
                            "points" : user_data['points']
          }
        farm_data['chickens'] = farm_dictionary['chickens']
        farm_data['eggs_generated'] = farm_dictionary['eggs_generated']
        user_data['points'] = user_dictionary['points']
        return farm_data
                    
async def feed_eggs_auto(farm_data, bank_amount): 
    """Feed the chickens automatically"""
    total_upkeep = 0
    random_range = load_farmer_upgrades('Sustainable Farmer')[1]
    if farm_data['farmer'] == "Sustainable Farmer":
        for chicken in farm_data['chickens']:
            if chicken['happiness'] == 100:
                continue
            generated_happines = randint(random_range[0], random_range[1])
            cHappiness = chicken['happiness'] + generated_happines
            if cHappiness > 100:
                cHappiness = 100
            chicken['happiness'] = cHappiness
            chicken_loss = int(await get_chicken_egg_value(chicken) * chicken['upkeep_multiplier'])
            total_upkeep += chicken_loss
        if bank_amount < total_upkeep:
            return 0
        return total_upkeep

async def update_user_farm(user, farm_data):
    if not farm_data:
        return None
    last_drop_time = time() - farm_data['last_chicken_drop']
    updated_farm_data = farm_data
    hours_passed_since_last_egg_drop = min(last_drop_time // 7200, 24)
    user_data = await user_cache_retriever(user.id)
    user_data = user_data['user_data']
    taxes = 0
    for _ in range(int(hours_passed_since_last_egg_drop)):
        updated_farm_data = await drop_egg_for_player(farm_data, user_data)
        taxes += await farm_maintence_tax(updated_farm_data)
    if hours_passed_since_last_egg_drop != 0:
        Farm.update_chicken_drop(user.id)
        Farm.update(user.id, chickens=updated_farm_data['chickens'], eggs_generated=updated_farm_data['eggs_generated'])
        user_data['points'] -= taxes
        User.update_points(user_data['user_id'], user_data['points'])
    return updated_farm_data

async def update_farmer(user, farm_data):
    last_drop_time = time() - farm_data['last_farmer_drop']
    hours_passed_since_feed = 0
    bank_data = await user_cache_retriever(user.id)
    bank_data = bank_data['bank_data']
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
            
async def devolve_chicken(chicken):
        """Devolve a chicken if its happiness is 0"""
        devolveChance = randint(1, 3)
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

async def update_player_corn(farm_data, user: discord.Member):
    last_drop_time = time() - farm_data['last_corn_drop']
    updated_farm_data = farm_data
    hours_passed_since_last_drop = min(last_drop_time // 7200, 10)
    for _ in range(int(hours_passed_since_last_drop)):
        updated_farm_data = await generate_corncrops(farm_data)
    if hours_passed_since_last_drop != 0:
        Farm.update_corn_drop(user.id)
        Farm.update(user.id, corn=updated_farm_data['corn'])
    return updated_farm_data

def calculate_corn(farm_data):
    """Calculate the corn generated by the farm"""
    if farm_data['farmer'] == 'Rich Farmer':
         to_increase = corn_per_plot * (load_farmer_upgrades('Rich Farmer')[1]) / 100
         production = corn_per_plot + to_increase
         production = int(production)
         return farm_data['plot'] * production
    return farm_data['plot'] * corn_per_plot

async def generate_corncrops(farm_data):
        """Generate corn crops"""
        corn_dict = {}
        if farm_data:
            totalCorn = calculate_corn(farm_data)
            corn = farm_data['corn']
            corn += totalCorn
            if corn > farm_data['corn_limit']:
                corn = farm_data['corn_limit']
            corn_dict = {
                 "corn" : corn
            }
            farm_data['corn'] = corn_dict['corn']
            return farm_data
        
async def get_player_chicken(ctx, user: discord.Member, farm_data):
     """Retrieves the player's chickens from market offers."""
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
                print(len(var))
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

async def farm_maintence_tax(farm_data):
    """Check if the farm is in maintence"""
    player_plot = farm_data['plot']
    plot_tax = player_plot * 10
    player_corn_size = farm_data['corn_limit']
    corn_tax = math.sqrt(player_corn_size) * 4
    chicken_rarity_weight = sum([rarities_weight[chicken['rarity']] for chicken in farm_data['chickens']])
    chicken_rarity_weight = chicken_rarity_weight * 2
    chicken_tax =  chicken_rarity_weight / get_max_chicken_limit(farm_data)
    total_tax = plot_tax + corn_tax + chicken_tax
    return int(total_tax)

     
