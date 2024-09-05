"""
This file contains the chicken combat system for the bot.
"""

from discord.ext import commands
from dataclasses import dataclass
from tools.pointscore import pricing
from tools.shared import send_bot_embed, make_embed_object, confirmation_embed, user_cache_retriever
from tools.settings import queue_command_cooldown
from tools.chickens.combatbot import BotMatchMaking, bot_maker
from tools.chickens.chickenhandlers import EventData
from tools.chickens.chickenshared import verify_events, determine_upkeep_rarity, get_rarity_emoji, rank_determiner, define_chicken_overrall_score, create_chicken, get_max_chicken_limit
from tools.settings import max_bench
from tools.chickens.chickeninfo import rarities_weight, upkeep_weight, score_determiner, chicken_ranking
from db.farmDB import Farm
from db.userDB import User
from tools.tips import tips
from random import random, randint
from discord.ext.commands import Context
from typing import Union, Dict, List
import asyncio
import discord

@dataclass
class UserInQueue():
    member: discord.Member
    chickens: list
    ctx: commands.Context   
    in_event: EventData
    score: int
    chicken_overrall_score: int = 0
    has_opponent: bool = False
    
class ChickenCombat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_queue: Dict[int, List[UserInQueue]] = {}

    @commands.hybrid_command(name="eggleague", aliases=["eleague", "fight", "battle", "queue"], brief="Match making for chicken combat.", description="Match making for chicken combat.", usage="combat")
    @commands.cooldown(1, queue_command_cooldown, commands.BucketType.user)
    @pricing()
    async def queue(self, ctx: Context) -> None:
        """
        Match making function for chicken combat.
        param: ctx: commands.Context
        """
        farm_data = ctx.data["farm_data"]
        if await verify_events(ctx, ctx.author):
            return
        author_chickens = await self.define_eight_chickens_for_match(farm_data['chickens'])
        e = EventData(ctx.author)
        user = UserInQueue(ctx.author, author_chickens, ctx, e, farm_data['mmr'])
        if not user.chickens:
            await send_bot_embed(ctx, description=":no_entry_sign: You need to have chickens to participate in combat.")
            EventData.remove(user.in_event)
            return
        await self.add_user_in_queue(user)
        user.chicken_overrall_score = await define_chicken_overrall_score(user.chickens)
        match_matching_obj = await make_embed_object(description=f"🔍 {ctx.author.name} has joined the queue. Attemping to find balanced matches. Your current chicken overrall is: **{await self.score_string(user.chicken_overrall_score)}**. Your current rank is: **{await rank_determiner(farm_data['mmr'])}**.")
        match_matching_obj.set_footer(text=tips[randint(0, len(tips) - 1)])
        author_msg, user_msg = await self.check_if_same_guild(user, user, match_matching_obj)
        opponent = await self.search(user)
        await self.combat_handler(user, opponent, user_msg, author_msg, ctx, e)

    async def add_user_in_queue(self, user: UserInQueue):
        """
        Adds a user in the queue.
        """
        set_scores = [i for i in range(0, 2100, 100)]
        for score in reversed(set_scores):
            if user.score >= score:
                if score not in self.user_queue:
                    self.user_queue[score] = []
                self.user_queue[score].append(user)
                break

    async def retrieve_user_key(self, user: UserInQueue) -> int:
        """
        Retrieve the user key.
        """
        set_scores = [i for i in range(0, 2100, 100)]
        for score in reversed(set_scores):
            if user.score >= score:
                return score

    async def combat_handler(self, user: UserInQueue, opponent: Union[UserInQueue, str], user_msg: discord.Message, author_msg: discord.Message, ctx: Context, e: EventData) -> None:
        """
        Handles the combat between the two users.
        param: user: UserInQueue
        param: opponent: Union[UserInQueue, str]
        param: user_msg: discord.Message
        param: author_msg: discord.Message
        param: ctx: commands.Context
        param: e: EventData
        """
        if isinstance(opponent, (UserInQueue, BotMatchMaking)):
            opponent_mmr = 0
            if not await self.check_if_user_is_bot(opponent):
                opponent_data = Farm.read(opponent.member.id)
                opponent_mmr = opponent_data['mmr']
            else:
                opponent_mmr = opponent.score
            msg_user = await make_embed_object(description=f"🔎 **{user.member.name}**, **{await self.check_user_name(opponent)}** has been found as your opponent. **({opponent_mmr} MMR)**")
            msg_opponent = await make_embed_object(description=f"🔎 **{await self.check_user_name(opponent)}**, **{user.member.name}** has been found as your opponent. **({user.score} MMR)**")
            await user.ctx.send(embed=msg_user)
            if not await self.check_if_user_is_bot(opponent):
                await opponent.ctx.send(embed=msg_opponent)
                user_msg = author_msg
            await asyncio.sleep(3)
            author_msg, user_msg = await self.check_if_same_guild(user, opponent, await make_embed_object(description=f"🔥 The match will begin soon."))
            await asyncio.sleep(3)
            await self.send_battle_decks(user, opponent, author_msg, user_msg)
            await asyncio.sleep(await self.dynamic_match_cooldown(user.chickens, opponent.chickens))
            await self.define_chicken_matchups(user, opponent, "ranked", user_msg, author_msg, [], [])
        elif opponent == "opponent":
            return 
        elif opponent == "No opponent found.":
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.member.name}, no opponent has been found. Please try again later.")
            self.user_queue.remove(user)
            EventData.remove(e)
            self.queue.reset_cooldown(ctx)
            return
            
    async def return_user_id(self, user: Union[UserInQueue, BotMatchMaking]) -> int:
        """
        Return the user id of the user.
        param: user: UserInQueue
        return: int
        """
        if isinstance(user, UserInQueue):
            return user.member.id
        else:
            return user.bot_id
                    
    async def increase_search_range(self, positive_search: int, negative_search: int, current_user: UserInQueue) -> Union[UserInQueue, None]:
        """
        Increase the search range for the user queue.
        param: positive_search: int
        param: negative_search: int
        param: current_user: UserInQueue
        return: Generator
        """
        for i in range(negative_search, positive_search):
            if i in self.user_queue.keys():
                for user in self.user_queue[i]:
                    if user.member.id != current_user.member.id:
                        self.user_queue[i].remove(user)
                        return user
        return None
    
    async def send_battle_decks(self, user: UserInQueue, opponent: UserInQueue, author_msg: discord.Message, user_msg: discord.Message) -> None:
        """
        Sends the battle decks to the users.
        param: user: UserInQueue
        param: opponent: UserInQueue
        param: author_msg: discord.Message
        param: user_msg: discord.Message
        """
        opponent_deck = opponent.chickens
        author_deck = user.chickens
        both_deck = await make_embed_object(title=":crossed_swords: Battle decks:")
        both_deck.add_field(name=f"{user.member.name}'s deck:", value= f"\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in author_deck]), inline=False)
        both_deck.add_field(name=f"{await self.check_user_name(opponent)}'s deck:", value= f"\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in opponent_deck]), inline=False)
        await self.check_if_same_guild_edit(user, opponent, user_msg, author_msg, both_deck)
    
    async def search(self, current_user: UserInQueue) -> Union[UserInQueue, BotMatchMaking, str]:
        """
        Search for an opponent for the user.
        param: current_user: UserInQueue
        return: Union[UserInQueue, BotMatchMaking, str]
        """
        attemps = 0
        saved_positive_score, saved_negative_score = current_user.score, current_user.score
        while attemps != 25:
            if current_user.has_opponent:
                return "opponent"
            if attemps == 24:
                bot = await bot_maker(current_user.score)
                current_user.has_opponent = True
                self.user_queue[await self.retrieve_user_key(current_user)].remove(current_user)
                return bot   
            positive_search = saved_positive_score + 5
            negative_search = saved_negative_score - 5
            if negative_search < 0:
                negative_search = 0
            opponent_found = await self.increase_search_range(positive_search, negative_search, current_user)
            if opponent_found:
                current_user.has_opponent = True
                opponent_found.has_opponent = True
                self.user_queue[await self.retrieve_user_key(current_user)].remove(current_user)
                return opponent_found
            attemps += 1
            await asyncio.sleep(1)
            saved_negative_score, saved_positive_score = negative_search, positive_search
        return "No opponent found."
    
    async def define_chicken_matchups(self, author: UserInQueue, user: Union[UserInQueue, BotMatchMaking], match_type: str, user_msg: discord.Message, author_msg: discord.Message, dead_chickens_author: list, dead_chickens_user: list) -> None:
        """
        Define the chicken matchups for the combat.
        param: author: UserInQueue
        param: user: UserInQueue
        param: match_type: str
        param: user_msg: discord.Message
        param: author_msg: discord.Message
        param: dead_chickens_author: list
        param: dead_chickens_user: list
        """
        author_chickens = author.chickens
        user_chickens = user.chickens
        bench_chickens_author = []
        bench_chickens_user = []
        matchups = []
        matchups, bench_chickens_author, bench_chickens_user = await self.define_bench_chickens(author_chickens, user_chickens, matchups, bench_chickens_author, bench_chickens_user)
        print_matchups = [f"**{author.member.name}'s {get_rarity_emoji(match[0]['rarity'])}{match[0]['rarity']} {match[0]['name']}** vs **{await self.check_user_name(user)}'s {get_rarity_emoji(match[1]['rarity'])}{match[1]['rarity']} {match[1]['name']}**" for match in matchups]
        bench_chickens_author_formatted = "\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in bench_chickens_author] if bench_chickens_author else ["No bench chickens."])
        bench_chickens_user_formatted = "\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in bench_chickens_user] if bench_chickens_user else ["No bench chickens."])
        matchups_description = "\n".join(print_matchups)
        embed_per_round = await make_embed_object(
            title="🔥 The matchups have been defined.",
            description=f"Here are the matchups:\n{matchups_description}\n\n**Bench Chickens:**\n {author.member.name}:\n{bench_chickens_author_formatted}\n\n{await self.check_user_name(user)}:\n{bench_chickens_user_formatted}"
        )
        total_matches = len(matchups)
        await self.check_if_same_guild_edit(author, user, user_msg, author_msg, embed_per_round)
        await asyncio.sleep(await self.dynamic_match_cooldown(author.chickens, user.chickens))
        embed_per_round.title = ":crossed_swords: Match Results:"
        embed_per_round.description = ""
        accumulator = 0
        for match in matchups:
            accumulator += 1
            await self.matches(user, author, match, accumulator, total_matches, embed_per_round, match_type, user_msg, author_msg, dead_chickens_author, dead_chickens_user)

    async def matches(self, user: Union[UserInQueue, BotMatchMaking], author: UserInQueue, match: list, accumulator: int, total_matches: int, embed_per_round: discord.Embed, match_type: str, user_msg: discord.Message, author_msg: discord.Message, dead_chickens_author: list, dead_chickens_user: list) -> None:
        """
        Determines which chickens wins in a match.
        param: user: Union[UserInQueue, BotMatchMaking]
        param: author: UserInQueue
        param: match: list
        param: accumulator: int
        param: total_matches: int
        param: embed_per_round: discord.Embed
        param: match_type: str
        param: user_msg: discord.Message
        param: author_msg: discord.Message
        param: dead_chickens_author: list
        param: dead_chickens_user: list
        """
        random_number = random()
        user_name = await self.check_user_name(user)
        win_rate_for_author, win_rate_for_user = await self.define_win_rate(match[0], match[1])
        await self.update_match_result(author, user, match, win_rate_for_author, win_rate_for_user, embed_per_round, dead_chickens_author, dead_chickens_user, random_number, user_name)

        winner = await self.check_winner(author, user)
        if winner:
            await self.handle_winner(author, user, winner, user_msg, author_msg, embed_per_round, dead_chickens_author, dead_chickens_user, match_type, user_name)
        else:
            await self.handle_no_winner(author, user, user_msg, author_msg, embed_per_round, dead_chickens_author, dead_chickens_user, match_type, total_matches, accumulator, user_name)

    async def handle_winner(self, author: UserInQueue, user: Union[UserInQueue, BotMatchMaking], winner: Union[UserInQueue, BotMatchMaking], user_msg: discord.Message, author_msg: discord.Message, embed_per_round: discord.Embed, dead_chickens_author: list, dead_chickens_user: list, match_type: str, user_name: str) -> None:
        loser = author if winner == user else user
        EventData.remove(author.in_event)
        if not await self.check_if_user_is_bot(user):
            EventData.remove(user.in_event)
        if dead_chickens_author:
            embed_per_round.add_field(name=f"{author.member.name}'s Dead Chickens:", value="\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in dead_chickens_author]), inline=False)
        if dead_chickens_user:
            embed_per_round.add_field(name=f"{user_name}'s Dead Chickens:", value="\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in dead_chickens_user]), inline=False)
        await self.check_if_same_guild_edit(author, user, user_msg, author_msg, embed_per_round)
        await asyncio.sleep(await self.dynamic_match_cooldown(author.chickens, user.chickens))
        await self.rewards(winner, loser, author.ctx, match_type, embed_per_round, user_msg, author_msg)
    
    async def handle_no_winner(self, author: UserInQueue, user: Union[UserInQueue, BotMatchMaking], user_msg: discord.Message, author_msg: discord.Message, embed_per_round: discord.Embed, dead_chickens_author: list, dead_chickens_user: list, match_type: str, total_matches: int, accumulator: int, user_name: str) -> None:
        if accumulator == total_matches:
            if dead_chickens_author:
                embed_per_round.add_field(name=f"{author.member.name}'s Dead Chickens:", value="\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in dead_chickens_author]), inline=False)
            if dead_chickens_user:
                embed_per_round.add_field(name=f"{user_name}'s Dead Chickens:", value="\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in dead_chickens_user]), inline=False)
            await self.check_if_same_guild_edit(author, user, user_msg, author_msg, embed_per_round)
            embed_per_round.clear_fields()
            await asyncio.sleep(await self.dynamic_match_cooldown(author.chickens, user.chickens))
            embed_per_round.title = "🔥 The next round will begin soon."
            embed_per_round.description = ""
            await self.check_if_same_guild_edit(author, user, user_msg, author_msg, embed_per_round)
            await asyncio.sleep(5)
            embed_per_round.clear_fields()
            await self.define_chicken_matchups(author, user, match_type, user_msg, author_msg, dead_chickens_author, dead_chickens_user)
    
    async def update_match_result(self, author: UserInQueue, user: Union[UserInQueue, BotMatchMaking], match: list, win_rate_for_author : float, win_rate_for_user: float, embed_per_round: discord.Embed, dead_chickens_author: list, dead_chickens_user: list, random_number: float, user_name: str) -> None:
        if random_number < win_rate_for_author:
            embed_per_round.add_field(name=f"Battle:", value=f"🎉 {author.member.name}'s **{get_rarity_emoji(match[0]['rarity'])}{match[0]['rarity']} {match[0]['name']} ({round(win_rate_for_author * 100)}%)** has won against {user_name}'s **{get_rarity_emoji(match[1]['rarity'])}{match[1]['rarity']} {match[1]['name']} ({round(win_rate_for_user * 100)}%)**\n", inline=False)
            if match[1] in user.chickens:
                user.chickens.remove(match[1])
                dead_chickens_user.append(match[1])
        else:
            embed_per_round.add_field(name=f"Battle:", value=f"🎉 {user_name}'s **{get_rarity_emoji(match[1]['rarity'])}{match[1]['rarity']} {match[1]['name']} ({round(win_rate_for_user * 100)}%)** has won against {author.member.name}'s **{get_rarity_emoji(match[0]['rarity'])}{match[0]['rarity']} {match[0]['name']} ({round(win_rate_for_author * 100)}%)**\n", inline=False) 
            if match[0] in author.chickens:
                author.chickens.remove(match[0])
                dead_chickens_author.append(match[0])

    async def define_win_rate(self, chicken1: dict, chicken2: dict) -> tuple:
        win_rate_for_author = 0.5
        win_rate_for_user = 0.5
        rarity_chicken_author_position = list(rarities_weight.keys()).index(chicken1['rarity'])
        rarity_chicken_user_position = list(rarities_weight.keys()).index(chicken2['rarity'])
        upkeep_chicken_author_position = list(upkeep_weight.keys()).index(determine_upkeep_rarity(chicken1['upkeep_multiplier']))
        upkeep_chicken_user_position = list(upkeep_weight.keys()).index(determine_upkeep_rarity(chicken2['upkeep_multiplier']))
        happy_chicken_author = chicken1['happiness']
        happy_chicken_user = chicken2['happiness']

        if rarity_chicken_author_position > rarity_chicken_user_position:
            difficulty = rarity_chicken_author_position - rarity_chicken_user_position
            win_rate_for_author += 0.45 * difficulty
        else:
            difficulty = rarity_chicken_user_position - rarity_chicken_author_position
            win_rate_for_user += 0.45 * difficulty

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
        return win_rate_for_author, win_rate_for_user
    
    async def define_bench_chickens(self, author_chickens: list, user_chickens: list, matchups: list, bench_chickens_author: list, bench_chickens_user: list) -> tuple:
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
        return matchups, bench_chickens_author, bench_chickens_user

    
    async def check_if_same_guild(self, author: Union[UserInQueue, BotMatchMaking], user: Union[UserInQueue, BotMatchMaking], embed: discord.Embed) -> tuple:
        if await self.check_if_user_is_bot(user):
            author_msg = await author.ctx.send(embed=embed)
            user_msg = author_msg
            return author_msg, user_msg
        elif await self.check_if_user_is_bot(author):
            user_msg = await user.ctx.send(embed=embed)
            author_msg = user_msg
            return user_msg, author_msg
        if author.ctx.guild.id == user.ctx.guild.id:
            author_msg = await author.ctx.send(embed=embed)
            user_msg = author_msg
            return author_msg, user_msg
        else:
            author_msg = await author.ctx.send(embed=embed)
            user_msg = await user.ctx.send(embed=embed)
            return author_msg, user_msg
        
    async def check_if_same_guild_edit(self, author: Union[UserInQueue, BotMatchMaking], user: Union[UserInQueue, BotMatchMaking], user_msg: discord.Message, author_msg: discord.Message, embed: discord.Embed) -> None:
        if await self.check_if_user_is_bot(user):
            await author_msg.edit(embed=embed)
            return
        elif await self.check_if_user_is_bot(author):
            await user_msg.edit(embed=embed)
            return
        elif author.ctx.guild.id == user.ctx.guild.id:
            await author_msg.edit(embed=embed)
            return
        else:
            await author_msg.edit(embed=embed)
            await user_msg.edit(embed=embed)
            return

    async def check_if_user_is_bot(self, user: Union[UserInQueue, BotMatchMaking]) -> bool:
        if isinstance(user, BotMatchMaking):
            return True
        return False
        
    async def check_user_name(self, user: Union[UserInQueue, BotMatchMaking]) -> str:
        if await self.check_if_user_is_bot(user):
            return user.name
        return user.member.name

    async def check_winner(self, author: UserInQueue, user: Union[UserInQueue, BotMatchMaking]) -> Union[UserInQueue, BotMatchMaking, None]:
        if len(author.chickens) == 0:
            return user
        if len(user.chickens) == 0:
            return author
        return None
    
    async def check_user_score(self, user: Union[UserInQueue, BotMatchMaking]) -> list:
        if not await self.check_if_user_is_bot(user):
            farm_data = Farm.read(user.member.id)
            return [farm_data['mmr'], farm_data['highest_mmr'], farm_data['wins'], farm_data['losses']]
        return [user.score, 0, 0, 0]

    async def rewards(self, winner: Union[BotMatchMaking, UserInQueue], loser: Union[UserInQueue, BotMatchMaking], ctx: Context, match_type: int, embed_per_round: discord.Embed, winner_msg: discord.Message, loser_msg: discord.Message) -> None:
        """Rewards the winner of the combat.""" 
        if match_type == "ranked":
            farm_data_winner = await self.check_user_score(winner)
            farm_data_loser = await self.check_user_score(loser)
            base_mmr_gain = 28
            multiplier = (loser.score + loser.chicken_overrall_score) / (winner.score + winner.chicken_overrall_score)
            mmr_diff = farm_data_loser[0] - farm_data_winner[0]
            multiplier = 1 + abs(mmr_diff / 1000)
            mmr_gain = base_mmr_gain * multiplier
            mmr_gain = int(mmr_gain)
            mmr_gain = max(base_mmr_gain, mmr_gain)
            score = mmr_gain
            farm_data_loser[0] -= mmr_gain
            if farm_data_loser[0] < 0:
                farm_data_loser[0] = 0
            await self.verify_if_upwards_rank(ctx, farm_data_winner[0], farm_data_winner[0] + score, winner, farm_data_winner[1])
            farm_data_winner[0] += mmr_gain
            if not await self.check_if_user_is_bot(winner):
                increment_wins = farm_data_winner[2] + 1
                Farm.update(winner.member.id, mmr=farm_data_winner[0], wins=increment_wins)
            if not await self.check_if_user_is_bot(loser):
                increment_losses = farm_data_loser[3] + 1
                Farm.update(loser.member.id, mmr=farm_data_loser[0], losses=increment_losses)
            msg = await make_embed_object(description=f"🎉 **{await self.check_user_name(winner)}** has won the combat and has gained **{mmr_gain}** MMR, while **{await self.check_user_name(loser)}** has lost the same amount.")
            embed_per_round = msg
            await self.check_if_same_guild_edit(winner, loser, winner_msg, loser_msg, embed_per_round)
            return
        elif match_type == "friendly":
            await send_bot_embed(ctx, description=f"🎉 **{await self.check_user_name(winner)}** has won the combat.")
            EventData.remove(winner.in_event)
            EventData.remove(loser.in_event)

    async def verify_if_upwards_rank(self, ctx: Context, before_mmr: int, after_mmr: int, winner: Union[UserInQueue, BotMatchMaking], highest_mmr: int) -> None:
        """Sends a notification if the user has uppwarded in rank."""
        before_rank = await rank_determiner(before_mmr)
        after_rank = await rank_determiner(after_mmr)
        if before_rank != after_rank:
            await send_bot_embed(ctx, description=f"🎉 **{await self.check_user_name(winner)}** has been promoted to **{after_rank}**.")    
        if not await self.check_if_user_is_bot(winner):
            if after_mmr > highest_mmr:
                await self.rank_rewards(ctx, after_mmr, highest_mmr, winner)
                Farm.update(winner.member.id, highest_mmr=after_mmr)
        return
        
    async def score_string(self, score: int) -> str:
        for key, value in reversed(score_determiner.items()):
            if score >= value:
                return key
            
    async def rank_rewards(self, ctx: Context, mmr: int, highest_mmr: int, winner: Union[UserInQueue, BotMatchMaking]) -> None:
        """Determines the rewards for the rank."""
        current_rank = await rank_determiner(mmr)
        highest_rank = await rank_determiner(highest_mmr)
        farm_data = await user_cache_retriever(winner.member.id)
        farm_data = farm_data["farm_data"]
        user_data = await user_cache_retriever(winner.member.id)
        user_data = user_data["user_data"]
        if chicken_ranking[current_rank] > chicken_ranking[highest_rank]:
            chicken_rewarded, points_gained = await self.rewards_per_rank(chicken_ranking[current_rank])
            chicken_rewarded = await create_chicken(chicken_rewarded, "rewards")
            msg = await make_embed_object(title=f"🎉 {winner.member.name}'s rank rewards", description=f"You've managed to upgrade your rank, here are the following rewards:\n\n :money_with_wings: **{points_gained}** eggbux.")
            User.update_points(winner.member.id, user_data['points'] + points_gained)
            if len(farm_data['chickens']) >= get_max_chicken_limit(farm_data) and len(farm_data['bench'] )>= max_bench:
                msg.description += f"\n\n:warning: You've reached the maximum amount of chickens in your farm. The **{get_rarity_emoji(chicken_rewarded['rarity'])}** **{chicken_rewarded['rarity']}** **{chicken_rewarded['name']}** has been added to the reedemable rewards. Type **redeemables** to claim it."
                farm_data['redeemables'].append(chicken_rewarded)
                Farm.update(winner.member.id, redeemables=farm_data['redeemables'])

            elif len(farm_data['chickens']) >= get_max_chicken_limit(farm_data):
                msg.description += f"\n\n:warning: You've reached the maximum amount of chickens in your farm. The **{get_rarity_emoji(chicken_rewarded['rarity'])}** **{chicken_rewarded['rarity']}** **{chicken_rewarded['name']}** has been added to the bench."
                farm_data['bench'].append(chicken_rewarded)
                Farm.update(winner.member.id, bench=farm_data['bench'])

            else:
                farm_data['chickens'].append(chicken_rewarded)
                msg.description += f"\n\n:chicken: **{get_rarity_emoji(chicken_rewarded['rarity'])}** **{chicken_rewarded['rarity']}** **{chicken_rewarded['name']}** has been added to your farm."
                Farm.update(winner.member.id, chickens=farm_data['chickens'])
            await ctx.send(embed=msg)
            return
            
    async def rewards_per_rank(self, rank: int) -> tuple:
        rank_list = list(chicken_ranking.values())
        chicken_list = list(rarities_weight.keys())
        rank_dictionary = zip(rank_list[1:], chicken_list[9:])
        rank_dictionary = dict(rank_dictionary)
        points_gained = rank * 6
        for key in rank_list:
            if rank == key:
                return rank_dictionary[key], points_gained
    
    @commands.hybrid_command(name="friendly", brief="Friendly combat with another user.", description="Friendly combat with another user.", usage="friendly @user")
    @commands.cooldown(1, queue_command_cooldown, commands.BucketType.user)
    @pricing()
    async def friendly_combat(self, ctx: Context, user: discord.Member) -> None:
        """Friendly combat with another user."""
        if user.id == ctx.author.id:
            await send_bot_embed(ctx, description=":no_entry_sign: You can't combat yourself.")
            return
        farm_data = ctx.data["farm_data"]
        user_data = await user_cache_retriever(user.id)
        user_data = user_data["farm_data"]
        if await verify_events(ctx, ctx.author) or await verify_events(ctx, user):
            return
        if user_data:
            e = EventData(ctx.author)
            e2 = EventData(user)
            confirmation = await confirmation_embed(ctx, user, f"{user.name}, do you accept the friendly combat request from {ctx.author.name}?")
            if confirmation:
                temp_farm_data_author = farm_data['chickens']
                temp_farm_data_user = user_data['chickens']
                temp_farm_data_author = await self.define_eight_chickens_for_match(farm_data['chickens'])
                temp_farm_data_user = await self.define_eight_chickens_for_match(user_data['chickens'])
                author = UserInQueue(ctx.author, temp_farm_data_author, ctx, e, farm_data['mmr'])
                user = UserInQueue(user, temp_farm_data_user, ctx, e2, user_data['mmr'])
                author.chicken_overrall_score = await define_chicken_overrall_score(author.chickens)
                user.chicken_overrall_score = await define_chicken_overrall_score(user.chickens)
                author_msg, user_msg = await self.check_if_same_guild(author, user, await make_embed_object(description=f"🔥 The match will begin soon."))
                await asyncio.sleep(3.5)
                await self.define_chicken_matchups(author, user, "friendly", user_msg, author_msg, [], [])
            else:
                await send_bot_embed(ctx, description=":no_entry_sign: The user has not responded or declined the friendly combat request.")
                EventData.remove(e)
                EventData.remove(e2)
                self.friendly_combat.reset_cooldown(ctx)
                return
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: one of the users does not have a farm.")
            return
        
    async def define_eight_chickens_for_match(self, chickens : list) -> list:
        """Defines the eight chickens for the match."""
        combat_list = []
        iterations = 0
        for chicken in chickens:
            if chicken['rarity'] != "DEAD":
                combat_list.append(chicken)
            iterations += 1
            if iterations == 8:
                break
        return combat_list

    async def dynamic_match_cooldown(self, author_chickens: list, user_chickens: list) -> int:
        """Determines the cooldown for the match based on the amount of chickens."""
        mean = (len(author_chickens) + len(user_chickens)) / 2
        return mean * 2
    
async def setup(bot):
    await bot.add_cog(ChickenCombat(bot))