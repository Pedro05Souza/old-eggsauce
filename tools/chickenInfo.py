
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
            "ALMIGHTY": 0.3
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
            "ALMIGHTY": ":cyclone:"
        }

from enum import Enum

class ChickenRarity(Enum):
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
        INFINITY = 14
        OMINOUS = 20
        CELESTIAL = 22
        IMMORTAL = 24

class ChickenMultiplier(Enum):
        COMMON = 2
        UNCOMMON = 2
        RARE = 4
        EXCEPTIONAL = 5
        EPIC = 8
        LEGENDARY = 11
        MYTHICAL = 14
        ULTIMATE = 16
        COSMIC = 17
        DIVINE = 19
        INFINITY = 21
        OMINOUS = 24
        CELESTIAL = 40
        IMMORTAL = 80

class ChickenUpkeep(Enum):
        COMMON = 3
        UNCOMMON = 2
        RARE = 3
        EXCEPTIONAL = 3
        EPIC = 5
        LEGENDARY = 7
        MYTHICAL = 9
        ULTIMATE = 10
        COSMIC = 10
        DIVINE = 11
        INFINITY = 8
        OMINOUS = 10
        CELESTIAL = 15
        IMMORTAL = 30

class TradeData():
        def __init__ (self):
            self.tradeData = {}