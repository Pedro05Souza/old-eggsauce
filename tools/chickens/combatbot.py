from random import randint, random
from tools.chickens.chickenshared import ChickenRarity, create_chicken, define_chicken_overrall_score
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

async def bot_maker(user_chicken, user_score):
    """"Function to create a bot in the matchmaking."""
    bot = BotMatchMaking(await name_maker())
    bot_farm_size = randint(await define_bot_min_farm_size(user_score), 8)
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
    negative_score = user_score * .8
    positive_score = user_score * 1.2
    negative_score = int(negative_score)
    positive_score = int(positive_score)
    bot.score = randint(negative_score, positive_score)
    if bot.score < 0:
        bot.score = 0 
    bot.chicken_overrall_score = await define_chicken_overrall_score(bot.chickens)
    return bot

async def define_bot_min_farm_size(player_mmr):
    """Defines the minimum farm size for the bot."""
    if player_mmr >= 2000:
        return 8
    for i in range(0, 2100, 100):
        if player_mmr <= i:
            return min(8, max(2, int(i / 100)))
        
async def define_chicken_rarity_list(player_mmr, all_rarities):
    """Changes the rarity list for the bot."""
    bot_deck = all_rarities.copy()
    if player_mmr >= 2000:
        player_mmr = 2000
    chicken_selected = player_mmr * 17/2000
    chicken_selected = int(chicken_selected)
    for key, value in all_rarities.items():
        distribution = abs(value - chicken_selected)
        distribution = 1 if distribution == 0 else distribution
        distribution = 1/distribution
        bot_deck[key] = distribution
    total = sum(bot_deck.values())
    for key in bot_deck:
        bot_deck[key] = round(bot_deck[key] / total, 2)
    return bot_deck

async def name_maker():
    """Defines the bot's username."""
    name_list = [
        "blud",
        "Alejandro",
        "Pickle",
        "Cucumber",
        "Hollow",
        "xX_Kirito_God_Slayer_Xx",
        "ProGamer_123",
        "ChickenLover",
        "Warrior_dewd",
        "Epicswordman99",
        "Unevenroblox1000",
        "GamerGirl <3",
        "Her Jett :sunglasses:",
        "Cru1zz",
        "the man",
        "Kefero",
        "trainer beco",
        "cracka",
        "chicken_butt",
        "the_fat_one",
        "jeff",
        "Mystical",
        "TheLegend27",
        "ant",
        "cr7",
        "messi",
        "ronaldo007",
        "neymar_jr2"	
    ]
    return name_list[randint(0, len(name_list) - 1)]