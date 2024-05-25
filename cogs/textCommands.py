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
        end_time = time.time() + 10
        players = []
        round_count = 1
        await ctx.send("The Hunger Games have begun, may the odds be in your favor. Type !join to participate. You have 20 seconds to join.")
        while True:
            timeout = end_time - time.time()
            if timeout <= 0: 
                break
            try:
                message = await asyncio.wait_for(self.bot.wait_for("message", check=lambda message: message.content == "!join"), timeout=timeout)
                if not any(player['player'] == message.author for player in players):
                    players.append({"player" : message.author, "inventory" : [], "team" : 0, "has_team" : False, "is_alive" : True})
                    # players.append({"player" : discord.utils.get(ctx.guild.members, id=391289130438623233), "inventory" : [], "team" : 0, "has_team" : False, "is_alive" : True})
                    # players.append({"player" : discord.utils.get(ctx.guild.members, id=254931754941415424), "inventory" : [], "team" : 0, "has_team" : False, "is_alive" : True})
                    # players.append({"player" : discord.utils.get(ctx.guild.members, id=270364294959333376), "inventory" : [], "team" : 0, "has_team" : False, "is_alive" : True})
                    # players.append({"player" : discord.utils.get(ctx.guild.members, id=303309575166099457), "inventory" : [], "team" : 0, "has_team" : False, "is_alive" : True})
                    # players.append({"player" : discord.utils.get(ctx.guild.members, id=322465483502780417), "inventory" : [], "team" : 0, "has_team" : False, "is_alive" : True})
                    await ctx.send(f"{message.author.display_name} has joined the Hunger Games.")
                else:
                    await ctx.send(f"{message.author.display_name} is already in the Hunger Games.")
            except asyncio.TimeoutError:
                break

        if len(players) < 2:
            await ctx.send("Not enough players to begin the Hunger Games.")
            return
        
        await ctx.send("The Hunger Games have begun.")
        while sum(player['is_alive'] for player in players) > 1:
            await ctx.send(f"Round {round_count} has offically started.")
            events = await self.events()
            for player in players:
                if player['is_alive']:
                    await asyncio.sleep(2)
                    print(player)
                    players = await self.eventActions(ctx, events, player, players)
            round_count += 1
        print("ballsack")
        #winner = (player['player'] for player in players if player['is_alive'])
        #await ctx.send(f"{winner.display_name} has won the Hunger Games winning 250 eggbux.")
        #Usuario.update(winner['player'], Usuario.read(winner['player']['points']) + 250, Usuario.read(winner['player'].id)['roles'])
            
    async def events(self):
        events = {
        0: " has been killed by a bear.",
        1: " has teamed up with",
        2: " has found a weapon.",
        3: " has found a medkit.",
        4: " has been killed by a trap set by",
        5: " was spotted hiding and was killed by",
        6: " narrowly escaped an attack from ",
        7: " has found food.",
        8: " has found a shelter.",
        9: " has found a trap.",
        10: "has been killed by team "
        }
        return events
    
    async def eventActions(self, ctx, events, player, players: list):
        if not player['is_alive']:
            return players
        for player in players:
            if player['is_alive']:
                print("balls", len(players))
                player1 = player
                player2 = random.choice(players)
                while player1 == player2:
                    player2 = random.choice(players)
                event_keys = list(events.keys())
                random_event = random.choice(event_keys)
        match (random_event):
            case 0:
                player1['is_alive'] = False
                await ctx.send(f"{player1['player'].display_name} {events[0]}")
            case 1:
                if not (player1['has_team']) and not (player2['has_team']):
                    player_team = randint(1, 100)
                    await ctx.send(f"{player1['player'].display_name} {events[1]} {player2['player'].display_name}, creating the team {player_team}.")
                    player1['team'] = player_team
                    player2['team'] = player_team 
                    player1['has_team'] = True
                    player2['has_team'] = True    
            case 2: 
                await ctx.send(f"{player1['player'].display_name} {events[2]}")
                player1['inventory'].append("weapon")
            case 3:
                await ctx.send(f"{player1['player'].display_name} {events[3]}")
                player1['inventory'].append("medkit") 
            case 4:
                if player1['is_alive'] and player2['is_alive'] and self.isPlayerInSameTeam(player1, player2) >= 70:
                    await ctx.send(f"{player1['player'].d} was betrayed by {player2['player'].display_name} and was killed.")
                    return 
                player1['is_alive'] = False
                await ctx.send(f"{player1['player'].display_name} {events[4]} {player2['player'].display_name}")
            case 5:
                player1['is_alive'] = False
                await ctx.send(f"{player1['player'].display_name} {events[5]} {player2['player'].display_name}")
            case 6:
                await ctx.send(f"{player1['player'].display_name} {events[6]} {player2['player'].display_name}.")
            case 7:
                await ctx.send(f"{player1['player'].display_name} {events[7]}")
            case 8:
                await ctx.send(f"{player1['player'].display_name} {events[8]}") 
            case 9:
                await ctx.send(f"{player1['player'].display_name} {events[9]}")
                player1['inventory'].append("trap")
            case 10:
                team_count = Counter(player['team'] for player in players if player['team'] != 0)
                if len(team_count) < 1:
                    players = await self.eventActions(ctx, events, player, players)
                else:
                    most_common_team = team_count.most_common(1)
                    await ctx.send(f"{player1['player'].display_name} {events[10]} {most_common_team[0]}")
                    player1['is_alive'] = False
                    
        return players

    def chooseRandomEventAction(self, ctx, player1, player2, events):
    
    def isPlayerInSameTeam(self, player1, player2) -> int:
        betrayalChance = randint(1, 100)
        if (player1['team'] is player2['team']) and player1['has_team'] and player2['has_team']:
            return betrayalChance
        return 0
    
    @commands.command()
    @pricing()
    async def nuke(self, ctx):
        await Usuario.deleteAll()
        await ctx.send("Database has been nuked.")
              
async def setup(bot):
    await bot.add_cog(TextCommands(bot))