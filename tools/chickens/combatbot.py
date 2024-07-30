from random import randint
from tools.chickens.chickenshared import ChickenRarity, create_chicken, define_chicken_overrall_score


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
    bot_chickens = []
    bot_rarity_list = await define_chicken_rarity_list(all_rarities[:5], all_rarities[5:10], all_rarities[10:14], all_rarities[12:], all_rarities[15:], user_chicken, user_score)
    for _ in range(bot_farm_size):
        random_rank = bot_rarity_list[randint(0, len(bot_rarity_list) - 1)]
        bot_chickens.append(await create_chicken(random_rank))
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
    for i in range(0, 2000, 100):
        if player_mmr <= i:
            return min(8, max(2, int(i / 100)))
        
async def define_chicken_rarity_list(low_level_rarities, medium_level_rarities, high_level_rarities, extreme_level_rarities, maxed_level_rarities, player_rarity_list, player_mmr):
    """Changes the rarity list for the bot."""
    bot_rarity = [chicken['rarity'] for chicken in player_rarity_list]
    if player_mmr < 250:
        [bot_rarity.append(rarity) for rarity in low_level_rarities if rarity not in bot_rarity]
    elif player_mmr >= 250 and player_mmr < 500:
        [bot_rarity.append(rarity) for rarity in medium_level_rarities if rarity not in bot_rarity]
    elif player_mmr >= 500 and player_mmr < 1000:
        [bot_rarity.append(rarity) for rarity in high_level_rarities if rarity not in bot_rarity]
    elif player_mmr >= 1000 and player_mmr < 1600:
        [bot_rarity.append(rarity) for rarity in extreme_level_rarities if rarity not in bot_rarity]
    else:
        [bot_rarity.append(rarity) for rarity in maxed_level_rarities if rarity not in bot_rarity]
    return bot_rarity
    
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
        "salsa",
        "Kefero",
        "trainer beco"
    ]
    return name_list[randint(0, len(name_list) - 1)]