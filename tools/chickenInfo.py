
from enum import Enum
from random import randint

rollRates = {
            "COMMON": 5000,
            "UNCOMMON": 2500,
            "RARE": 1250,
           "EXCEPTIONAL": 625,
            "EPIC": 312.5,
            "LEGENDARY" : 156.2,
            "MYTHICAL" : 78.1,
            "ULTIMATE": 39,
            "COSMIC": 19.5,
            "DIVINE": 9.7,
            "INFINITY": 4.8,
            "OMINOUS": 2.4,
            "CELESTIAL": 1.2,
            "IMMORTAL": 0.6,
            "CHOSEN": 0.3,
            "ASCENDED": 0.15,
        }

defineRarityEmojis = {
            "DEAD": ":skull_crossbones:",
            "COMMON": ":brown_circle:",
            "UNCOMMON": ":green_circle:",
            "RARE": ":blue_circle:",
            "EXCEPTIONAL": ":purple_circle:",
            "EPIC": ":orange_circle:",
            "LEGENDARY": ":red_circle:",
            "MYTHICAL": ":yellow_circle:",
            "ULTIMATE": ":black_circle:",
            "COSMIC": ":white_circle:",
            "DIVINE": ":sparkles:",
            "INFINITY": ":milky_way:",
            "OMINOUS": ":boom:",
            "CELESTIAL": ":star2:",
            "IMMORTAL": ":comet:",
            "CHOSEN": ":cyclone:",
            "ASCENDED": ":stars:",
        }

# multiplicador de preço
class ChickenRarity(Enum):
        DEAD = 0
        COMMON = 1
        UNCOMMON = 2
        RARE = 3
        EXCEPTIONAL = 4
        EPIC = 5
        LEGENDARY = 6
        MYTHICAL = 7
        ULTIMATE = 8
        COSMIC = 9
        DIVINE = 10
        INFINITY = 11
        OMINOUS = 12
        CELESTIAL = 13
        IMMORTAL = 14
        CHOSEN = 15
        ASCENDED = 16
class ChickenMultiplier(Enum):
        DEAD = 0
        COMMON = 3
        UNCOMMON = 7
        RARE = 9
        EXCEPTIONAL = 11
        EPIC = 13
        LEGENDARY = 15
        MYTHICAL = 18
        ULTIMATE = 19
        COSMIC = 27
        DIVINE = 33
        INFINITY = 45
        OMINOUS = 50
        CELESTIAL = 54
        IMMORTAL = 63
        CHOSEN = 69
        ASCENDED = 77
class ChickenFood(Enum):
        DEAD = 0
        COMMON = 2
        UNCOMMON = 4
        RARE = 6
        EXCEPTIONAL = 8
        EPIC = 10
        LEGENDARY = 12
        MYTHICAL = 14
        ULTIMATE = 16
        COSMIC = 18
        DIVINE = 20
        INFINITY = 22
        OMINOUS = 24
        CELESTIAL = 26
        IMMORTAL = 28
        CHOSEN = 30
        ASCENDED = 32
class TradeData():
        obj_list = []

        def __init__ (self):
            self.author = {}
            self.target = {}
            self.identifier = []
            TradeData.obj_list.append(self)

        @staticmethod
        def get(identifier):
            for obj in TradeData.obj_list:
                if obj.identifier == identifier:
                    return obj
            return None
        @staticmethod
        def remove(obj):
            try:
                TradeData.obj_list.remove(obj)
            except Exception as e:
                print("Error removing object from list.", e)

        @staticmethod
        def get_all():
            return TradeData.obj_list
        
        @staticmethod
        def clear():
            TradeData.obj_list.clear()

        @staticmethod
        def read(author):
            for obj in TradeData.obj_list:
                for id in obj.identifier:
                    if id == author:
                        return True
            return None
        
def determine_chicken_upkeep(chicken):
    min_value = find_min_upkeep_value(chicken)
    base_value = (ChickenMultiplier[chicken['rarity']].value * 2) // 5
    if min_value == 1:
        max_value = base_value
    else:
        max_value = min_value * 2
    if min_value < max_value:
        chicken['upkeep_multiplier'] = randint(min_value, max_value)
    else:
        chicken['upkeep_multiplier'] = min_value
        
    return chicken['upkeep_multiplier']
        
def find_min_upkeep_value(chicken):
    rarity_list = list(ChickenRarity.__members__.keys())[-5:]
    base_value = (ChickenMultiplier[chicken['rarity']].value * 2) // 5

    if chicken['rarity'] in rarity_list:
        min_value = 1

    else:
        min_value = base_value

    return min_value
        