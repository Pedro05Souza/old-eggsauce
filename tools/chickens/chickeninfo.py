from enum import Enum

# Chicken information module

chicken_default_value = 200
default_farm_size = 8
offer_expire_time = 48
max_bench = 5
max_corn_limit = 1702
max_plot_limit = 14

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
    INFINITY = 11
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
    RARE = 6
    EXCEPTIONAL = 10
    EPIC = 15
    LEGENDARY = 21
    MYTHICAL = 27
    ULTIMATE = 34
    COSMIC = 41
    DIVINE = 50
    INFINITY = 58
    OMINOUS = 68
    CELESTIAL = 78
    IMMORTAL = 88
    CHOSEN = 99
    ASCENDED = 111
    ETHEREAL = 1000
    
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
    ETHEREAL = 300