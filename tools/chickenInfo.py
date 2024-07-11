
from enum import Enum
from random import uniform
from db.farmDB import Farm

chicken_default_value = 150

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

chicken_rarities = {
        "TERRIBLE" : .75,
        "AWFUL" : .6,
        "BAD" : .45,
        "NORMAL" : .3,
        "DECENT" : .2,
        "GOOD" : .1,
        "GREAT" : .05,
        "PERFECT" : 0
}
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
        EXCEPTIONAL = 10
        EPIC = 11
        LEGENDARY = 14
        MYTHICAL = 17
        ULTIMATE = 18
        COSMIC = 25
        DIVINE = 29
        INFINITY = 45
        OMINOUS = 60
        CELESTIAL = 70
        IMMORTAL = 75
        CHOSEN = 82
        ASCENDED = 92
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
class RollLimit:
    obj_list = []
    def __init__(self, user_id, current, chickens=None):
        RollLimit.obj_list.append(self)
        self.user_id = user_id
        self.current = current
        self.chickens = chickens

    @staticmethod
    def read(user_id):
        for obj in RollLimit.obj_list:
            if obj.user_id == user_id:
                return obj
        return None
    
    @staticmethod
    def remove(obj):
        try:
            RollLimit.obj_list.remove(obj)
        except Exception as e:
            print("Error removing object from list.", e)
    
    @staticmethod
    def removeAll():
        RollLimit.obj_list.clear()
        
def determine_chicken_upkeep(chicken):
    percentage = uniform(0, .75)
    percentage = round(percentage, 2)
    chicken['upkeep_multiplier'] = percentage
    return chicken['upkeep_multiplier']

def get_chicken_egg_value(chicken):
     egg_value = ChickenMultiplier[chicken['rarity']].value
     return egg_value

def get_chicken_price(chicken, *args):
     if args:   
          farm_data = args[0]
          if farm_data['farmer'] == 'Executive Farmer':
               discount_value = load_farmer_upgrades(farm_data['user_id'])[1]
               default_discount = chicken_default_value * discount_value // 100
               chicken_discount = chicken_default_value - default_discount  
               chicken_price = (ChickenRarity[chicken['rarity']].value * chicken_discount)
               return chicken_price
     return ChickenRarity[chicken['rarity']].value * chicken_default_value

def load_farmer_upgrades(player_id):
        """Load the farmer upgrades"""
        farmer_dict = {
            "Rich Farmer": 10,
            "Guardian Farmer": 4,
            "Executive Farmer" : [8, 4],
            "Warrior Farmer": 3,
            "Generous Farmer": [3]
        }
        player_farmer = Farm.read(player_id)['farmer']
        return farmer_dict[player_farmer]
        