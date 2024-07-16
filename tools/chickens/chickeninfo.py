from enum import Enum

# Chicken information module

chicken_default_value = 150
default_farm_size = 8

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