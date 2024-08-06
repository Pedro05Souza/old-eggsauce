from enum import Enum

# Chicken information module

chicken_default_value = 400
default_farm_size = 8
offer_expire_time = 48
max_bench = 5
max_corn_limit = 2553
max_plot_limit = 20
corn_per_plot = 100

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
        "GALATIC": 4.8,
        "OMINOUS": 2.4,
        "CELESTIAL": 1.2,
        "IMMORTAL": 0.6,
        "CHOSEN": 0.3,
        "ASCENDED": 0.15,
    }

defineRarityEmojis = {
    "DEAD": "☠️",
    "COMMON": "🟤",
    "UNCOMMON": "🟢",
    "RARE": "🔵",
    "EXCEPTIONAL": "🟣",
    "EPIC": "🟠",
    "LEGENDARY": "🔴",
    "MYTHICAL": "🟡",
    "ULTIMATE": "⚫",
    "COSMIC": "⚪",
    "DIVINE": "✨",
    "GALATIC": "🌌",
    "OMINOUS": "💥",
    "CELESTIAL": "🌟",
    "IMMORTAL": "☄️",
    "CHOSEN": "🌀",
    "ASCENDED": "🌠",
    "ETHEREAL": "♾️"
}

chicken_rarities = {
    "HORRIFIC" : .75,
    "TERRIBLE": .7,
    "AWFUL" : .6,
    "BAD" : .5,
    "NORMAL" : .3,
    "DECENT" : .2,
    "GOOD" : .1,
    "GREAT" : .05,
    "AMAZING" : .02,
    "AWESOME" : .01,
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
    GALATIC = 11
    OMINOUS = 12
    CELESTIAL = 13
    IMMORTAL = 14
    CHOSEN = 15
    ASCENDED = 16
    ETHEREAL = 250

class ChickenMultiplier(Enum):
    DEAD = 0
    COMMON = 2
    UNCOMMON = 4
    RARE = 9
    EXCEPTIONAL = 16
    EPIC = 25
    LEGENDARY = 36
    MYTHICAL = 49
    ULTIMATE = 64
    COSMIC = 81
    DIVINE = 100
    GALATIC = 121
    OMINOUS = 144
    CELESTIAL = 169
    IMMORTAL = 196
    CHOSEN = 225
    ASCENDED = 256
    ETHEREAL = 1000
    
class ChickenFood(Enum):
    DEAD = 0
    COMMON = 1
    UNCOMMON = 3
    RARE = 7
    EXCEPTIONAL = 12
    EPIC = 18
    LEGENDARY = 25
    MYTHICAL = 33
    ULTIMATE = 42
    COSMIC = 52
    DIVINE = 63
    GALATIC = 74
    OMINOUS = 87
    CELESTIAL = 101
    IMMORTAL = 115
    CHOSEN = 130
    ASCENDED = 146
    ETHEREAL = 210

rarities_weight = {
    "DEAD": 0,
    "COMMON": 2,
    "UNCOMMON": 4,
    "RARE": 6,
    "EXCEPTIONAL": 10,
    "EPIC": 15,
    "LEGENDARY" : 21,
    "MYTHICAL" : 27,
    "ULTIMATE": 34,
    "COSMIC": 41,
    "DIVINE": 50,
    "GALATIC": 58,
    "OMINOUS": 68,
    "CELESTIAL": 78,
    "IMMORTAL": 88,
    "CHOSEN": 99,
    "ASCENDED": 111,
    "ETHEREAL": 200
}

upkeep_weight = {
    "HORRIFIC" : -30,
    "TERRIBLE": -20,
    "AWFUL" : -10,
    "BAD" : 0,
    "NORMAL" : 10,
    "DECENT" : 20,
    "GOOD" : 30,
    "GREAT" : 40,
    "AMAZING" : 50,
    "AWESOME" : 60,
    "PERFECT" : 70
}

score_determiner = {
    "REALLY LOW": 100,
    "LOW": 350,
    "MEDIUM": 500,
    "HIGH": 1000,
    "REALLY HIGH": 1300,
    "EXTREMELY HIGH": 1600,
    "BEYOND HIGH": 2000,
    "MAXED": 2160
}

farm_size_weights = {
    1: 100,
    2: 80,
    3: 60,
    4: 40,
    5: 20,
    6: 10,
    7: 5,
    8: 0
}

chicken_ranking = {
    "RAW EGG": 0,
    "FRIED EGG": 100,
    "BOILED EGG": 250,
    "OMELET": 500,
    "EGGPLANT": 750,
    "EGG MASTER": 1000,
    "EGG GRANDMASTER": 1250,
    "EGG CHALLENGER": 1750,
    "LEGGEND": 2000
}
