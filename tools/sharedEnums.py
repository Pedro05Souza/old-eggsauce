from enum import Enum

# this class was created to fix the circular import issue between ChickenCommands and ChickenSelection
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