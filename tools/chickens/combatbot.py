from random import randint, random, choice
from tools.chickens.chickenshared import ChickenRarity, create_chicken, define_chicken_overrall_score
from tools.settings import default_farm_size
import bisect

class BotMatchMaking():

    def __init__(self, bot_name):
        self.name = bot_name
        self.chickens = []
        self.score = 0
        self.chicken_overrall_score = 0
        self.has_opponent = False
        self.bot_id = randint(100000, 999999)

    def __repr__(self) -> str:
        return f"{self.name} - {self.score}"

async def bot_maker(user_score: int) -> BotMatchMaking:
    """"
    Function to create a bot in the matchmaking.
    """
    bot = BotMatchMaking(await name_maker())
    bot_farm_size = randint(await define_bot_min_farm_size(user_score), default_farm_size)
    all_rarities = list(ChickenRarity.__members__)
    all_rarities.remove("DEAD")
    all_rarities_dict = {rarity: position for position, rarity in enumerate(all_rarities)}
    bot_chickens = []
    bot_rarity_list = await define_chicken_rarity_list(user_score, all_rarities_dict)
    cumulative_distribution = []
    cummulative = 0

    for rarity, probability in bot_rarity_list.items():
        cummulative += probability
        cumulative_distribution.append((cummulative, rarity))
    for _ in range(bot_farm_size):
        random_number = random()
        index = bisect.bisect_left(cumulative_distribution, (random_number,))
        if index >= len(cumulative_distribution):
            index = len(cumulative_distribution) - 1
        else:
         rarity = cumulative_distribution[index][1]
        bot_chickens.append(await create_chicken(rarity, "bot"))
    bot.chickens = bot_chickens
    negative_score = user_score * .9
    positive_score = user_score * 1.1
    negative_score = int(negative_score)
    positive_score = int(positive_score)
    bot.score = randint(negative_score, positive_score)
    if bot.score < 0:
        bot.score = 0 
    bot.chicken_overrall_score = await define_chicken_overrall_score(bot.chickens)
    return bot

async def define_bot_min_farm_size(player_mmr: int) -> int:
    """
    Defines the minimum farm size for the bot.
    """
    if player_mmr >= 2000:
        return default_farm_size
    for i in range(0, 2100, 100):
        if player_mmr <= i:
            return min(default_farm_size, max(2, int(i / 100)))
        
async def define_chicken_rarity_list(player_mmr: int, all_rarities: dict) -> dict:
    """
    Changes the rarity list for the bot to pick from.
    """
    bot_deck = all_rarities.copy()
    if player_mmr >= 2000:
        chances = .33
        rarities = ['ASCENDED', 'ETHEREAL', 'CHOSEN']
        zip_list = zip(rarities, [chances] * len(rarities))
        bot_deck = dict(zip_list)
        for rarity, chance in zip_list:
            bot_deck[rarity] = chance
        return bot_deck
    else:
        bot_deck.pop('ETHEREAL')
        all_rarities.pop('ETHEREAL')

    chicken_selected = player_mmr * len(all_rarities) / 2000
    chicken_selected = int(chicken_selected)

    for key, value in all_rarities.items():
        distance = abs(value - chicken_selected)
        weight = 1 / (distance + 1)
        bot_deck[key] = weight ** 2

    total = sum(bot_deck.values())
    for key in bot_deck:
        bot_deck[key] = round(bot_deck[key] / total, 2)
    return bot_deck

async def generate_syllabe():
    pattern = [
        "CVC",  
        "VC",   
        "CV",   
        "V",    
        "C",    
        "CCV",  
        "VCC",  
        "CVV",  
        "VV",   
        "CCVC",
    ]
    syllable = ""
    for char in pattern:
        if char == "C":
            syllable += choice("bdfghjklmnpqrstvwxyz")
        elif char == "V":
            syllable += choice("aeiou")
    return syllable

async def name_maker():
    name = ""
    for _ in range(randint(2, 3)):
        name += await generate_syllabe()
    if randint(0, 1):
        name += str(randint(0, 999))
    return name.capitalize() if randint(0, 1) else name

