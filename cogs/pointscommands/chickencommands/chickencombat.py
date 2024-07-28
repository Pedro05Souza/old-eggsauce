from discord.ext import commands
from dataclasses import dataclass
from tools.shared import send_bot_embed, make_embed_object
from tools.chickens.chickenhandlers import EventData
from tools.chickens.chickenshared import verify_events, determine_upkeep_rarity
from db.farmDB import Farm
import asyncio
import discord

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
    "EXTREMELY HIGH": 1600
}

@dataclass
class UserInQueue():
    member: discord.Member
    chickens: list
    score: int = 0
    has_opponent: bool = False

    async def define_score_with_weight(self):
        for chicken in self.chickens:
            self.score += rarities_weight[chicken['rarity']]
            self.score += upkeep_weight[determine_upkeep_rarity(chicken['upkeep_multiplier'])]

class ChickenCombat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_queue = []
        self.map = {}

    @commands.hybrid_command(name="queue", aliases=["fight"], brief="Match making for chicken combat.", description="Match making for chicken combat.", usage="combat")
    async def queue(self, ctx):
        """Match making for chicken combat."""
        farm_data = Farm.read(ctx.author.id)
        if farm_data:
            if await verify_events(ctx, ctx.author):
                return
            if farm_data['farmer'] == 'Warrior Farmer':
                combat_list = []
                iterations = 0
                for chicken in farm_data['chickens']:
                    if chicken['rarity'] != "DEAD":
                        combat_list.append(chicken)
                    iterations += 1
                    if iterations == 8:
                        break
                farm_data['chickens'] = combat_list
            print(len(farm_data['chickens']))
            e = EventData(ctx.author)
            user = UserInQueue(ctx.author, farm_data['chickens'])
            if not user.chickens:
                await send_bot_embed(ctx, description=":no_entry_sign: You need to have chickens to participate in combat.")
                return
            if user in self.user_queue:
                await send_bot_embed(ctx, description=":no_entry_sign: You are already in the queue.")
                return
            self.user_queue.append(user)
            await user.define_score_with_weight()
            match_matching_obj = await make_embed_object(description=f"🔍 {ctx.author.name} has joined the queue. Attemping to find balanced matches. Your current chicken score is: **{await self.score_string(user.score)}**")
            match_matching_obj.set_footer(text=f"Having a higher score will decrease the chances of finding an opponent, but also increase the rewards.")
            await ctx.send(embed=match_matching_obj)
            opponent = await self.search(user)
            if type(opponent) == UserInQueue:
                if str(user.member.id) + "_" + str(opponent.member.id) in self.map:
                    return
                opponent.has_opponent = True
                user.has_opponent = True
                self.map = {str(user.member.id) + "_" + str(opponent.member.id): [user, opponent]}
                msg_user = await make_embed_object(description=f"🔎 {opponent.member.name} has been found as your opponent.")
                msg_opponent = await make_embed_object(description=f"🔎 {user.member.name} has been found as your opponent.")
                await user.member.send(embed=msg_user)
                await opponent.member.send(embed=msg_opponent)
                await send_bot_embed(ctx, description=f"🔥 {user.member.name} has been matched against {opponent.member.name} in a chicken combat. Prepare your chickens!")
                self.user_queue.remove(user)
                self.user_queue.remove(opponent)
            else:
                if opponent == "opponent":
                    EventData.remove(e)
                    return
                if opponent == "No opponent found.":
                    await send_bot_embed(ctx, description=f":no_entry_sign: {user.member.name}, no opponent has been found. Please try again later.")
                    self.user_queue.remove(user)
                    EventData.remove(e)

    async def user_queue_generator(self, positive_search, negative_search):
        for user in self.user_queue:
            if user.score >= negative_search and user.score <= positive_search:
                yield user

    async def increase_search_range(self, positive_search, negative_search): 
        user_list = self.user_queue_generator(positive_search, negative_search)
        return user_list
    
    async def search(self, current_user):
        attemps = 0
        saved_positive_score, saved_negative_score = current_user.score, current_user.score
        while attemps < 20:
            if current_user.has_opponent:
                return "opponent"
            positive_search = saved_positive_score + 20
            negative_search = saved_negative_score - 20
            if negative_search < 0:
                negative_search = 0
            user_list = await self.increase_search_range(positive_search, negative_search)
            async for user in user_list:
                if user.member.id != current_user.member.id:
                    return user
            attemps += 1
            await asyncio.sleep(1.5)
            saved_negative_score, saved_positive_score = negative_search, positive_search
        return "No opponent found."
    

    async def score_string(self, score):
        for key, value in score_determiner.items():
            if score <= value:
                return key
    
        

async def setup(bot):
    await bot.add_cog(ChickenCombat(bot))