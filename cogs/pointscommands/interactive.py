from discord.ext import commands
from db.botConfigDB import BotConfig
from tools.pricing import pricing, refund
from tools.embed import create_embed_without_title, create_embed_with_title
from db.userDB import Usuario
from collections import Counter
import time
import asyncio
from tools.pagination import PaginationView
import discord
from random import randint, sample, choice
hungergames_status = {}
class InteractiveCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.remove_command('help')

    async def drop_eggbux(self):
        await asyncio.gather(*(self.drop_eggbux_for_guild(guild) for guild in self.bot.guilds))

    async def drop_eggbux_for_guild(self, guild):
        """Drops eggbux in the chat."""
        server = BotConfig.read(server_id=guild.id)
        if server:
            channel = self.bot.get_channel(server["channel_id"])
            chance = randint(0, 100)
            minutesToClaim = 5
            if chance <= 8:  # 8% drop chance
                quantEgg = randint(1, 750)
                embed = discord.Embed(description=f":moneybag: A bag with **{quantEgg}** eggbux has been dropped in the chat!. Type **claim** to get it. Remember you only have **{minutesToClaim} minutes** to claim it.") 
                await channel.send(embed=embed)
                try:
                    Message = await asyncio.wait_for(self.bot.wait_for('message', check=lambda message: message.content == "claim" and message.channel == channel), timeout=60*minutesToClaim)
                    if Usuario.read(Message.author.id):
                        Usuario.update(Message.author.id, Usuario.read(Message.author.id)["points"] + quantEgg, Usuario.read(Message.author.id)["roles"])
                        embedClaim = discord.Embed(description=f"{Message.author.display_name} claimed {quantEgg} eggbux")
                        await channel.send(embed=embedClaim)
                    else:
                        Usuario.create(Message.author.id, quantEgg)
                        embedClaim2 = discord.Embed(description=f"{Message.author.display_name} claimed {quantEgg} eggbux")
                        await channel.send(embed=embedClaim2)
                except asyncio.TimeoutError:
                    embedTimeout = discord.Embed(description=f"The bag with {quantEgg} eggbux has expired.")
                    await channel.send(embed=embedTimeout)
            
    async def drop_periodically(self):
        """Drops eggbux in the chat every 1000 seconds."""
        while True:
            await asyncio.sleep(1000)
            await self.drop_eggbux()

    @commands.hybrid_command(name="donatepoints", aliases=["donate", "give"], brief="Donate points to another user.", usage="donatePoints [user] [amount]", description="Donate points to another user.")
    @pricing()
    async def donate_points(self, ctx, user:discord.Member, amount: int):
        """Donates points to another user."""
        if Usuario.read(user.id):
            if ctx.author.id == user.id:
                await create_embed_without_title(ctx, f"{ctx.author.display_name} You can't donate to yourself.")
            elif Usuario.read(ctx.author.id)["points"] >= amount:
                if amount <= 0:
                    await create_embed_without_title(ctx, f"{ctx.author.display_name} You can't donate 0 or negative eggbux.")
                    return
                else:
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] - amount, Usuario.read(ctx.author.id)["roles"])
                    Usuario.update(user.id, Usuario.read(user.id)["points"] + amount, Usuario.read(user.id)["roles"])
                    await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name} donated {amount} eggbux to {user.display_name}")
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} doesn't have enough eggbux.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} isn't registered in the database.")
             
    @commands.hybrid_command(name="casino", aliases=["cassino", "bet", "gamble", "roulette"], brief="Bet on a color in the roulette.", usage="casino [amount] [color]", description="Bet on a color in the roulette, RED, BLACK or GREEN.")
    @pricing()
    async def cassino(self, ctx, amount, cor: str):
        """Bet on a color in the roulette."""
        if amount.upper() == "ALL":
            amount = Usuario.read(ctx.author.id)["points"]
        else:
            amount = int(amount)
        cor = cor.upper()
        coresPossiveis = ["RED", "BLACK", "GREEN"]
        corEmoji = {"RED": "🟥", "BLACK": "⬛", "GREEN": "🟩"}
        vermelhos = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        roleta = {i : "RED" if i in vermelhos else ("BLACK" if i != 0 else "GREEN") for i in range(0, 37)}
        if cor in coresPossiveis:
            if Usuario.read(ctx.author.id)["points"] >= amount and amount >= 50:
                cassino = randint(0, 36)
                corSorteada = roleta[cassino]
                if corSorteada == "GREEN" and cor == "GREEN":
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + (amount * 14), Usuario.read(ctx.author.id)["roles"])
                    await create_embed_without_title(ctx, f":slot_machine: {ctx.author.display_name} has **won** {amount * 14} eggbux! The selected color was {corSorteada} {corEmoji[corSorteada]}")
                elif corSorteada == cor:
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + amount, Usuario.read(ctx.author.id)["roles"])
                    await create_embed_without_title(ctx, f":slot_machine: {ctx.author.display_name} has **won** {amount} eggbux!")
                else:                  
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] - amount, Usuario.read(ctx.author.id)["roles"])
                    await create_embed_without_title(ctx, f":slot_machine: {ctx.author.display_name} has **lost!** The selected color was {corSorteada} {corEmoji[corSorteada]}")
                    return
            else:
                await create_embed_without_title(ctx, f":slot_machine: {ctx.author.display_name} You don't have enough eggbux or the amount is less than 50.")
                return  
        else:
            await create_embed_with_title(ctx, ":slot_machine:" ,f"{ctx.author.display_name} You don't have permission to do this.")
            return

    @cassino.error
    async def cassino_error(self, ctx, error):
        """Handles errors in the cassino command."""
        if isinstance(error, commands.MissingRequiredArgument):
            await create_embed_without_title(ctx, f"{ctx.author.display_name} Please, insert a valid amount and color.")
        elif isinstance(error, commands.BadArgument):
            await create_embed_without_title(ctx, f"{ctx.author.display_name} Please, insert a valid amount.")
        else:
            await create_embed_without_title(ctx, f"{ctx.author.display_name} An unexpected error occurred.")
            print(error)

    @commands.hybrid_command(name="stealpoints", aliases=["steal", "rob"], brief="Steal points from another user.", usage="stealPoints [user]", description="Steal points from another user.")
    @pricing()
    async def steal_points(self, ctx, user: discord.Member):
        """Steals points from another user."""
        chance  = randint(0, 100)
        if user.bot:
            await create_embed_without_title(ctx, f"{ctx.author.display_name} You can't steal from a bot.")
            await refund(ctx.author, ctx)
            return
        if Usuario.read(user.id):
            if ctx.author.id == user.id:
                await create_embed_without_title(ctx, f"{ctx.author.display_name} You can't steal from yourself.")
                await refund(ctx.author, ctx)
                return
            quantUser = Usuario.read(user.id)["points"]
            if quantUser <= 150:
                await create_embed_without_title(ctx, f"{ctx.author.display_name} You can't steal from a user with less than 150 eggbux.")
                await refund(ctx.author, ctx)
                return
            elif chance >= 10:
                randomInteiro = randint(1, int(quantUser//2))
                Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + randomInteiro, Usuario.read(ctx.author.id)["roles"])
                Usuario.update(user.id, Usuario.read(user.id)["points"] - randomInteiro, Usuario.read(user.id)["roles"])
                await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name} stole {randomInteiro} eggbux from {user.display_name}")
                return
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} failed to steal from {user.display_name}")
                return
        else:
            await create_embed_without_title(ctx, f"{ctx.author.display_name} You don't have permission to do this.")
            return
        
    @commands.hybrid_command(name="buytitles", aliases=["titles"], brief="Buy custom titles.", usage="Buytitles", description="Buy custom titles that comes with different salaries every 30 minutes.")
    @pricing()
    async def points_Titles(self, ctx):
        end_time = time.time() + 60
        roles = {
            "T" : "Egg Novice",
            "L" : "Egg Apprentice",
            "M" : "Egg wizard",
            "H" : "Egg King",
        }

        rolePrices = {
            "T" : 600,
            "L" : 800,
            "M" : 1200,
            "H" : 1800
        }
        message = await create_embed_with_title(ctx, "Custom Titles:", f":poop: **{roles['T']}**\nIncome: 50 eggbux. :money_bag: \nPrice: 600 eggbux.\n\n :farmer: **{roles['L']}** \nIncome: 75 eggbux. :money_bag:\n Price: 800 eggbux. \n\n:man_mage: **{roles['M']}** \n Income: 100 eggbux. :money_bag:\n Price: 1200 eggbux. \n\n:crown: **{roles['H']}** \n Income: 150 eggbux. :money_bag:\n Price: 1800 eggbux. \n**The titles are bought sequentially.**\nReact with ✅ to buy a title.")
        await message.add_reaction("✅")
        while True:
            actual_time = end_time - time.time()
            if actual_time <= 0:
                await message.clear_reactions()
                break
            check = lambda reaction, user: reaction.emoji == "✅" and reaction.message.id == message.id
            reaction, user = await self.bot.wait_for("reaction_add", check=check)
            if reaction.emoji == "✅":
                if Usuario.read(user.id)["roles"] == "":
                    await self.buy_roles(ctx, user, rolePrices["T"], "T", roles["T"])
                elif Usuario.read(user.id)["roles"][-1] == "T":
                    await self.buy_roles(ctx, user, rolePrices["L"], "L", roles["L"])
                elif Usuario.read(user.id)["roles"][-1] == "L":
                    await self.buy_roles(ctx, user, rolePrices["M"], "M", roles["M"])
                elif Usuario.read(user.id)["roles"][-1] == "M":
                    await self.buy_roles(ctx, user, rolePrices["H"], "H", roles["H"])

    async def buy_roles(self, ctx, User: discord.Member, roleValue, roleChar, roleName):
        """Buy roles."""
        if Usuario.read(User.id)["points"] >= roleValue and roleChar not in Usuario.read(User.id)["roles"]:
            Usuario.update(User.id, Usuario.read(User.id)["points"] - roleValue, Usuario.read(User.id)["roles"] + roleChar)
            await create_embed_without_title(ctx, f":white_check_mark: {User.display_name} has bought the role **{roleName}**.")
        elif Usuario.read(User.id)["points"] < roleValue:
            await create_embed_without_title(ctx, f":no_entry_sign: {User.display_name}, you don't have enough eggbux to buy the role **{roleName}**.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {User.display_name} already has the role **{roleName}**.")

    def salary_role(self, User:discord.Member):
        """Returns the salary of a user based on their roles."""
        salarios = {
            "T": 50,
            "L": 75,
            "M": 100,
            "H": 150
        }
        if Usuario.read(User.id):
            return salarios[Usuario.read(User.id)["roles"][-1]]
        else:
            return 0
        
    def get_user_title(self, User: discord.Member):
        userRoles = {
            "T" : "Egg Novice",
            "L" : "Egg Apprentice",
            "M" : "Egg wizard",
            "H" : "Egg King",
        }
        if Usuario.read(User.id):
            if Usuario.read(User.id)["roles"] == "":
                return "Unemployed"
            return userRoles[Usuario.read(User.id)["roles"][-1]]
        
    async def work_periodically(self):
        """Periodically updates the salary of users with roles."""
        while True:
            await asyncio.sleep(1600)
            for user in Usuario.read_all_members_with_role():
                Usuario.update(user["user_id"], user["points"] + self.salary_role(discord.utils.get(self.bot.get_all_members(), id=user["user_id"])), user["roles"])
                print(f"Updated {user['user_id']} salary.")

    @commands.hybrid_command(name="salary", aliases=["sal"], brief="Check the salary of a user.", usage="salary OPTIONAL [user]", description="Check the salary of a user. If not user, shows author's salary.")
    @pricing()
    async def salary(self, ctx, user: discord.Member = None):
        """Check the salary of a user."""
        if user is None:
            user = ctx.author
        user_data = Usuario.read(user.id)
        if user_data:
            if user_data["roles"] != "":
                await create_embed_without_title(ctx, f":moneybag: {user.display_name} has the title of **{self.get_user_title(user)}** and earns {self.salary_role(user)} eggbux..")
                return   
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} doesn't have a title.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} isn't registered in the database.")
            await refund(ctx.author, ctx)

    @commands.command(aliases=["hg"])
    @pricing()
    async def hungergames(self, ctx, *args):
        """Starts a hunger games event."""
        global hungergames_status
        guild_id = ctx.guild.id
        if guild_id in hungergames_status:
            await create_embed_without_title(ctx, ":no_entry_sign: A hunger games is already in progress.")
            return
        wait_time = 15
        if args and args[0].isdigit():
            args = [int(arg) for arg in args] 
            if ctx.guild.owner.id == ctx.author.id:
                wait_time = args[0] * 60  
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have permission to set a custom time for the hunger games. The default time is 60 seconds.")
        hungergames_status[guild_id] = {
        "game_Start": False,
        "dead_tribute": None,
        "bear_disabled": False
        }
        day = 1
        tributes = []
        min_tributes = 4
        end_time = time.time() + wait_time
        messageHg = await create_embed_without_title(ctx, f":hourglass: The hunger games will start in **{wait_time} seconds.** React with ✅ to join.")
        # for member in ctx.guild.members:
        #     tributes.append({"tribute": member, "is_alive": True, "has_event": False,"team": None, "kills": 0, "inventory" : [], "days_alive" : 0, "Killed_by": None})
        await messageHg.add_reaction("✅")
        while True:
            actual_time = end_time - time.time()
            if actual_time <= 0:
                break
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=actual_time)
                if reaction.emoji == "✅":
                    allowplay = self.check_tribute_play(discord.utils.get(ctx.guild.members, id=user.id))
                    if allowplay:
                        if not any(tribute['tribute'] == user for tribute in tributes):
                            tributes.append({"tribute": user, "is_alive": True, "has_event": False,"team": None, "kills": 0, "inventory" : [], "days_alive" : 0, "Killed_by": None})
                            await create_embed_without_title(ctx, f":white_check_mark: {user.display_name} has joined the hunger games.")
                        else:
                            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} is already in the hunger games.")
                    else:
                        await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, you don't have enough eggbux to join the hunger games.")
            except asyncio.TimeoutError:
                break
        if len(tributes) < min_tributes:
            await create_embed_without_title(ctx, f":no_entry_sign: Insufficient tributes to start the hunger games. The game has been cancelled. The minimum number of tributes is **{min_tributes}**.")
            hungergames_status.pop(guild_id)
            for tribute in tributes:
                    Usuario.update(tribute['tribute'].id, Usuario.read(tribute['tribute'].id)["points"] + 100, Usuario.read(tribute['tribute'].id)["roles"])
            return
        else:
            await create_embed_without_title(ctx, f":white_check_mark: The hunger games have started with {len(tributes)} tributes.")
            alive_tributes = tributes
            while len(alive_tributes) > 1:
                shuffle_tributes = sample(alive_tributes, len(alive_tributes))
                alive_tributes = shuffle_tributes
                await create_embed_with_title(ctx, f"Day {day}", f"**Tributes remaining: {len(alive_tributes)}**")
                for tribute in alive_tributes:
                    if tribute['is_alive']:
                        await asyncio.sleep(3)
                        random_tribute = self.pick_random_tribute(tribute, alive_tributes)
                        event_possibilities = self.check_event_possibilities(tribute, random_tribute, alive_tributes, self.loot_tribute_Body(tributes), guild_id)
                        random_event = self.choose_random_event(event_possibilities)
                        await self.event_actions(ctx, tribute, random_tribute, alive_tributes, random_event)
                        alive_tributes = self.check_alive_tributes(alive_tributes)
                        if len(alive_tributes) == 1:
                            break
                fallen_tributes = [tribute for tribute in tributes if not tribute['is_alive'] and tribute['days_alive'] == day]
                if fallen_tributes:
                    await create_embed_without_title(ctx, f"**Fallen tributes:** {', '.join([tribute['tribute'].display_name for tribute in fallen_tributes])}")
                self.increase_days_alive(alive_tributes)
                self.remove_plr_team_on_death(tributes)
                self.update_tribute_event(alive_tributes)
                day += 1

            winner = alive_tributes[0]
            prizeMultiplier = len(tributes) * 50
            await create_embed_without_title(ctx, f":trophy: The winner is {winner['tribute'].display_name}! They have won {prizeMultiplier} eggbux.")
            Usuario.update(winner['tribute'].id, Usuario.read(winner['tribute'].id)["points"] + 350, Usuario.read(winner['tribute'].id)["roles"])
            hungergames_status.pop(guild_id)
            await self.statistics(ctx, tributes)

    def check_tribute_play(self, tribute):
        """Check if the tribute has enough points to play."""
        if Usuario.read(tribute.id) and Usuario.read(tribute.id)["points"] >= 50:
            Usuario.update(tribute.id, Usuario.read(tribute.id)["points"] - 50, Usuario.read(tribute.id)["roles"])
            return True
        else:
            return False
        
    def increase_days_alive(self, tributes):
        """Increase the days alive of the tributes."""
        for tribute in tributes:
            if tribute['is_alive']:
                tribute['days_alive'] += 1
     
    def check_alive_tributes(self, tributes):
        """Check the alive tributes."""
        alive_tributes = []
        for tribute in tributes:
            if tribute['is_alive']:
                alive_tributes.append(tribute)
        return alive_tributes
                
    def events(self):
        """Returns the events that can happen in the hunger games."""
        events = {
        0: "has been killed by a bear.",
        1: "has teamed up with",
        2: "has found a knife.",
        3: "has successfully stolen a",
        4: "has been killed by a trap set by",
        5: "was spotted hiding and was killed by",
        6: "narrowly escaped an ambush from",
        7: "was shot to death by",
        8: "was stabbed to death by",
        9: "has found a trap.",
        10: "has been killed by team",
        11: "has found a gun.",
        12: "slept through the night safely.",
        13: "began to hallucinate.",
        14: "has found a beautiful rock.",
        15: "has built a campfire.",
        16: "has found a map.",
        17: "spares the life of", 
        18: "is hunting for other tributes.",
        19: "has spotted ",
        20: "has looted the body of the fallen tribute",
        21: "has been betrayed by",
        22: "has disbanded from team",
        23: "team",
        24:"has triumphantly killed the entirety of team",
        25: "team",
        26: "has gifted a",
        27: "has traded a"
        }
        return events

    def choose_random_event(self, events):
        """Choose a random event from the list of events."""
        return  choice(events)
    
    def update_tribute_event(self, tributes):
        """Update the tribute event."""
        for tribute in tributes:
            tribute['has_event'] = False

    def pick_random_tribute(self, tribute1, tributes):
        """Pick a random tribute."""
        aux_tributes = tributes.copy()
        aux_tributes.remove(tribute1)
        if aux_tributes:
            return aux_tributes[randint(0, len(aux_tributes) - 1)]
        else:
            return None
    
    async def event_actions(self, ctx, tribute1, tribute2, tributes, chosen_event):
        """Perform the actions of the event."""
        events = self.events()
        print(f"Chosen event: {chosen_event}")
        if not tribute1['has_event']:
            tribute1['has_event'] = True
            match (chosen_event):
                case 0:
                    tribute1['is_alive'] = False
                    tribute1['Killed_by'] = "Bear"
                    await create_embed_without_title(ctx, f":skull_crossbones: **{tribute1['tribute'].display_name}** {events[chosen_event]}")
                case 1:
                    team = self.create_team(tribute1, tribute2, tributes)
                    await create_embed_without_title(ctx, f":people_hugging: **{tribute1['tribute'].display_name}** {events[chosen_event]} **{tribute2['tribute'].display_name}** creating team **{team}**!")
                case 2:
                    tribute1['inventory'].append("knife")
                    await create_embed_without_title(ctx, f":dagger: **{tribute1['tribute'].display_name}** {events[chosen_event]}")
                case 3:
                    item = self.steal_item(tribute1, tribute2)
                    await create_embed_without_title(ctx, f":crossed_swords: **{tribute1['tribute'].display_name}** {events[chosen_event]} {item} from **{tribute2['tribute'].display_name}**!")
                case 4:
                    tribute1['is_alive'] = False
                    tribute1['Killed_by'] = tribute2['tribute'].display_name
                    await create_embed_without_title(ctx, f":skull_crossbones: **{tribute1['tribute'].display_name}** {events[chosen_event]} **{tribute2['tribute'].display_name}**")
                    tribute2['kills'] += 1
                    tribute2['inventory'].remove("trap")
                case 5:
                    tribute1['is_alive'] = False
                    tribute1['Killed_by'] = tribute2['tribute'].display_name
                    await create_embed_without_title(ctx, f":skull_crossbones: **{tribute1['tribute'].display_name}** {events[chosen_event]} **{tribute2['tribute'].display_name}**")
                    tribute2['kills'] += 1
                case 6:
                    await create_embed_without_title(ctx, f":warning: **{tribute1['tribute'].display_name}** {events[chosen_event]} **{tribute2['tribute'].display_name}**!")
                case 7:
                    tribute1['is_alive'] = False
                    tribute1['Killed_by'] = tribute2['tribute'].display_name
                    await create_embed_without_title(ctx, f":skull_crossbones: **{tribute1['tribute'].display_name}** {events[chosen_event]} **{tribute2['tribute'].display_name}**")
                    tribute2['kills'] += 1
                    tribute2['inventory'].remove("gun")
                case 8:
                    tribute1['is_alive'] = False
                    tribute1['Killed_by'] = tribute2['tribute'].display_name
                    await create_embed_without_title(ctx, f":skull_crossbones: **{tribute1['tribute'].display_name}** {events[chosen_event]} **{tribute2['tribute'].display_name}**")
                    tribute2['kills'] += 1
                    tribute2['inventory'].remove("knife")
                case 9:
                    tribute1['inventory'].append("trap")
                    await create_embed_without_title(ctx, f":mouse_trap: **{tribute1['tribute'].display_name}** {events[chosen_event]}")
                case 10:
                    tribute1['is_alive'] = False
                    tribute1['Killed_by'] = "team " + str(tribute2['team'])
                    tribute2['kills'] += 1
                    for tribute in tributes:
                        if tribute['team'] == tribute2['team'] and tribute['is_alive']:
                            if tribute['team'] is not None:
                                tribute['kills'] += 1
                    await create_embed_without_title(ctx, f":skull_crossbones: **{tribute1['tribute'].display_name}** {events[chosen_event]} **{tribute2['team']}**!")
                case 11:
                    tribute1['inventory'].append("gun")
                    await create_embed_without_title(ctx, f":gun: **{tribute1['tribute'].display_name}** {events[chosen_event]}")
                case 17:
                    await create_embed_without_title(ctx, f":flag_white: **{tribute1['tribute'].display_name}** {events[chosen_event]} **{tribute2['tribute'].display_name}**!")
                case 19:
                    await create_embed_without_title(ctx, f":warning: **{tribute1['tribute'].display_name}** {events[chosen_event]} **{tribute2['tribute'].display_name}** running in the distance!")
                case 20:
                    dead_tribute = hungergames_status[ctx.guild.id]['dead_tribute']
                    item = self.steal_item(tribute1, dead_tribute)
                    await create_embed_without_title(ctx, f":ninja: **{tribute1['tribute'].display_name}** {events[chosen_event]} **{dead_tribute['tribute'].display_name}** stealing a {item} in the process!")
                case 21:
                    await create_embed_without_title(ctx, f":broken_heart: **{tribute1['tribute'].display_name}** {events[chosen_event]} **{tribute2['tribute'].display_name}**!")
                    tribute1['team'] = None
                    tribute2['team'] = None
                    tribute1['is_alive'] = False
                    tribute1['Killed_by'] = tribute2['tribute'].display_name
                    tribute2['kills'] += 1
                case 22:
                    disbanded_team = self.get_tribute_team(tribute1, tributes)
                    await create_embed_without_title(ctx, f":broken_heart: **{tribute1['tribute'].display_name}** {events[chosen_event]} **{disbanded_team}**!")
                    for tribute in tributes:
                        if tribute['team'] == disbanded_team:
                            tribute['team'] = None
                case 23:
                    for tribute in tributes:
                        if tribute['team'] == tribute1['team']:
                            tribute['is_alive'] = False
                            tribute['Killed_by'] = "team " + str(tribute2['team'])
                            tribute1['is_alive'] = False
                            tribute1['Killed_by'] = "team " + str(tribute2['team'])
                        if tribute['team'] == tribute2['team']:
                            tribute['kills'] += 1
                            tribute2['kills'] += 1
                    await create_embed_without_title(ctx, f":skull_crossbones: {events[chosen_event]} **{tribute1['team']}** has been eliminated by team **{tribute2['team']}**!")
                case 24:
                    for tribute in tributes:
                        if tribute['team'] == tribute2['team']:
                            tribute['is_alive'] = False
                            tribute['Killed_by'] = tribute1['tribute'].display_name
                            tribute2['is_alive'] = False
                            tribute2['Killed_by'] = tribute1['tribute'].display_name
                    tribute1['kills'] += 2
                    await create_embed_without_title(ctx, f":zap: **{tribute1['tribute'].display_name}** {events[chosen_event]} **{tribute2['team']}**!")
                case 25:
                    team = self.get_tribute_team(tribute1, tributes)
                    await create_embed_without_title(ctx, f":bear: {events[chosen_event]} **{team}** has managed to kill the bear, disabling that for the rest of the game.")
                    hungergames_status[ctx.guild.id]['bear_disabled'] = True
                case 26:
                    tribute1Item = choice(tribute1['inventory'])
                    tribute2['inventory'].append(tribute1Item)
                    tribute1['inventory'].remove(tribute1Item)
                    await create_embed_without_title(ctx, f":gift: **{tribute1['tribute'].display_name}** {events[chosen_event]} {tribute1Item} to **{tribute2['tribute'].display_name}**!")
                case 27:
                    tribute1Item = choice(tribute1['inventory'])
                    tribute2Item = choice(tribute2['inventory'])
                    tribute1['inventory'].append(tribute2Item)
                    tribute2['inventory'].append(tribute1Item)
                    tribute1['inventory'].remove(tribute1Item)
                    tribute2['inventory'].remove(tribute2Item)
                    await create_embed_without_title(ctx, f":handshake: **{tribute1['tribute'].display_name}** {events[chosen_event]} {tribute1Item} for a {tribute2Item} with **{tribute2['tribute'].display_name}**!")
                case _:
                    await create_embed_without_title(ctx, f"**{tribute1['tribute'].display_name}** {events[chosen_event]}")


    def check_event_possibilities(self, tribute1, tribute2, tributes, dead_tributes, guild_id):
        """Check the event possibilities."""
        global hungergames_status
        list_events = list(range(20))

        collect_requirements = {
                2: "knife",
                9: "trap",
                11: "gun"
            }
        
        list_events = [event for event in list_events if event not in collect_requirements.keys() or collect_requirements[event] not in tribute1['inventory']]
        
        if dead_tributes:
            dead_tribute = hungergames_status[guild_id]['dead_tribute'] = choice(dead_tributes)
            if dead_tribute and not any(item for item in tribute1['inventory'] if item in dead_tribute['inventory']):
                list_events.append(20)

        bear_events = [0, 25]

        if hungergames_status[guild_id]['bear_disabled']:
            list_events = [event for event in list_events if event not in bear_events]

        if tribute2:

            kill_requirements = {
                4: "trap",
                7: "gun",
                8: "knife"
            }
            
            list_events = [event for event in list_events if event not in kill_requirements.keys() or kill_requirements[event] in tribute2['inventory']]

            if not tribute2['inventory'] and not any(item in tribute1['inventory'] for item in tribute2['inventory'] if item in tribute2['inventory']):
                list_events = [event for event in list_events if event != 3]

            if tribute1['team'] is not None or tribute2['team'] is not None: 
                list_events = [event for event in list_events if event != 1]

            if len(tribute1['inventory']) and len(tribute2['inventory']) and not any(item in tribute1['inventory'] for item in tribute2['inventory'] if item in tribute2['inventory']):
                list_events.append(27)

            if len(tribute1['inventory']) >= 2 and len(tribute2['inventory']) == 0:
                list_events.append(26)
            
            friendly_fire_events = [3, 4, 5, 6, 7, 8, 10, 17, 19]

            if tribute1['team'] == tribute2['team'] and tribute1['team'] is not None and tribute2['team'] is not None:
                list_events = [event for event in list_events if event not in friendly_fire_events]
                list_events.append(21)
                list_events.append(22)

            no_team_events = [10, 21, 22, 23]

            if tribute2['team'] is None:
                list_events = [event for event in list_events if event not in no_team_events]

            if len(tributes) == 2 and tribute1['team'] == tribute2['team'] and tribute1['team'] is not None and tribute2['team'] is not None:
                list_events = [21, 22]

            existing_teams = self.check_existing_teams(tributes)

            if len(existing_teams) >= 2 and tribute2['team'] is not None and tribute1['team'] is not None and tribute1['team'] != tribute2['team']:
                list_events = [event for event in list_events]
                list_events.append(23)

            if len(existing_teams) >= 1 and tribute2['team'] is not None and tribute1['team'] is None and len(tribute1['inventory']) >= 1:
                list_events = [event for event in list_events]
                list_events.append(24)

            if tribute1['team'] is not None and not hungergames_status[guild_id]['bear_disabled']:
                list_events.append(25)

            if len(existing_teams) == 0:
                list_events = [event for event in list_events if event != 10]

            finalists_events = [1, 26, 27]

            if len(tributes) == 2:
                list_events = [event for event in list_events if event not in finalists_events]
        else:
            tribute2_events = [1, 3, 4, 5, 6, 7, 8, 10, 17, 19, 21, 22, 23, 24]
            list_events = [event for event in list_events if event not in tribute2_events]
        print(f"List of events: {list_events}")
        return list_events

    def remove_plr_team_on_death(self, tributes):
        """Remove the player's team on death."""
        teams_to_remove = set()

        for tribute in tributes:
            if not tribute['is_alive']:
                teams_to_remove.add(tribute['team'])

        for tribute in tributes:
            if tribute['team'] in teams_to_remove and tribute['is_alive']:
                tribute['team'] = None

    def steal_item(self, tribute1, tribute2):
        """Steal an item from a tribute."""
        item = choice(tribute2['inventory'])
        tribute1['inventory'].append(item)
        tribute2['inventory'].remove(item)
        return item
    
    def loot_tribute_Body(self, tributes):
        """Loot the body of a fallen tribute."""
        dead_tributes = [dead_tribute for dead_tribute in tributes if not dead_tribute['is_alive'] and len(dead_tribute['inventory']) > 0]
        if len(dead_tributes) >= 1:
            return dead_tributes
        else:
            return None
    
    async def statistics(self, ctx, tributes):
        """Show the statistics of the hungergames match."""
        data = []
        for tribute in tributes:
            data.append(
            {"title": ":medal: " + tribute['tribute'].display_name if self.get_winner(tributes) == tribute else ":skull_crossbones: " + tribute['tribute'].display_name, 
            "value": (
                f"Kills: {str(tribute['kills'])}" 
                + f"\n Days survived: {str(tribute['days_alive'])}" 
                + "\n" + (f" Team: {str(tribute['team'])}" if tribute['team'] is not None else "Team: No team.") 
                + "\n" + (f"Inventory: {str(tribute['inventory'])}" if tribute['inventory'] else "Inventory: No items.") +
                "\n" + (f"Killed by: {tribute['Killed_by']}" if tribute['Killed_by'] is not None else "Killed by: No one.")
                )
            })
        sorted_data = sorted(data, key=lambda x: x['value'], reverse=True)
        view = PaginationView(sorted_data)
        await view.send(ctx, title="Match results:", description="Match statistics for each tribute:", color=0xff0000)
        
    
    def create_team(self, tribute1, tribute2, tributes):
        """Create a team."""
        teams = self.check_existing_teams(tributes)
        teamNumber = randint(1, 100)
        if teamNumber not in teams.keys():
            tribute1['team'] = teamNumber
            tribute2['team'] = teamNumber
            return teamNumber
        else:
            self.create_team(tribute1, tribute2, tributes)

    def check_existing_teams(self, tributes):
        """Check the existing teams."""
        teams = Counter([tribute['team'] for tribute in tributes if tribute['team'] is not None])
        return teams
    
    def get_tribute_team(self, tribute1, tributes):
        """Get the tribute team."""
        for tribute in tributes:
            if tribute1['team'] == tribute['team']:
                return tribute1['team']
    
    def get_winner(self, tributes):
        """Get the winner of the hunger games."""
        highestdayAlive = 0
        for tribute in tributes:
            if tribute['days_alive'] > highestdayAlive:
                highestdayAlive = tribute['days_alive']
                winner = tribute
        return winner
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.drop_periodically())
        self.bot.loop.create_task(self.work_periodically())

async def setup(bot):
    await bot.add_cog(InteractiveCommands(bot))