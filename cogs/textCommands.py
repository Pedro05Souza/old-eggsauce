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
        round = 1
        tributes = []
        limit_time = time.time() + 20
        await ctx.send("The hunger games are starting in 20 seconds. Type !join to participate.")
        while time.time() != limit_time:
            if time.time() == limit_time:
                break
        message = await self.bot.wait_for("message", check=lambda message: message.content == "!join")
        if Usuario.read(message.author.id):
            if message.author not in tributes:
                tributes.append({"tribute" : message.author, "kills": 0, "inventory" : [] ,"is_alive": True, "has_event" : False, "event" : None, "team": 0, "has_team" : False})
                await ctx.send(f"{message.author.display_name} has joined the hunger games.")
            else:
                await ctx.send(f"{message.author.display_name} is already in the hunger games.")
        else:
            await ctx.send(f"{message.author.display_name} is not registered in the database.")
        await ctx.send("The hunger games have started.")
        alive_tributes = tributes
        while len(alive_tributes) > 1:
            ctx.send(f"# Round {round} has officialy begun.")
            for tribute in alive_tributes:
                if tribute["has_event"] == False:
                    event = self.events()
                    random_tributes = self.pickRandomTribute(tribute, alive_tributes)
                    await self.eventActions(ctx, alive_tributes, tribute, random_tributes, event)
                    alive_tributes = self.checkAliveTributes(alive_tributes)
            round += 1
            alive_tributes = self.disableHasEventPerRound(alive_tributes)    
        winner = alive_tributes[0]
        await ctx.send(f"{winner['tribute'].display_name} has won the hunger games. Congratulations for winning 200 eggbux.")
        Usuario.update(winner["tribute"].id, Usuario.read(winner["tribute"].id)["points"] + 200, Usuario.read(winner["tribute"].id)["roles"])

    def checkAliveTributes(self, tributes):
        alive_tributes = []
        for tribute in tributes:
            if tribute['is_alive']:
                alive_tributes.append(tribute)
        
        return alive_tributes
        
    def events(self):
        events = {
        0: " has been killed by a bear.",
        1: " has teamed up with",
        2: " has found a knife.",
        3: " has successfully stole a .",
        4: " has been killed by a trap set by",
        5: " was spotted hiding and was killed by",
        6: " narrowly escaped an ambush from ",
        7: " was shot by",
        8: " was stabbed by ",
        9: " has found a trap.",
        10: "has been killed by team ",
        11: " has found a gun.",
        12: " slept throught the night safely.",
        13: " began to hallucinate.",
        14: " has found a beatiful rock.",
        15: "has built a campfire.",
        16: " has found a map.", 
        17: "has been betrayed by "
        }
        return events
    
    async def eventActions(self, ctx, tributes, tribute1, tribute2, event):
        if tribute1['has_event'] == False and tribute2['has_event'] == False:
            tributeEvent = self.pickEventRandom(tributes, tribute1, tribute2)
            tribute1['has_event'] = True
            tribute2['has_event'] = True
            match (tributeEvent):
                case 0:
                    await ctx.send(f"{tribute1['tribute'].display_name} {event[tributeEvent]}")
                    tribute1['is_alive'] = False 
                case 1:
                    await ctx.send(f"{tribute1['tribute'].display_name} {event[tributeEvent]} {tribute2['tribute'].display_name}")
                    self.pickTributeTeam(tributes, tribute1, tribute2)
                case 2:
                    await ctx.send(f"{tribute1['tribute'].display_name} {event[tributeEvent]}")
                    tribute1['inventory'].append("knife")
                case 3:
                    if tribute2['inventory']:
                        stolen_item = random.choice(tribute2['inventory'])
                        tribute1['inventory'].append(stolen_item)
                        tribute2['inventory'].remove(stolen_item)
                        await ctx.send(f"{tribute1['tribute'].display_name} {event[tributeEvent]} {tribute2['tribute'].display_name}'s {stolen_item}") 
                case 4:
                    if "trap" in tribute2['inventory']:
                        await ctx.send(f"{tribute2['tribute'].display_name} {event[tributeEvent]} {tribute1['tribute'].display_name}")
                        tribute1['is_alive'] = False
                        tribute1['inventory'].remove("trap")
                case 5:
                    await ctx.send(f"{tribute1['tribute'].display_name} {event[tributeEvent]} {tribute2['tribute'].display_name}")
                    tribute2['is_alive'] = False
                case 6:
                    await ctx.send(f"{tribute1['tribute'].display_name} {event[tributeEvent]} {tribute2['tribute'].display_name}")
                case 7:
                    if "gun" in tribute2['inventory']:
                        await ctx.send(f"{tribute2['tribute'].display_name} {event[tributeEvent]} {tribute1['tribute'].display_name}")
                        tribute1['is_alive'] = False
                        tribute2['inventory'].remove("gun")
                case 8:
                    if "knife" in tribute2['inventory']:
                        await ctx.send(f"{tribute2['tribute'].display_name} {event[tributeEvent]} {tribute1['tribute'].display_name}")
                        tribute1['is_alive'] = False
                        tribute2['inventory'].remove("knife")
                case 9:
                    await ctx.send(f"{tribute1['tribute'].display_name} {event[tributeEvent]}")
                    tribute1['inventory'].append("trap")
                case 10:
                    await ctx.send(f"{tribute1['tribute'].display_name} {event[tributeEvent]} {tribute2['team']}")
                    tribute2['is_alive'] = False
                case 11:
                    await ctx.send(f"{tribute1['tribute'].display_name} {event[tributeEvent]}")
                    tribute1['inventory'].append("gun")
                case 17:
                    await ctx.send(f"{tribute1['tribute'].display_name} {event[tributeEvent]} {tribute2['tribute'].display_name}")
                    tribute1['is_alive'] = False
                case _:
                    await ctx.send(f"{tribute1['tribute'].display_name} {event[tributeEvent]}")


    def disableHasEventPerRound(self, tributes):
        for tribute in tributes:
            tribute['has_event'] = False
        return tributes
    
    def checkIfTributesAreInSameTeam(self, tribute1, tribute2):
        return tribute1['team'] == tribute2['team']
    
    def pickEventRandom(self, tributes, tribute1, tribute2):
        choices = list(range(17))
        tribute1Inv = tribute1['inventory']
        tribute2Inv = tribute2['inventory']
        teams = Counter(teams for teams in tributes['team'] if teams != 0)
        match (tribute2Inv):
            case []:
                choices.remove(3, 4, 7, 8)
            case "trap" if "trap" not in tribute2Inv:
                choices.remove(4)
            case "knife" if "knife" not in tribute2Inv:
                choices.remove(8)
            case "gun" if "gun" not in tribute2Inv:
                choices.remove(7)

        match (tribute1Inv):
            case "knife" if "knife" in tribute1Inv:
                choices.remove(2)
            case "trap" if "trap" in tribute1Inv:
                choices.remove(9)
            case "gun" if "gun" in tribute1Inv:
                choices.remove(11)

        if tribute1['has_team'] or tribute2['has_team']:
            choices.remove(1)

        if not tribute1['has_team'] and not tribute2['has_team']:
            choices.remove(17)

        if self.checkIfTributesAreInSameTeam(tribute1, tribute2):
            choices.remove(1, 4, 5, 7, 8)
            
        if not teams:
            choices.remove(10)

        return random.choice(choices)


    def pickRandomTribute(self, tribute, tributes):
        aux_tributes = tributes.copy()
        aux_tributes.remove(tribute)
        return random.choice(aux_tributes)
    
    def pickTributeTeam(self, tributes, tribute1, tribute2):
        if not tribute1['has_team'] and not tribute2['has_team']:
            team = randint(1, 100)
            if team not in Counter(tributes['team']):
                tribute1['team'] = team
                tribute2['team'] = team
            else:
                self.pickTributeTeam(tributes, tribute1, tribute2)
    
    @commands.command()
    @pricing()
    async def nuke(self, ctx):
        await Usuario.deleteAll()
        await ctx.send("Database has been nuked.")
              
async def setup(bot):
    await bot.add_cog(TextCommands(bot))