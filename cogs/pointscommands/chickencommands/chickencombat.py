from discord.ext import commands
from dataclasses import dataclass
from tools.pointscore import pricing
from tools.shared import send_bot_embed, make_embed_object, queue_command_cooldown, confirmation_embed
from tools.chickens.combatbot import BotMatchMaking, bot_maker
from tools.chickens.chickenhandlers import EventData
from tools.chickens.chickenshared import verify_events, determine_upkeep_rarity, get_rarity_emoji, rank_determiner, define_chicken_overrall_score, create_chicken, get_max_chicken_limit, max_bench
from tools.chickens.chickeninfo import rarities_weight, upkeep_weight, score_determiner, chicken_ranking
from db.farmDB import Farm
from db.userDB import User
from tools.tips import tips
from random import sample, random, randint
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
        self.user_queue = []
        self.map = {}

    @commands.hybrid_command(name="eggleague", aliases=["eleague", "fight", "battle", "queue"], brief="Match making for chicken combat.", description="Match making for chicken combat.", usage="combat")
    @commands.cooldown(1, queue_command_cooldown, commands.BucketType.user)
    @pricing()
    async def queue(self, ctx):
        """Match making for chicken combat."""
        farm_data = Farm.read(ctx.author.id)
        if farm_data:
            if await verify_events(ctx, ctx.author):
                return
            farm_data['chickens'] = await self.define_eight_chickens_for_match(farm_data['chickens'])
            e = EventData(ctx.author)
            user = UserInQueue(ctx.author, farm_data['chickens'], ctx, e, farm_data['mmr'])
            if not user.chickens:
                await send_bot_embed(ctx, description=":no_entry_sign: You need to have chickens to participate in combat.")
                EventData.remove(user.in_event)
                return
            self.user_queue.append(user)
            user.chicken_overrall_score = await define_chicken_overrall_score(user.chickens)
            match_matching_obj = await make_embed_object(description=f"🔍 {ctx.author.name} has joined the queue. Attemping to find balanced matches. Your current chicken overrall is: **{await self.score_string(user.chicken_overrall_score)}**. Your current rank is: **{await rank_determiner(farm_data['mmr'])}**.")
            match_matching_obj.set_footer(text=tips[randint(0, len(tips) - 1)])
            author_msg, user_msg = await self.check_if_same_guild(user, user, match_matching_obj)
            opponent = await self.search(user)
            await self.combat_handler(user, opponent, user_msg, author_msg, ctx, e)

    async def combat_handler(self, user, opponent, user_msg, author_msg, ctx, e):
        """Handles the combat between the two users."""
        if isinstance(opponent, UserInQueue):
            if str(user.member.id) + "_" + str(opponent.member.id) in self.map:
                return
            self.user_queue.remove(user)
            self.user_queue.remove(opponent)
            opponent.has_opponent = True
            user.has_opponent = True
            self.map = {str(user.member.id) + "_" + str(opponent.member.id): [user, opponent]}
            opponent_data = Farm.read(opponent.member.id)
            msg_user = await make_embed_object(description=f"🔎 **{user.member.name}**, **{opponent.member.name}** has been found as your opponent. **({opponent_data['mmr']} MMR)**")
            msg_opponent = await make_embed_object(description=f"🔎 **{opponent.member.name}**, **{user.member.name}** has been found as your opponent. **({user.score} MMR)**")
            await user.ctx.send(embed=msg_user)
            await opponent.ctx.send(embed=msg_opponent)
            await asyncio.sleep(3.5)
            author_msg, user_msg = await self.check_if_same_guild(user, opponent, await make_embed_object(description=f"🔥 The match will begin soon."))
            await asyncio.sleep(2.5)
            await self.send_battle_decks(user, opponent, author_msg, user_msg)
            await asyncio.sleep(6)
            await self.define_chicken_matchups(user, opponent, "ranked", user_msg, author_msg, [], [])
        else:
            if isinstance(opponent, BotMatchMaking):
                user.has_opponent = True
                opponent.has_opponent = True
                self.user_queue.remove(user)
                self.user_queue.remove(opponent)
                self.map = {str(user.member.id) + "_" + str(opponent.name): [user, opponent]}
                msg_user = await make_embed_object(description=f"🔎 **{user.member.name}**, **{opponent.name}** has been found as your opponent. **({opponent.score}) MMR**")
                await user.ctx.send(embed=msg_user)
                author_msg, user_msg = await self.check_if_same_guild(user, opponent, await make_embed_object(description=f"🔥 The match will begin soon."))
                await asyncio.sleep(3.5)
                await self.send_battle_decks(user, opponent, author_msg, user_msg)
                await asyncio.sleep(6)
                await self.define_chicken_matchups(user, opponent, "ranked", user_msg, author_msg, [], [])
            elif opponent == "opponent":
                return
            elif opponent == "No opponent found.":
                await send_bot_embed(ctx, description=f":no_entry_sign: {user.member.name}, no opponent has been found. Please try again later.")
                self.user_queue.remove(user)
                EventData.remove(e)
                self.queue.reset_cooldown(ctx)
                return
            
    async def user_queue_generator(self, positive_search_rank, negative_search_rank, current_user, positive_search_overrall, negative_search_overrall):
        for user in self.user_queue:
            if user.score >= negative_search_rank and user.score <= positive_search_rank:
                if user.has_opponent:
                    continue
                if not await self.check_if_user_is_bot(user):
                    if user.member.id == current_user.member.id:
                        continue
                if user.chicken_overrall_score >= negative_search_overrall and user.chicken_overrall_score <= positive_search_overrall:
                    yield user

    async def increase_search_range(self, positive_search, negative_search, current_user, positive_search_overrall, negative_search_overrall): 
        user_list = self.user_queue_generator(positive_search, negative_search, current_user, positive_search_overrall, negative_search_overrall)
        return user_list
    
    async def send_battle_decks(self, user, opponent, author_msg, user_msg):
        opponent_deck = opponent.chickens
        author_deck = user.chickens
        both_deck = await make_embed_object(title=":crossed_swords: Battle decks:")
        both_deck.add_field(name=f"{user.member.name}'s deck:", value= f"\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in author_deck]), inline=False)
        both_deck.add_field(name=f"{await self.check_user_name(opponent)}'s deck:", value= f"\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in opponent_deck]), inline=False)
        await self.check_if_same_guild_edit(user, opponent, user_msg, author_msg, both_deck)
    
    async def search(self, current_user):
        attemps = 0
        saved_positive_score, saved_negative_score = current_user.score, current_user.score
        saved_positive_overrall, saved_negative_overrall = current_user.chicken_overrall_score, current_user.chicken_overrall_score
        while attemps != 30:
            if current_user.has_opponent:
                return "opponent"
            if attemps == 15:   
                bot = await bot_maker(current_user.score)
                self.user_queue.append(bot)
            positive_search = saved_positive_score + 10
            negative_search = saved_negative_score - 10
            positive_search_overrall, negative_search_overrall = saved_positive_overrall + 50, saved_negative_overrall - 50
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
            saved_positive_overrall, saved_negative_overrall = positive_search_overrall, negative_search_overrall
        return "No opponent found."
    
    async def define_chicken_matchups(self, author, user, match_type, user_msg, author_msg, dead_chickens_author, dead_chickens_user):
        """Define the chicken matchups for the combat."""
        author_chickens = author.chickens
        user_chickens = user.chickens
        author_chickens = sample(author_chickens, len(author_chickens))
        user_chickens = sample(user_chickens, len(user_chickens))
        bench_chickens_author = []
        bench_chickens_user = []
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

        print_matchups = [f"**{author.member.name}'s {get_rarity_emoji(match[0]['rarity'])}{match[0]['rarity']} {match[0]['name']}** vs **{await self.check_user_name(user)}'s {get_rarity_emoji(match[1]['rarity'])}{match[1]['rarity']} {match[1]['name']}**" for match in matchups]
        bench_chickens_author_formatted = "\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in bench_chickens_author] if bench_chickens_author else ["No bench chickens."])
        bench_chickens_user_formatted = "\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in bench_chickens_user] if bench_chickens_user else ["No bench chickens."])
        matchups_description = "\n".join(print_matchups)
        embed_per_round = await make_embed_object(
            title="🔥 The matchups have been defined.",
            description=f"Here are the matchups:\n{matchups_description}\n\n**Bench Chickens:**\n {author.member.name}:\n{bench_chickens_author_formatted}\n\n{await self.check_user_name(user)}:\n{bench_chickens_user_formatted}"
        )
        total_matches = len(matchups)
        accumulator = 0
        for match in matchups:
            accumulator += 1
            await self.matches(user, author, match, accumulator, total_matches, embed_per_round, match_type, user_msg, author_msg, dead_chickens_author, dead_chickens_user)

    async def matches(self, user, author, match, accumulator, total_matches, embed_per_round, match_type, user_msg, author_msg, dead_chickens_author, dead_chickens_user):
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
        user_name = await self.check_user_name(user)

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

        winner = await self.check_winner(author, user)
        if winner:
            loser = author if winner == user else user
            EventData.remove(author.in_event)
            if not await self.check_if_user_is_bot(user):
                EventData.remove(user.in_event)
            if dead_chickens_author:
                embed_per_round.add_field(name=f"{author.member.name}'s Dead Chickens:", value="\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in dead_chickens_author]), inline=False)
            if dead_chickens_user:
                embed_per_round.add_field(name=f"{user_name}'s Dead Chickens:", value="\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in dead_chickens_user]), inline=False)
            await self.check_if_same_guild_edit(author, user, user_msg, author_msg, embed_per_round)
            await asyncio.sleep(12)
            await self.rewards(winner, loser, author.ctx, match_type, embed_per_round, user_msg, author_msg)
            return
        else:
            if accumulator == total_matches:
                if dead_chickens_author:
                    embed_per_round.add_field(name=f"{author.member.name}'s Dead Chickens:", value="\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in dead_chickens_author]), inline=False)
                if dead_chickens_user:
                    embed_per_round.add_field(name=f"{user_name}'s Dead Chickens:", value="\n".join([f"**{get_rarity_emoji(chicken['rarity'])}{chicken['rarity']} {chicken['name']}**" for chicken in dead_chickens_user]), inline=False)
                await self.check_if_same_guild_edit(author, user, user_msg, author_msg, embed_per_round)
                embed_per_round.clear_fields()
                await asyncio.sleep(15)
                embed_per_round = await make_embed_object(description=f"🔥 The next round will start shortly.")
                await self.check_if_same_guild_edit(author, user, user_msg, author_msg, embed_per_round)
                await asyncio.sleep(6)
                embed_per_round.clear_fields()
                await self.define_chicken_matchups(author, user, match_type, user_msg, author_msg, dead_chickens_author, dead_chickens_user)
    
    async def check_if_same_guild(self, author, user, embed):
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
        
    async def check_if_same_guild_edit(self, author, user, user_msg, author_msg, embed):
        if await self.check_if_user_is_bot(user):
            await author_msg.edit(embed=embed)
            return
        elif await self.check_if_user_is_bot(author):
            await user_msg.edit(embed=embed)
            return
        if author.ctx.guild.id == user.ctx.guild.id:
            await author_msg.edit(embed=embed)
            return
        else:
            await author_msg.edit(embed=embed)
            await user_msg.edit(embed=embed)
            return

    async def check_if_user_is_bot(self, user):
        if isinstance(user, BotMatchMaking):
            return True
        return False
        
    async def check_user_name(self, user):
        if await self.check_if_user_is_bot(user):
            return user.name
        return user.member.name

    async def check_winner(self, author, user):
        if len(author.chickens) == 0:
            return user
        if len(user.chickens) == 0:
            return author
        return None
    
    async def check_user_score(self, user):
        if not await self.check_if_user_is_bot(user):
            farm_data = Farm.read(user.member.id)
            return [farm_data['mmr'], farm_data['highest_mmr'], farm_data['wins'], farm_data['losses']]
        return [user.score, 0, 0, 0]

    async def rewards(self, winner, loser, ctx, match_type, embed_per_round, winner_msg, loser_msg):
        """Rewards the winner of the combat."""
        if match_type == "ranked":
            farm_data_winner = await self.check_user_score(winner)
            farm_data_loser = await self.check_user_score(loser)
            base_mmr_gain = 25
            multiplier = (loser.score + loser.chicken_overrall_score) / (winner.score + winner.chicken_overrall_score)
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

    async def verify_if_upwards_rank(self, ctx, before_mmr, after_mmr, winner, highest_mmr):
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
        
    async def score_string(self, score):
        for key, value in score_determiner.items():
            if score <= value:
                return key
            
    async def rank_rewards(self, ctx, mmr, highest_mmr, winner):
        """Determines the rewards for the rank."""
        current_rank = await rank_determiner(mmr)
        highest_rank = await rank_determiner(highest_mmr)
        farm_data = Farm.read(winner.member.id)
        user_data = User.read(winner.member.id)
        if chicken_ranking[current_rank] > chicken_ranking[highest_rank]:
            chicken_rewarded, points_gained = await self.rewards_per_rank(chicken_ranking[current_rank])
            chicken_rewarded = await create_chicken(chicken_rewarded, "rewards")
            msg = await make_embed_object(title=f"🎉 {winner.member.name}'s rank rewards", description=f"You've managed to upgrade your rank, here are the following rewards:\n\n :money_with_wings: **{points_gained}** eggbux.")
            User.update_points (winner.member.id, user_data['points'] + points_gained)
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
            
    async def rewards_per_rank(self, rank):
        rank_list = list(chicken_ranking.values())
        chicken_list = list(rarities_weight.keys())
        rank_dictionary = zip(rank_list[1:], chicken_list[9:])
        rank_dictionary = dict(rank_dictionary)
        points_gained = rank * 2
        for key in rank_list:
            if rank == key:
                return rank_dictionary[key], points_gained
    
    @commands.hybrid_command(name="friendly", brief="Friendly combat with another user.", description="Friendly combat with another user.", usage="friendly @user")
    @commands.cooldown(1, queue_command_cooldown, commands.BucketType.user)
    @pricing()
    async def friendly_combat(self, ctx, user: discord.Member):
        """Friendly combat with another user."""
        if user.id == ctx.author.id:
            await send_bot_embed(ctx, description=":no_entry_sign: You can't combat yourself.")
            return
        farm_data = Farm.read(ctx.author.id)
        user_data = Farm.read(user.id)
        if await verify_events(ctx, ctx.author) or await verify_events(ctx, user):
            return
        if farm_data and user_data:
            e = EventData(ctx.author)
            e2 = EventData(user)
            confirmation = await confirmation_embed(ctx, user, f"{user.name}, do you accept the friendly combat request from {ctx.author.name}?")
            if confirmation:
                farm_data['chickens'] = await self.define_eight_chickens_for_match(farm_data['chickens'])
                user_data['chickens'] = await self.define_eight_chickens_for_match(user_data['chickens'])
                author = UserInQueue(ctx.author, farm_data['chickens'], ctx, e, farm_data['mmr'])
                user = UserInQueue(user, user_data['chickens'], ctx, e2, user_data['mmr'])
                author.chicken_overrall_score = await define_chicken_overrall_score(author.chickens)
                user.chicken_overrall_score = await define_chicken_overrall_score(user.chickens)
                author_msg, user_msg = await self.check_if_same_guild(author, user, await make_embed_object(description=f"🔥 The mach will begin soon."))
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
        
    async def define_eight_chickens_for_match(self, chickens):
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
    
async def setup(bot):
    await bot.add_cog(ChickenCombat(bot))