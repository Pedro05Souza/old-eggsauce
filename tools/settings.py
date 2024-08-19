
"""
Settings for the bot. Highly customizable.

This module contains various configuration settings for the bot, including cooldowns, prices, and limits.

"""
# Cooldown settings (in seconds)

spam_command_cooldown = .8 # Cooldown for spam commands
regular_command_cooldown = 3.5 # Cooldown for regular commands
queue_command_cooldown = 90 # Cooldown for queue commands

# Hunger Games command settings

hunger_games_wait_time = 60 # Wait time before a hunger games match starts (in seconds)
hunger_games_match_value_per_tribute = 75 # The prize that the user has to pay to join the match
hunger_games_prize_multiplier = 50 # The weight that each tribute's that is in the match will be multiplied by to determine the total prize
min_tributes = 4 # The minimum number of tributes that must be in the match for it to start
max_tributes = 30 # The maximum number of tributes that can be in the match

# Farm settings

chicken_default_value = 400 # controls the minimum value of a chicken that can generate in the market.
default_farm_size = 8 # controls the default farm size
offer_expire_time = 48 # controls the time it takes for an offer to expire (in hours)
max_bench = 5 # controls the maximum number of chickens that can be on the bench
max_corn_limit = 2553 # controls the maximum corn limit
max_plot_limit = 20 # controls the maximum plot limit
corn_per_plot = 100 # controls the amount of corn that can be produced per plot
farm_drop = 7200 # controls the time it takes for the chickens in a farm to drop eggs (in seconds)
roll_per_hour = 3600 # controls the time it takes for the user to reset their rolls in the market (in seconds)
max_plot_tax_value = 200 # controls the maximum tax value for the plots
max_corn_tax_value = 150 # controls the maximum tax value for the corn
max_farm_tax_value = 300 # controls the maximum tax value for the farm

# Hybrid command settings

tax = .15 # controls the donate command tax and buying a chicken tax
user_salary_drop = 3600 # controls the time it takes for the user to drop eggs (in seconds)