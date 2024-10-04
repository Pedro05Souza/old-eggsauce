"""
This package contains commands for managing the chicken game in the bot.

Modules included:
* chickencombat: Contains functions for combat in the chicken game.
* chickencore: Contains core functions for the chicken game.
* chickenevents: Contains functions for events in the chicken game.
* chickenview: Contains functions for viewing data in the chicken game.
* corncmds: Contains commands for managing corn in the chicken game.
* playermarket: Contains functions for selling and buying chickens with other players.
* chicken_interactive: Contains chicken commands that at least 2 users are required to run.
* chickenbench: Contains commands for managing the chicken bench in the chicken game.
"""
from .chicken_combat import *
from .chicken_core import *
from .chicken_events import *
from .chicken_view import *
from .corn_cmds import *
from .player_market import *
from .chicken_interactive import *
from .chicken_bench import *