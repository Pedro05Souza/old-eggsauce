from discord.ext import commands
from dataclasses import dataclass
from tools.shared import send_bot_embed, make_embed_object
from tools.chickens.chickenhandlers import EventData
from tools.chickens.chickenshared import verify_events, determine_upkeep_rarity, get_rarity_emoji, rank_determiner
from db.farmDB import Farm
from random import sample, random
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
    "EXTREMELY HIGH": 1600,
    "MAXIMUM": 2160
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

ranks_weight = {
    "BRONZE": 0,
    "SILVER": 250,
    "GOLD": 500,
    "PLATINUM": 750,
    "DIAMOND": 1000,
    "MASTER": 1250,
    "GRANDMASTER": 1500,
    "CHALLENGER": 1750,
    "LEGEND": 2000
}

@dataclass
class UserInQueue():
    member: discord.Member
    chickens: list
    ctx: commands.Context   
    in_event: EventData
    score: int = 0
    chicken_overrall_score: int = 0
    has_opponent: bool = False

    async def define_rank_mmr_weight(self, farm_data):
        self.score += ranks_weight[await rank_determiner(farm_data)]
        if self.score < 0:
            self.score = 0
        return self.score
    
    async def define_chicken_overrall_score(self):
        for chicken in self.chickens:
            self.chicken_overrall_score += rarities_weight[chicken['rarity']]
            self.chicken_overrall_score += upkeep_weight[determine_upkeep_rarity(chicken['upkeep_multiplier'])]
        self.chicken_overrall_score -= farm_size_weights[len(self.chickens)]
        if self.chicken_overrall_score < 0:
            self.chicken_overrall_score = 0
        return self.chicken_overrall_score
    

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
            e = EventData(ctx.author)
            user = UserInQueue(ctx.author, farm_data['chickens'], ctx, e)
            if not user.chickens:
                await send_bot_embed(ctx, description=":no_entry_sign: You need to have chickens to participate in combat.")
                EventData.remove(user.in_event)
                return
            self.user_queue.append(user)
            await user.define_rank_mmr_weight(farm_data)
            await user.define_chicken_overrall_score()
            match_matching_obj = await make_embed_object(description=f"🔍 {ctx.author.name} has joined the queue. Attemping to find balanced matches. Your current chicken overrall is: **{await self.score_string(user.chicken_overrall_score)}**. Your current rank is: **{await rank_determiner(farm_data)}**.")
            match_matching_obj.set_footer(text=f"Having a higher chicken overall will decrease the chances of finding an opponent, but also increase the rewards.")
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
                await user.ctx.send(embed=msg_user)
                await opponent.ctx.send(embed=msg_opponent)
                await self.define_chicken_matchups(user, opponent)
                self.user_queue.remove(user)
                self.user_queue.remove(opponent)
            else:
                if opponent == "opponent":
                    return
                if opponent == "No opponent found.":
                    await send_bot_embed(ctx, description=f":no_entry_sign: {user.member.name}, no opponent has been found. Please try again later.")
                    self.user_queue.remove(user)
                    EventData.remove(e)

    async def user_queue_generator(self, positive_search_rank, negative_search_rank, current_user, positive_search_overrall, negative_search_overrall):
        for user in self.user_queue:
            if user.score >= negative_search_rank and user.score <= positive_search_rank:
                if user.has_opponent:
                    continue
                if user.member.id == current_user.member.id:
                    continue
                if user.chicken_overrall_score >= current_user.chicken_overrall_score - positive_search_overrall and user.chicken_overrall_score <= current_user.chicken_overrall_score + negative_search_overrall:
                    yield user

    async def increase_search_range(self, positive_search, negative_search, current_user, positive_search_overrall, negative_search_overrall): 
        user_list = self.user_queue_generator(positive_search, negative_search, current_user, positive_search_overrall, negative_search_overrall)
        return user_list
    
    async def search(self, current_user):
        attemps = 0
        saved_positive_score, saved_negative_score = current_user.score, current_user.score
        positive_overrall_score, negative_overrall_score = current_user.chicken_overrall_score, current_user.chicken_overrall_score
        while attemps < 20:
            if current_user.has_opponent:
                return "opponent"
            positive_search = saved_positive_score + 30
            negative_search = saved_negative_score - 30
            positive_search_overrall, negative_search_overrall = positive_overrall_score + 50, negative_overrall_score - 50
            if positive_search_overrall < 0:
                positive_search_overrall = 0
            if negative_search < 0:
                negative_search = 0
            if positive_search > 2000:
                positive_search = 2000
            user_list = await self.increase_search_range(positive_search, negative_search, current_user, positive_search_overrall, negative_search_overrall)
            async for user in user_list:
                return user
            attemps += 1
            await asyncio.sleep(1.5)
            saved_negative_score, saved_positive_score = negative_search, positive_search
        return "No opponent found."
    
    async def score_string(self, score):
        for key, value in score_determiner.items():
            if score <= value:
                return key
            
    async def define_chicken_matchups(self, author, user):
        """Define the chicken matchups for the combat."""
        author_chickens = author.chickens
        user_chickens = user.chickens
        author_chickens = sample(author_chickens, len(author_chickens))
        user_chickens = sample(user_chickens, len(user_chickens))
        bench_chickens_author = []
        bench_chickens_user = []
        embed_per_round = await make_embed_object()
        matchups = []
        if len(author_chickens) == len(user_chickens):
            for i in range(0, len(author_chickens)):
                matchups.append([author_chickens[i], user_chickens[i]])
        else:
            if len(author_chickens) > len(user_chickens):
                for i in range(len(user_chickens), len(author_chickens)):
                    bench_chickens_author.append(author_chickens[i])
                author_chickens = author_chickens[:len(user_chickens)]
            else:
                for i in range(len(author_chickens), len(user_chickens)):
                    bench_chickens_user.append(user_chickens[i])
                user_chickens = user_chickens[:len(author_chickens)]
            for i in range(0, len(user_chickens)):
                matchups.append([author_chickens[i], user_chickens[i]])

        print_matchups = [f"**{author.member.name}'s {get_rarity_emoji(match[0]['rarity'])}{match[0]['rarity']} {match[0]['name']}** vs **{user.member.name}'s {get_rarity_emoji(match[1]['rarity'])}{match[1]['rarity']} {match[1]['name']}**" for match in matchups]
        bench_chickens_author_formatted = "\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in bench_chickens_author] if bench_chickens_author else ["No bench chickens."])
        bench_chickens_user_formatted = "\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in bench_chickens_user] if bench_chickens_user else ["No bench chickens."])
        matchups_description = "\n".join(print_matchups)
        embed = await make_embed_object(
            title="🔥 The matchups have been defined.",
            description=f"Here are the matchups:\n{matchups_description}\n\n**Bench Chickens:**\n {author.member.name}:\n{bench_chickens_author_formatted}\n\n{user.member.name}:\n{bench_chickens_user_formatted}"
        )
        await asyncio.sleep(3)
        await self.check_if_same_guild(author, user, embed)
        total_matches = len(matchups)
        accumulator = 0
        for match in matchups:
            accumulator += 1
            await self.matches(user, author, match, accumulator, total_matches, embed_per_round)

    async def matches(self, user, author, match, accumulator, total_matches, embed_per_round):
        """Determines which chickens wins in a match"""
        random_number = random()
        win_rate_for_author = 0.5
        win_rate_for_user = 0.5
        rarity_chicken_author_position = list(rarities_weight.keys()).index(match[0]['rarity'])
        rarity_chicken_user_position = list(rarities_weight.keys()).index(match[1]['rarity'])
        upkeep_chicken_author_position = list(upkeep_weight.keys()).index(determine_upkeep_rarity(match[0]['upkeep_multiplier']))
        upkeep_chicken_user_position = list(upkeep_weight.keys()).index(determine_upkeep_rarity(match[1]['upkeep_multiplier']))
        happy_chicken_author = match[0]['happiness']
        happy_chicken_user = match[1]['happiness']

        if rarity_chicken_author_position > rarity_chicken_user_position:
            difficulty = rarity_chicken_author_position - rarity_chicken_user_position
            win_rate_for_author += 0.2 * difficulty
        else:
            difficulty = rarity_chicken_user_position - rarity_chicken_author_position
            win_rate_for_user += 0.2 * difficulty

        if upkeep_chicken_author_position > upkeep_chicken_user_position:
            difficulty = upkeep_chicken_author_position - upkeep_chicken_user_position
            win_rate_for_author += 0.05 * difficulty

        else:
            difficulty = upkeep_chicken_user_position - upkeep_chicken_author_position
            win_rate_for_user += 0.05 * difficulty
        
        if happy_chicken_author > happy_chicken_user:
            win_rate_for_author += 0.04
        else:
            win_rate_for_user += 0.04

        real_win_rate = win_rate_for_author + win_rate_for_user
        win_rate_for_author = win_rate_for_author / real_win_rate
        win_rate_for_user = win_rate_for_user / real_win_rate

        if random_number < win_rate_for_author:
            embed_per_round.add_field(name=f"Battle:", value=f"🎉 {author.member.name}'s **{get_rarity_emoji(match[0]['rarity'])}{match[0]['rarity']} {match[0]['name']}** has won against {user.member.name}'s **{get_rarity_emoji(match[1]['rarity'])}{match[1]['rarity']} {match[1]['name']}**\n Win chance for {author.member.name}: {round(win_rate_for_author * 100)}%\n Win chance for {user.member.name}: {round(win_rate_for_user * 100)}%", inline=False)
            if match[1] in user.chickens:
                user.chickens.remove(match[1])
        else:
            embed_per_round.add_field(name=f"Battle:", value=f"🎉 {user.member.name}'s **{get_rarity_emoji(match[1]['rarity'])}{match[1]['rarity']} {match[1]['name']}** has won against {author.member.name}'s **{get_rarity_emoji(match[0]['rarity'])}{match[0]['rarity']} {match[0]['name']}**\n Win chance for {author.member.name}: {round(win_rate_for_author * 100)}%\n Win chance for {user.member.name}: {round(win_rate_for_user * 100)}%", inline=False) 
            if match[0] in author.chickens:
                author.chickens.remove(match[0])

        winner = await self.check_winner(author, user)
        if winner:
            loser = author if winner.member.id == user.member.id else user
            await asyncio.sleep(3)
            await self.check_if_same_guild(author, user, embed_per_round)
            await self.rewards(winner, loser)
            EventData.remove(author.in_event)
            EventData.remove(user.in_event)
            return
        else:
            await asyncio.sleep(3)
            if accumulator == total_matches:
                await self.check_if_same_guild(author, user, embed_per_round)
                embed_per_round.clear_fields()
                await asyncio.sleep(3)
                embed_per_round = await make_embed_object(description=f"🔥 The next round will start shortly.")
                await asyncio.sleep(3)
                await self.check_if_same_guild(author, user, embed_per_round)
                await self.define_chicken_matchups(author, user)
    
    async def check_if_same_guild(self, author, user, embed):
        if author.ctx.guild.id == user.ctx.guild.id:
            await author.ctx.send(embed=embed)
        else:
            await author.ctx.send(embed=embed)
            await user.ctx.send(embed=embed)

    async def check_winner(self, author, user):
        if len(author.chickens) == 0:
            return user
        if len(user.chickens) == 0:
            return author
        return
    
    async def rewards(self, winner, loser):
        """Rewards the winner of the combat."""
        farm_data_winner = Farm.read(winner.member.id)
        farm_data_loser = Farm.read(loser.member.id)
        base_mmr_gain = 50
        multiplier = (winner.score + winner.chicken_overrall_score) / (loser.score + loser.chicken_overrall_score)
        mmr_gain = base_mmr_gain * multiplier
        mmr_gain = int(mmr_gain)
        farm_data_winner['mmr'] += mmr_gain
        farm_data_loser['mmr'] -= mmr_gain
        if farm_data_loser['mmr'] < 0:
            farm_data_loser['mmr'] = 0
        Farm.update(winner.member.id, mmr=farm_data_winner['mmr'])
        Farm.update(loser.member.id, mmr=farm_data_loser['mmr'])
        msg = await make_embed_object(description=f"🎉 {winner.member.name} has won the combat and has gained {mmr_gain} MMR, while {loser.member.name} has lost {mmr_gain} MMR.")
        await self.check_if_same_guild(winner, loser, msg)
        return
    
async def setup(bot):
    await bot.add_cog(ChickenCombat(bot))