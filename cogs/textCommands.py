# Description: cog that contains administration and fun commands
import asyncio
import time
import discord.message
from collections import Counter
from random import randint
from discord.ext import commands
import discord
from db.userDB import Usuario
import os
import random
from tools.pagination import PaginationView
from tools.pricing import pricing, refund

# This class is responsible for handling the text commands.
class TextCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        bot.remove_command('help')

    @commands.Cog.listener()
    async def on_ready(self):
        asyncio.create_task(self.work_periodically())


    @commands.command()
    @pricing()
    async def balls(self, ctx):
        await ctx.send("balls")

    @commands.command()
    @pricing()
    async def mog(self, ctx, User: discord.Member):
            path = random.choice(os.listdir("images/mogged/"))
            await ctx.send(file=discord.File("images/mogged/"+path))
            await ctx.send(f"{User.mention} bye bye 🤫🧏‍♂️")

    @commands.command()
    @pricing()
    async def purge(self, ctx, amount: int):
        if amount > 0 and amount <= 25:
            await ctx.channel.purge(limit=amount + 1)
        else:
            await ctx.send("Please, insert a number between 1 and 25.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def kick(self, ctx, User: discord.Member):
        if User.id == ctx.author.id:
                await ctx.send("You can't kick yourself.")
                await refund(ctx.author, ctx) 
                return
        if User.top_role.position <= ctx.guild.me.top_role.position:
            try:
                await User.kick()
                await ctx.send(f"{User.mention} was kicked.")
            except discord.errors.Forbidden:
                await ctx.send(f"{ctx.author.mention}, you don't have permission to do that.")
                await refund(ctx.author, ctx)
                return
        else:
            await ctx.send("I don't have permission to do that.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def ban(self, ctx, User: discord.Member):
        if User.id == ctx.author.id:
                await ctx.send("You can't ban yourself.")
                await refund(ctx.author, ctx)
                return
        if User.top_role.position <= ctx.guild.me.top_role.position:
            try:
                await User.ban()
                await ctx.send(f"{User.mention} was banned.")
            except discord.errors.Forbidden:
                await ctx.send(f"{ctx.author.mention}, you don't have permission to do that")
                await refund(ctx.author, ctx)
                return
        else:
            await ctx.send("I don't have permission to do that.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def changeNickname(self, ctx, User: discord.Member, *apelido: str):
        if User.top_role.position <= ctx.guild.me.top_role.position:
            if User.id == ctx.me.id:
                await ctx.send("I can't change my own nickname.")
                await refund(ctx.author, ctx)
                return
            else:
                apelido = " ".join(apelido)
                await User.edit(nick=apelido)
                await ctx.send(f"{User.mention}'s nickname has changed to {apelido}.")   
        else:
            await refund(ctx.author, ctx)
            await ctx.send("I don't have permission to do that.")

    @commands.command()
    async def help(self, ctx):
         pass

    @commands.command()
    @pricing()
    async def pardon(self, ctx, id: str):
        User = await self.bot.fetch_user(id)
        if await ctx.guild.fetch_ban(User):
            await ctx.guild.unban(User)
            await ctx.send(f"{User.mention} has been unbanned.")
        else:
            await ctx.send("This user is not banned.")
            await refund(ctx.author, ctx)
            
    @commands.command()
    @pricing()
    async def lowWageRole(self, ctx):
         if Usuario.read(ctx.author.id):    
            permissions = discord.Permissions(
                move_members = True,
            )
            role = discord.utils.get(ctx.guild.roles, name="Low wage worker")
            if role is None:
                role = await ctx.guild.create_role(name="Low wage worker", permissions=permissions, color=discord.Color.from_rgb(165, 42, 42))
                await role.edit(position=9, hoist=True, mentionable=True)
            if ctx.author in role.members:
                await ctx.send("You already have this role.")
                return
            if Usuario.read(ctx.author.id)["roles"] == "":
                await ctx.author.add_roles(role)
                await ctx.send(f"{ctx.author.mention} received the low wage worker role.")


    @commands.command()
    @pricing()
    async def lowClassRole(self, ctx):
        if Usuario.read(ctx.author.id):    
             permissions = discord.Permissions(
                 move_members = True,
                 mute_members = True,
                 deafen_members = True
             )
             role = discord.utils.get(ctx.guild.roles, name="Peasant")
             if role is None:
                    role = await ctx.guild.create_role(name="Peasant", permissions=permissions, color=discord.Color.from_rgb(255, 0, 0))
                    await role.edit(position=8, hoist=True, mentionable=True)
             if ctx.author in role.members:
                    await ctx.send("You already have this role.")
                    await refund(ctx.author, ctx)
                    return
             if Usuario.read(ctx.author.id)["roles"] == "T":
                await ctx.author.add_roles(role)
                await ctx.send(f"{ctx.author.mention} received the low class role.")
             else:
                await ctx.send("You don't have one or more of the necessary roles.")
                await refund(ctx.author, ctx)   

    @commands.command()
    @pricing()
    async def middleClassRole(self, ctx):
        if Usuario.read(ctx.author.id):    
             permissions = discord.Permissions(
                 move_members = True,
                 mute_members = True,
                 deafen_members = True,
                 manage_messages = True
             )
             role = discord.utils.get(ctx.guild.roles, name="Brokie who thinks they are rich")
             if role is None:
                    role = await ctx.guild.create_role(name="Brokie who thinks they are rich", permissions=permissions, color=discord.Color.from_rgb(0, 0, 255))
                    await role.edit(position=7, hoist=True, mentionable=True)
             if ctx.author in role.members:
                    await ctx.send("You already have this role.")
                    await refund(ctx.author, ctx)
                    return
             if Usuario.read(ctx.author.id)["roles"] == "TB":
                await ctx.author.add_roles(role)
                await ctx.send(f"{ctx.author.mention} received the middle class role.")
             else:
                    await ctx.send("You don't have one or more of the necessary roles.")
                    await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def highClassRole(self, ctx):
         if Usuario.read(ctx.author.id):    
             permissions = discord.Permissions(
                 move_members = True,
                 mute_members = True,
                 deafen_members = True,
                 manage_messages = True,
                 manage_channels = True
             )
             role = discord.utils.get(ctx.guild.roles, name="Magnate")
             if role is None:
                    role = await ctx.guild.create_role(name="Magnate", permissions=permissions, color=discord.Color.from_rgb(0, 0, 0))
                    await role.edit(position=6, hoist=True, mentionable=True)
             if ctx.author in role.members:
                    await ctx.send("You already have this role.")
                    await refund(ctx.author, ctx)
                    return
             if Usuario.read(ctx.author.id)["roles"] == "TBM":
                await ctx.author.add_roles(role)
                await ctx.send(f"{ctx.author.mention} received the high class role.")
             else:
                  await ctx.send("You don't have one or more of the necessary roles.")
                  await refund(ctx.author, ctx)

    def salarioCargo(self, User:discord.Member):
        salarios = {
            "T": 50,
            "B": 100,
            "M": 200,
            "A": 300
        }
        if Usuario.read(User.id):
            return salarios[Usuario.read(User.id)["roles"] [-1]]
        else:
            return 0
        
    async def work_periodically(self):
        while True:
            for guild in self.bot.guilds:
                for member in guild.members:
                        user_data = Usuario.read(member.id)
                        if user_data:
                            if user_data["roles"] != "":
                                Usuario.update(member.id, Usuario.read(member.id)["points"] + self.salarioCargo(member), Usuario.read(member.id)["roles"])
                await asyncio.sleep(1600)

    @commands.command("salary", aliases=["income"])
    async def salary(self, ctx, User: discord.Member = None):
        if User is None:
            User = ctx.author
        user_data = Usuario.read(User.id)
        if user_data:
            if user_data["roles"] != "":
                await ctx.send(f"{User.display_name} earns {self.salarioCargo(User)} eggbux of salary.")
                return   
            await ctx.send(f"{User.display_name} doesn't have a custom role that receives a salary.")
        else:
            await ctx.send(f"{User.display_name} is not registered in the database.")
            await refund(ctx.author, ctx) 

    @commands.command()
    async def hungergames(self, ctx):
        day = 1
        tributes = []
        wait_time = 10
        end_time = time.time() + wait_time
        tributes.append({"tribute": discord.utils.get(ctx.guild.members, id=675996677366218774), "is_alive": True, "has_event": False,"team": None, "kills": 0, "inventory" : [], "days_alive" : 0})
        tributes.append({"tribute": discord.utils.get(ctx.guild.members, id=656621136808902656), "is_alive": True, "has_event": False,"team": None, "kills": 0, "inventory" : [], "days_alive" : 0})
        tributes.append({"tribute": discord.utils.get(ctx.guild.members, id=247283454440374274), "is_alive": True, "has_event": False,"team": None, "kills": 0, "inventory" : [], "days_alive" : 0})
        tributes.append({"tribute": discord.utils.get(ctx.guild.members, id=411916947773587456), "is_alive": True, "has_event": False,"team": None, "kills": 0, "inventory" : [], "days_alive" : 0})
        tributes.append({"tribute": discord.utils.get(ctx.guild.members, id=692045914436796436), "is_alive": True, "has_event": False,"team": None, "kills": 0, "inventory" : [], "days_alive" : 0})
        await ctx.send(f"The hunger games are about to start. Type !join to join the hunger games. You have {wait_time} seconds to join.")
        while True:
            actual_time = end_time - time.time()
            if actual_time <= 0:
                break
            try:
                message = await asyncio.wait_for(self.bot.wait_for("message", check=lambda message: message.content == "!join"), timeout=actual_time)
                allowplay = self.checkIfTributePlay(discord.utils.get(ctx.guild.members, id=message.author.id))
                if allowplay:
                    if not any(tribute['tribute'] == message.author for tribute in tributes):
                        tributes.append({"tribute": message.author, "is_alive": True, "has_event": False,"team": None, "kills": 0, "inventory" : [], "days_alive" : 0})
                        await ctx.send(f"{message.author.display_name} has joined the hunger games.")
                    else:
                        await ctx.send(f"{message.author.display_name} is already in the hunger games.")
                else:
                    await ctx.send(f"{message.author.display_name} doesn't have enough eggbux to join the hunger games.")
            except asyncio.TimeoutError:
                break
        if len(tributes) < 2:
            await ctx.send("Not enough players to start the hunger games. At least 4 players are needed.")
            Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + 200, Usuario.read(ctx.author.id)["roles"])
            return
        else:
            await ctx.send("# The hunger games have started.")
            alive_tributes = tributes
            while len(alive_tributes) > 1:
                await ctx.send(f"## Day {day} has started.")
                for tribute in alive_tributes:
                    if tribute['is_alive']:
                        await asyncio.sleep(3)
                        print(f"Tribute: {tribute['tribute'].display_name}, inventory: {tribute['inventory']}")
                        random_tribute = self.pickRandomTribute(tribute, alive_tributes)
                        if random_tribute:
                            print(f"Random tribute: {random_tribute['tribute'].display_name}, inventory: {random_tribute['inventory']}")
                        else:
                            print("Random tribute: None")
                        event_possibilities = self.checkEventPossibilities(tribute, random_tribute, alive_tributes)
                        print(f"Possibilities: {event_possibilities}")
                        random_event = self.chooseRandomEvent(event_possibilities)
                        await self.eventActions(ctx, tribute, random_tribute, alive_tributes, random_event)
                        alive_tributes = self.checkAliveTributes(alive_tributes)
                        if len(alive_tributes) == 1:
                            break
                await ctx.send(f"**Tributes remaining: {len(alive_tributes)}**")
                self.increaseDaysAlive(alive_tributes)
                self.removePlrTeamOnDeath(tributes)
                self.updateTributeEvent(alive_tributes)
                day += 1

            winner = alive_tributes[0]
            await ctx.send(f"{winner['tribute'].display_name} has won the hunger games and has won 350 Eggbux!.")
            #Usuario.update(winner['tribute'].id, Usuario.read(winner['tribute'].id)["points"] + 350, Usuario.read(winner['tribute'].id)["roles"])
            await self.statistics(ctx, tributes)


    def checkIfTributePlay(self, tribute):
        if Usuario.read(tribute.id) and Usuario.read(tribute.id)["points"] >= 50:
            Usuario.update(tribute.id, Usuario.read(tribute.id)["points"] - 50, Usuario.read(tribute.id)["roles"])
            return True
        else:
            return False
        
    def increaseDaysAlive(self, tributes):
        for tribute in tributes:
            if tribute['is_alive']:
                tribute['days_alive'] += 1
     
    def checkAliveTributes(self, tributes):
        alive_tributes = []
        for tribute in tributes:
            if tribute['is_alive']:
                alive_tributes.append(tribute)
        return alive_tributes
                
    def events(self):
        events = {
        0: "has been killed by a bear.",
        1: "has teamed up with",
        2: "has found a knife.",
        3: "has successfully stolen a",
        4: "has been killed by a trap set by",
        5: "was spotted hiding and was killed by",
        6: "narrowly escaped an ambush from",
        7: "was shot by",
        8: "was stabbed by",
        9: "has found a trap.",
        10: "has been killed by team",
        11: "has found a gun.",
        12: "slept through the night safely.",
        13: "began to hallucinate.",
        14: "has found a beautiful rock.",
        15: "has built a campfire.",
        16: "has found a map.", 
        17: "has been betrayed by",
        18: "has disbanded team",
        19: "team"
        }
        return events

    def chooseRandomEvent(self, events):
        return random.choice(events)
    
    def updateTributeEvent(self, tributes):
        for tribute in tributes:
            tribute['has_event'] = False
    

    def pickRandomTribute(self, tribute1, tributes):
        aux_tributes = tributes.copy()
        aux_tributes.remove(tribute1)
        if aux_tributes:
            return aux_tributes[randint(0, len(aux_tributes) - 1)]
        else:
            return None
    
    
    async def eventActions(self, ctx, tribute1, tribute2, tributes, chosen_event):
        events = self.events()
        print(f"Chosen event: {chosen_event}")
        if not tribute1['has_event']:
            tribute1['has_event'] = True
            match (chosen_event):
                case 0:
                    tribute1['is_alive'] = False
                    await ctx.send(f"{tribute1['tribute'].display_name} {events[chosen_event]}")
                case 1:
                    team = self.createTeam(tribute1, tribute2, tributes)
                    await ctx.send(f"{tribute1['tribute'].display_name} {events[chosen_event]} {tribute2['tribute'].display_name} creating team {team}!")
                case 2:
                    tribute1['inventory'].append("knife")
                    await ctx.send(f"{tribute1['tribute'].display_name} {events[chosen_event]}")
                case 3:
                    item = self.stealItem(tribute1, tribute2)
                    await ctx.send(f"{tribute1['tribute'].display_name} {events[chosen_event]} {item} from {tribute2['tribute'].display_name}.")
                case 4:
                    tribute1['is_alive'] = False
                    await ctx.send(f"{tribute1['tribute'].display_name} {events[chosen_event]} {tribute2['tribute'].display_name}")
                    tribute2['kills'] += 1
                    tribute2['inventory'].remove("trap")
                case 5:
                    tribute1['is_alive'] = False
                    await ctx.send(f"{tribute1['tribute'].display_name} {events[chosen_event]} {tribute2['tribute'].display_name}")
                    tribute2['kills'] += 1
                case 6:
                    await ctx.send(f"{tribute1['tribute'].display_name} {events[chosen_event]} {tribute2['tribute'].display_name}")
                case 7:
                    tribute1['is_alive'] = False
                    await ctx.send(f"{tribute1['tribute'].display_name} {events[chosen_event]} {tribute2['tribute'].display_name}")
                    tribute2['kills'] += 1
                    tribute2['inventory'].remove("gun")
                case 8:
                    tribute1['is_alive'] = False
                    await ctx.send(f"{tribute1['tribute'].display_name} {events[chosen_event]} {tribute2['tribute'].display_name}")
                    tribute2['kills'] += 1
                    tribute2['inventory'].remove("knife")
                case 9:
                    tribute1['inventory'].append("trap")
                    await ctx.send(f"{tribute1['tribute'].display_name} {events[chosen_event]}")
                case 10:
                    await ctx.send(f"{tribute1['tribute'].display_name} {events[chosen_event]} {tribute2['team']}!")
                    tribute1['is_alive'] = False
                    tribute2['kills'] += 1
                    for tribute in tributes:
                        if tribute['team'] == tribute2['team'] and tribute['is_alive']:
                            if tribute['team'] is not None:
                                tribute['kills'] += 1
                case 11:
                    tribute1['inventory'].append("gun")
                    await ctx.send(f"{tribute1['tribute'].display_name} {events[chosen_event]}")
                case 17:
                    await ctx.send(f"{tribute1['tribute'].display_name} {events[chosen_event]} {tribute2['tribute'].display_name}!")
                    tribute1['team'] = None
                    tribute2['team'] = None
                    tribute1['is_alive'] = False
                    tribute2['kills'] += 1
                case 18:
                    disbanded_team = self.getTributeTeam(tribute1, tributes)
                    await ctx.send(f"{tribute1['tribute'].display_name} {events[chosen_event]} team {disbanded_team}!")
                    for tribute in tributes:
                        if tribute['team'] == disbanded_team:
                            tribute['team'] = None
                case 19:
                    for tribute in tributes:
                        if tribute['team'] == tribute1['team']:
                            tribute['is_alive'] = False
                            tribute1['is_alive'] = False
                        if tribute['team'] == tribute2['team']:
                            tribute['kills'] += 1
                            tribute2['kills'] += 1
                    await ctx.send(f"{events[chosen_event]} {tribute1['team']} has been eliminated by team {tribute2['team']}!")
                case _:
                    await ctx.send(f"{tribute1['tribute'].display_name} {events[chosen_event]}")


    def checkEventPossibilities(self, tribute1, tribute2, tributes):
        list_events = list(range(17))

        collect_requirements = {
                2: "knife",
                9: "trap",
                11: "gun"
            }
        
        list_events = [event for event in list_events if event not in collect_requirements.keys() or collect_requirements[event] not in tribute1['inventory']]

        if tribute2:

            kill_requirements = {
                4: "trap",
                7: "gun",
                8: "knife"
            }
            
            list_events = [event for event in list_events if event not in kill_requirements.keys() or kill_requirements[event] in tribute2['inventory']]

            if not tribute2['inventory']:
                list_events = [event for event in list_events if event != 3]

            if tribute1['team'] is not None or tribute2['team'] is not None: 
                list_events = [event for event in list_events if event != 1]

            friendly_fire_events = [4, 5, 6, 7, 8, 10]

            if tribute1['team'] == tribute2['team'] and tribute1['team'] is not None and tribute2['team'] is not None:
                list_events = [event for event in list_events if event not in friendly_fire_events]
                list_events.append(17)
                list_events.append(18)

            if tribute2['team'] is None:
                list_events = [event for event in list_events if event != 10]

            if len(tributes) == 2 and tribute1['team'] == tribute2['team'] and tribute1['team'] is not None and tribute2['team'] is not None:
                list_events = [17, 18]

            existing_teams = self.checkExistingTeams(tributes)

            if len(existing_teams) >= 2 and tribute2['team'] is not None and tribute1['team'] is not None and tribute1['team'] != tribute2['team']:
                list_events = [event for event in list_events]
                list_events.append(19)

            if len(existing_teams) == 0:
                list_events = [event for event in list_events if event != 10]

        else:
            tribute2_events = [1, 3, 4, 5, 6, 7, 8, 10]
            list_events = [event for event in list_events if event not in tribute2_events]

        return list_events


    def removePlrTeamOnDeath(self, tributes):
        teams_to_remove = set()

        for tribute in tributes:
            if not tribute['is_alive']:
                teams_to_remove.add(tribute['team'])

        for tribute in tributes:
            if tribute['team'] in teams_to_remove and tribute['is_alive']:
                tribute['team'] = None

    def stealItem(self, tribute1, tribute2):
        item = random.choice(tribute2['inventory'])
        tribute1['inventory'].append(item)
        tribute2['inventory'].remove(item)
        return item
    
    async def statistics (self, ctx, tributes):
        data = []
        for tribute in tributes:
            data.append(
            {"title": tribute['tribute'].display_name, 
            "value": (
                f"Kills: {str(tribute['kills'])}" 
                + f"\n Days survived: {str(tribute['days_alive'])}" 
                + "\n" + (f" Team: {str(tribute['team'])}" if tribute['team'] is not None else "Team: No team.") 
                + "\n" + (f"Inventory: {str(tribute['inventory'])}" if tribute['inventory'] else "Inventory: No items.")
                )
            })
        sorted_data = sorted(data, key=lambda x: x['value'], reverse=True)
        view = PaginationView(sorted_data)
        await view.send(ctx, title="Match results:", description="Match statistics for each tribute:", color=0xff0000)
        
    
    def createTeam(self, tribute1, tribute2, tributes):
        teams = self.checkExistingTeams(tributes)
        teamNumber = randint(1, 100)
        if teamNumber not in teams.keys():
            tribute1['team'] = teamNumber
            tribute2['team'] = teamNumber
            return teamNumber
        else:
            self.createTeam(tribute1, tribute2, tributes)

    def checkExistingTeams(self, tributes):
        teams = Counter([tribute['team'] for tribute in tributes if tribute['team'] is not None])
        return teams
    
    def getTributeTeam(self, tribute1, tributes):
        for tribute in tributes:
            if tribute1['team'] == tribute['team']:
                return tribute1['team']

   
    @commands.command()
    @pricing()
    async def nuke(self, ctx):
        await Usuario.deleteAll()
        await ctx.send("Database has been nuked.")
              
async def setup(bot):
    await bot.add_cog(TextCommands(bot))