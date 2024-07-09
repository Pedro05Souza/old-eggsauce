import asyncio
from discord.ext import commands
from db.farmDB import Farm
from db.bankDB import Bank
from tools.chickenInfo import ChickenRarity,TradeData, ChickenMultiplier, ChickenFood, RollLimit, determine_chicken_upkeep, chicken_rarities, chicken_default_value
from db.userDB import Usuario
from tools.chickenSelection import ChickenSelectView
from tools.chickenInfo import rollRates, defineRarityEmojis, find_min_upkeep_value
from random import uniform, randint
from time import time
import discord
from tools.pricing import pricing
from tools.embed import create_embed_without_title, create_embed_with_title, make_embed_object

class ChickenCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="createfarm", aliases=["cf"], usage="createFarm", description="Create a farm to start farming eggs.")
    @pricing()
    async def create_farm(self, ctx):
        """Farm some eggs"""
        if Farm.read(ctx.author.id):
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You already have a farm.")
        else:
            Farm.create(ctx.author.id, ctx)
            await create_embed_without_title(ctx, f"{ctx.author.display_name} You have created a farm.")

    @commands.hybrid_command(name="feedallchicken", aliases=["fac"], usage="feedallchicken", description="Feed a chicken.")
    @pricing()
    async def feed_all_chickens(self, ctx):
        """Feed all the chickens"""
        farm_data = Farm.read(ctx.author.id)
        if farm_data:
            if farm_data['corn'] == 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have any corn.")
                return
            total_cost = 0
            all_happiness = 0
            for chicken in farm_data['chickens']:
                if chicken['happiness'] == 100:
                    all_happiness += 1
                    continue
                cost_to_feed = ChickenFood[chicken['rarity']].value
                if farm_data['corn'] > cost_to_feed:
                    total_cost += cost_to_feed
                    chicken['happiness'] = 100
                    all_happiness += 1
                    farm_data['corn'] -= cost_to_feed
                else:
                    break
            if total_cost == 0 and all_happiness != len(farm_data['chickens']):
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't afford to feed any chickens.")
                return
            elif total_cost == 0 and all_happiness == len(farm_data['chickens']):
                await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, all the chickens are already fed.")
                return
            Farm.update_corn(ctx.author.id, farm_data['corn'])
            Farm.update_chickens(ctx.author.id, farm_data['chickens'])
            await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, all the chickens have been fed.\n:corn:The corn cost was {total_cost}.")

    @commands.hybrid_command(name="market", aliases=["m"], usage="market", description="Market that generates 10 random chickens to buy.")
    @pricing()
    async def market(self, ctx):
        """Market to buy chickens"""
        if Farm.read(ctx.author.id):
            default_rolls = 15
            chickens_generated = 8
            plrObj = RollLimit.read(ctx.author.id)
            if not plrObj:
                farm_data = Farm.read(ctx.author.id)    
                if farm_data['farmer'] == "Executive Farmer":
                    plrObj = RollLimit(ctx.author.id, default_rolls + self.load_farmer_upgrades(ctx.author.id)[0])
                else:
                    plrObj = RollLimit(ctx.author.id, default_rolls)
            if plrObj.current == 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} you have reached the limit of rolls for today.")
                return
            plrObj.current -= 1
            if Farm.read(ctx.author.id)['farmer'] == "Generous Farmer":
                chickens_generated += self.load_farmer_upgrades(ctx.author.id)[0]
            generated_chickens = self.generate_chickens(*self.roll_rates_sum(), chickens_generated, ctx)
            plrObj.chickens = generated_chickens
            message = await make_embed_object(title=f":chicken: {ctx.author.display_name} here are the chickens you generated to buy: \n", description="\n".join([f" {self.get_rarity_emoji(chicken['rarity'])} **{index + 1}.** **{chicken['rarity']} {chicken['name']}**: {chicken['price']} eggbux." for index, chicken in enumerate(generated_chickens)]))
            view = ChickenSelectView(chickens=generated_chickens, author=ctx.author.id, action="M", message=message, chicken_emoji=self.get_rarity_emoji)
            await ctx.send(embed=message, view=view)
                         
    def roll_rates_sum(self):
        """Roll the sum of the rates of the chicken rarities"""
        return sum(rollRates.values()), rollRates
    
    def load_farmer_upgrades(self, player_id):
        """Load the farmer upgrades"""
        farmer_dict = {
            "Rich Farmer": 10,
            "Guardian Farmer": 4,
            "Executive Farmer" : [8, 4],
            "Warrior Farmer": 3,
            "Generous Farmer": [3]
        }
        player_farmer = Farm.read(player_id)['farmer']
        return farmer_dict[player_farmer]
    
    def generate_chickens(self, rollRatesSum, rollRates, quant, ctx):
        """Generate chickens according to the roll rates"""
        default_value = chicken_default_value
        generated_chickens = []
        author_data = Farm.read(ctx.author.id)
        initial_range = 1
        for _ in range(quant):
            randomRoll = uniform(initial_range, rollRatesSum)
            for rarity, rate in rollRates.items():
                if randomRoll <= rate:
                    chicken_price = default_value * ChickenRarity[rarity].value
                    if author_data['farmer'] == 'Executive Farmer':
                        discount = self.load_farmer_upgrades(ctx.author.id)[1]
                        chicken_price = ChickenRarity[rarity].value * default_value - (ChickenRarity[rarity].value * default_value * discount) // 100
                    generated_chickens.append({
                        "rarity" : rarity,
                        "name" : "Chicken",
                        "price" : chicken_price
                    })
                    break
                randomRoll -= rate
        return generated_chickens
    
    def get_rarity_emoji(self, rarity):
        return defineRarityEmojis[rarity]
    
    async def reset_periodically(self):
        """Reset the roll limit every 12 hours"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await asyncio.sleep(43200 - time() % 43200)
            RollLimit.removeAll()
    
    @commands.hybrid_command(name="farm", aliases=["f"], usage="farm OPTIONAL [user]", description="Check the chickens in the farm.")
    @pricing()
    async def farm(self, ctx, user: discord.Member = None):
        """Check the chickens in the farm"""
        if user is None:
            user = ctx.author
        if Farm.read(user.id):
            await ctx.send(embed=await self.get_usr_farm(user))
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} doesn't have a farm.")

    @commands.hybrid_command(name="sellchicken", aliases=["sc"], usage="sellChicken", description="Deletes a chicken from the farm.")
    @pricing()
    async def sell_chicken(self, ctx):
        """Deletes a chicken from the farm"""
        if Farm.read(ctx.author.id):
            if not Farm.read(ctx.author.id)['chickens']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You don't have any chickens.")
                return
            farm_data = Farm.read(ctx.author.id)
            message = await self.get_usr_farm(ctx.author)
            view = ChickenSelectView(message=message, chickens=farm_data['chickens'], author=ctx.author.id, action="D", chicken_emoji=self.get_rarity_emoji)
            await ctx.send(embed=message,view=view)
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} you do not have a farm.")

    @commands.hybrid_command(name="renamefarm", aliases=["rf"], usage="renameFarm <nickname>", description="Rename the farm.")
    @pricing()
    async def rename_farm(self, ctx, nickname: str):
        """Rename the farm"""
        if Farm.read(ctx.author.id):
            farm_data = Farm.read(ctx.author.id)
            if len(nickname) > 20:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} The farm name must have a maximum of 20 characters.")
                return
            farm_data['farm_name'] = nickname
            Farm.update(ctx.author.id, nickname, farm_data['chickens'], farm_data['eggs_generated'])
            await create_embed_without_title(ctx, f"{ctx.author.display_name} Your farm has been renamed to {nickname}.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You do not have a farm.")

    @commands.hybrid_command(name="renamechicken", aliases=["rc"], usage="renameChicken <index> <nickname>", description="Rename a chicken in the farm.")
    @pricing()
    async def rename_chicken(self, ctx, index: int, nickname: str):
        """Rename a chicken in the farm"""
        index -= 1
        if Farm.read(ctx.author.id):
            farm_data = Farm.read(ctx.author.id)
            if not farm_data['chickens']:
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have any chickens.")
                    return
            if len(nickname) > 15:
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the chicken name must have a maximum of 15 characters.")
                    return
            if index > len(farm_data['chickens']) or index < 0:
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
                    return
            check_nickname = nickname.upper()
            if check_nickname in ChickenRarity.__members__:
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't rename a chicken with a rarity name.")
            chicken_arr = farm_data['chickens']
            for i, chicken in enumerate(chicken_arr):
                if index == i:
                    chicken_arr[i]['name'] = nickname
                    break
            farm_data['chickens'] = chicken_arr
            Farm.update(ctx.author.id, farm_data['farm_name'], farm_data['chickens'], farm_data['eggs_generated'])
            await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, the chicken has been renamed to {nickname}.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have a farm.")

    @commands.hybrid_command(name="tradechicken", aliases=["tc", "trade"], usage="tradeChicken <user>", description="Trade a chicken(s) with another user.")
    @pricing()
    async def trade_chicken(self, ctx, user: discord.Member):
        """Trade a chicken(s) with another user"""
        author_involved_in_trade = TradeData.read(ctx.author.id)
        target_involved_in_trade = TradeData.read(user.id)

        if author_involved_in_trade:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you already have a trade in progress.")
            return
        if target_involved_in_trade:
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} already has a trade request in progress.")
            return
        
        if Farm.read(ctx.author.id) and Farm.read(user.id):
            farm_data = Farm.read(ctx.author.id)
            if not farm_data['chickens'] or not Farm.read(user.id)['chickens']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, {user.display_name} doesn't have any chickens.")
                return
            if user.id == ctx.author.id:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't trade with yourself.")
                return
            t = TradeData()
            t.identifier = [ctx.author.id, user.id]
            msg = await create_embed_without_title(ctx, f":chicken: {ctx.author.display_name} has sent a trade request to {user.display_name}. You have 40 seconds to react with ✅ to accept or ❌ to decline.")
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            try:
                reaction, usr = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == user and reaction.message == msg, timeout=40)
                if reaction.emoji == "✅":
                    if not author_involved_in_trade and not target_involved_in_trade:
                        await self.trade_chickens(ctx, user, t)
                elif reaction.emoji == "❌":
                    await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} has declined the trade request.")
                    TradeData.remove(t)
                    return
            except asyncio.TimeoutError:
                await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} has not responded to the trade request.")
                TradeData.remove(t)
                
    @commands.hybrid_command(name="farmprofit", aliases=["fp"], usage="farmprofit OPTIONAL [user]", description="Check the farm profit.")
    @pricing()
    async def farm_profit(self, ctx, user: discord.Member = None):
        """Check the farm profit"""
        if user is None:
            user = ctx.author
        if Farm.read(user.id):
            farm_data = Farm.read(user.id)
            totalProfit = 0
            totalLoss = 0
            totalcorn = 0
            if len(farm_data['chickens']) == 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, you don't have any chickens.")
                return
            for chicken in farm_data['chickens']:
                totalcorn += ChickenFood[chicken['rarity']].value
                totalProfit += (chicken['egg_value'] * chicken['happiness']) // 100
                if farm_data['farmer'] == 'Guardian Farmer':
                    to_reduce = self.load_farmer_upgrades(user.id)
                    totalLoss += chicken['upkeep_multiplier'] - (chicken['upkeep_multiplier'] * to_reduce) // 100
                else:
                    totalLoss += chicken['upkeep_multiplier']
            if farm_data['farmer'] == "Rich Farmer":
                to_add = self.load_farmer_upgrades(user.id)
                added_value = (totalProfit * to_add) // 100
                totalProfit += added_value
            result = totalProfit - totalLoss
            if result > 0:
                await create_embed_without_title(ctx, f":white_check_mark: {user.display_name}, your farm is expected to generate a profit of **{result}** per hour :money_with_wings:.\n:chicken: Chicken upkeep: **{totalLoss}**\n:egg: Eggs produced: **{totalProfit}**\n :corn: Corn going to the chickens: **{totalcorn}**.")
            elif result < 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, your farm is expected to generate a loss of **{result}** per hour :money_with_wings:.\n:chicken: Money expected to go woards feeding the chickens: **{totalLoss}**\n:egg: Eggs produced: **{totalProfit}**\n:corn:Corn going to the chickens: **{totalcorn}**.")
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, your farm is expected to generate neither profit nor loss.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, you don't have a farm.")

    async def trade_chickens(self, ctx, User: discord.Member, t):
        """Trade the chickens"""
        author_data = Farm.read(ctx.author.id)
        user_data = Farm.read(User.id)
        authorEmbed = await self.get_usr_farm(ctx.author)
        userEmbed = await self.get_usr_farm(User)
        trade_data = [author_data['chickens'], user_data['chickens']]
        members_data = [ctx.author, User]
        embeds = [authorEmbed, userEmbed]
        view_author = ChickenSelectView(chickens=trade_data, author=members_data, action="T", message=embeds, chicken_emoji=self.get_rarity_emoji, role="author", trade_data=t)
        view_user = ChickenSelectView(chickens=trade_data, author=members_data, action="T", message=embeds, chicken_emoji=self.get_rarity_emoji, role="user", trade_data=t, instance_bot = self.bot)
        await ctx.send(embed=authorEmbed, view=view_author)
        await ctx.send(embed=userEmbed, view=view_user)

    async def get_usr_farm(self, User: discord.Member):
        """Get the user's farm"""
        if Farm.read(User.id):
            user_data = Farm.read(User.id)
            msg = await make_embed_object(
                title=f":chicken: {user_data['farm_name']}\n\n:egg: **Eggs generated**: {user_data['eggs_generated']}\n:farmer: Farmer: {user_data['farmer'] if user_data['farmer'] else 'No Farmer.'}",
                description="\n".join([
                f"{self.get_rarity_emoji(chicken['rarity'])}  **{index + 1}.** **{chicken['rarity']} {chicken['name']}** \n:partying_face: Happiness: **{chicken['happiness']}%**\n :gem: Upkeep rarity: **{self.determine_upkeep_rarity(chicken)}**\n"
                for index, chicken in enumerate(user_data['chickens'])
            ]))
            msg.set_thumbnail(url=User.display_avatar)
            return msg
        else:
            return None

    @commands.hybrid_command(name="chickenrarities", aliases=["cr"], usage="chickenRarities", description="Check the rarities of the chickens.")
    @pricing()
    async def check_chicken_rarities(self, ctx):
        """Check the rarities of the chickens"""
        rarity_info = "\n".join([f"{self.get_rarity_emoji(rarity)} **{rarity}**: {round(rate/100, 4)}%" for rarity, rate in rollRates.items()])
        await create_embed_with_title(ctx, "Chicken Rarities:", rarity_info)

    @commands.hybrid_command(name="chickenvalues", aliases=["cv"], usage="chickenValues", description="Check the values of eggs produced by chickens.")
    @pricing()
    async def check_chicken_values(self, ctx):
        """Check the amount of eggs produced by chickens"""
        value_info = "\n".join([f"{self.get_rarity_emoji(rarity)} **{rarity}**: {ChickenMultiplier[rarity].value}x" for rarity in ChickenMultiplier.__members__])
        await create_embed_with_title(ctx, "Amount of eggs produced by rarity:", value_info)
    
    @commands.hybrid_command(name="chickencorn", usage="chickencorn", description="Show all the chicken food values.")
    @pricing()
    async def chicken_corn(self, ctx):
        """Show all the chicken food values"""
        corn_info = "\n".join([f"{self.get_rarity_emoji(rarity)} **{rarity}**: {ChickenFood[rarity].value}" for rarity in ChickenFood.__members__])
        await create_embed_with_title(ctx, "Chicken food values:", corn_info)
    
    @commands.hybrid_command(name="chickenprices", aliases=["cprice"], usage="chickenPrices", description="Check the prices of the chickens.")
    @pricing()
    async def check_chicken_prices(self, ctx):
        """Check the prices of the chickens"""
        prices_info = "\n".join([f"{self.get_rarity_emoji(rarity)} **{rarity}**: {175 * ChickenRarity[rarity].value} eggbux" for rarity in ChickenRarity.__members__])
        await create_embed_with_title(ctx, "Chicken prices:", prices_info)

    @commands.hybrid_command(name="giftchicken", aliases=["gc"], usage="giftChicken <index> <user>", description="Gift a chicken to another user.")
    @pricing()
    async def gift_chicken(self, ctx, index: int, user: discord.Member):
        """Gift a chicken to another user"""
        index -= 1
        if Farm.read(ctx.author.id) and Farm.read(user.id):
            author_data = Farm.read(ctx.author.id)
            user_data = Farm.read(user.id)
            if not author_data['chickens']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have any chickens.")
                return
            if index > len(author_data['chickens']) or index < 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
                return
            if user.id == ctx.author.id:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't gift a chicken to yourself.")
                return
            if len(user_data['chickens']) >= self.get_max_chicken_limit():
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, {user.display_name} already has the maximum amount of chickens.")
                return
            gifted_chicken = author_data['chickens'][index]
            msg = await create_embed_without_title(ctx, f":gift: {user.display_name}, {ctx.author.display_name} wants to gift you a {gifted_chicken['rarity']} {gifted_chicken['name']}. You have 20 seconds to react with ✅ to accept or ❌ to decline the gift request.")
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            try:
                reaction, jogador = await self.bot.wait_for("reaction_add", check=lambda reaction, jogador: jogador == user and reaction.message == msg, timeout=40)
                if reaction.emoji == "✅":
                    chicken = author_data['chickens'][index]
                    user_data['chickens'].append(chicken)
                    author_data['chickens'].remove(chicken)
                    Farm.update(ctx.author.id, author_data['farm_name'], author_data['chickens'], author_data['eggs_generated'])
                    Farm.update(user.id, user_data['farm_name'], user_data['chickens'], user_data['eggs_generated'])
                    await create_embed_without_title(ctx, f":gift: {ctx.author.display_name}, the chicken has been gifted to {user.display_name}.")
                elif reaction.emoji == "❌":
                    await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} has declined the gift request.")
                    return
            except asyncio.TimeoutError:
                await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} has not responded to the gift request.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you or {user.display_name} don't have a farm.")
    
    @commands.hybrid_command(name="evolvechicken", aliases=["ec"], usage="evolveChicken <index> <index2>", description="Evolve a chicken if having 2 of the same rarity.")
    @pricing()
    async def evolve_chicken(self, ctx, index: int, index2: int):
        """Evolves a chicken if having 2 of the same rarity"""
        farm_data = Farm.read(ctx.author.id)
        if farm_data:
            if not farm_data['chickens']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have any chickens.")
                return
            if index > len(farm_data['chickens']) or index < 0 or index2 > len(farm_data['chickens']) or index2 < 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
                return
            chicken_selected = farm_data['chickens'][index - 1]
            chicken_removed = farm_data['chickens'][index2 - 1]
            if chicken_selected['rarity'] != chicken_removed['rarity']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the chickens must be of the same rarity to evolve.")
                return
            if chicken_selected['rarity'] == "ASCENDED" or chicken_removed['rarity'] == "ASCENDED":
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't evolve an ascended chicken.")
                return
            rarity_list = list(ChickenRarity.__members__)
            chicken_selected['rarity'] = rarity_list[rarity_list.index(chicken_selected['rarity']) + 1]
            chicken_selected['egg_value'] = ChickenMultiplier[chicken_selected['rarity']].value
            chicken_selected['price'] = chicken_default_value * ChickenRarity[chicken_selected['rarity']].value
            chicken_selected['upkeep_multiplier'] = determine_chicken_upkeep(chicken_selected)
            farm_data['chickens'].remove(chicken_removed)
            Farm.update_chickens(ctx.author.id, farm_data['chickens'])
            await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, the chicken has been evolved to {chicken_selected['rarity']} {chicken_selected['name']}.")
            
    @commands.hybrid_command(name="chickeninfo", aliases=["ci"], usage="chickenInfo <index>", description="Check the information of a chicken.")
    @pricing()
    async def check_chicken_info(self, ctx, index: int):
        """Check the information of a chicken."""
        farm_data = Farm.read(ctx.author.id)
        if farm_data:
            if index > len(farm_data['chickens']) or index < 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
                return
            chicken = farm_data['chickens'][index - 1]
            msg = await make_embed_object(title=f":chicken: {chicken['rarity']} {chicken['name']}", description=f":partying_face: **Happiness**: {chicken['happiness']}%\n:moneybag: **Price**: {chicken['price']} eggbux\n:egg: **Egg value**: {chicken['egg_value']} \n:gem: **Upkeep rarity**: {chicken['upkeep_multiplier']}\n:coin: **Eggs generated:** {chicken['eggs_generated']}\n:corn: **Food necessary:** {ChickenFood[chicken['rarity']].value} \n:money_with_wings: **Total profit: {(chicken['egg_value'] * chicken['happiness']) // 100 - chicken['upkeep_multiplier']} eggbux.**")
            await ctx.send(embed=msg)

    @commands.hybrid_command(name="farmer", usage="farmer", description="The farmers helps increase the productivity of the chickens.")
    @pricing()
    async def farmer(self, ctx):
        """The farmer automatically feeds the chickens"""
        farmer_price = 2500
        description = [
            ":moneybag: Rich Farmer: Increase the egg value of the chickens by 10%.\n",
            ":shield: Guardian Farmer: Whenever you sell a chicken, sell it for the full price and reduces upkeep by 4%.\n",
            ":briefcase: Executive Farmer: Gives you 4 more daily rolls in the market and chickens generated in the market comes with 30% discount. \n",
            ":crossed_swords: Warrior Farmer: Gives 3 more farm slots.\n",
            ":leaves: Sustainable Farmer: Auto-feeds the chickens every 4 hours, the happiness generated is a number between 20-40%. The farmer uses the money from your bank account.\n",
            ":tickets: Generous Farmer: Increases the maximum chickens generated in the market by 3 slots.\n"
            f"\n\nAll the farmer roles have a cost of **{farmer_price}** eggbux and you can only buy one of them. **Buying a farmer when you already have one will override the existing one.**\nReact with the corresponding emoji to purchase the role."
        ]
        message = await create_embed_with_title(ctx, ":farmer: Farmer roles:\n", "\n".join(description))
        emojis = ["💰", "🛡️", "💼", "⚔️", "🍃", "🎟️"]
        for emoji in emojis:
            await message.add_reaction(emoji)
        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.message == message, timeout=40)
            if Usuario.read(user.id)['points'] >= farmer_price:
                if Farm.read(user.id)['farmer'] == 'Warrior Farmer' and len(Farm.read(user.id)['chickens']) > 8 and reaction.emoji in emojis:
                    await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} you have a Warrior farmer, you need to sell the extra farm slots to buy another farmer.")
                    return
                if reaction.emoji == "💰":
                    await self.buy_farmer_upgrade(ctx, "Rich Farmer", farmer_price)
                elif reaction.emoji == "🛡️":
                    await self.buy_farmer_upgrade(ctx, "Guardian Farmer", farmer_price)
                elif reaction.emoji == "💼":
                    await self.buy_farmer_upgrade(ctx, "Executive Farmer", farmer_price)
                elif reaction.emoji == "⚔️":
                    await self.buy_farmer_upgrade(ctx, "Warrior Farmer", farmer_price)
                elif reaction.emoji == "🍃":
                    await self.buy_farmer_upgrade(ctx, "Sustainable Farmer", farmer_price)
                elif reaction.emoji == "🎟️":
                    await self.buy_farmer_upgrade(ctx, "Generous Farmer", farmer_price)
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have enough eggbux to purchase a farmer role.")
        except asyncio.TimeoutError:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you have not selected a farmer role.")

    async def buy_farmer_upgrade(self, ctx, name, farmer_price):
        """Buy the farmer upgrade"""
        user_data = Usuario.read(ctx.author.id)
        farm_data = Farm.read(ctx.author.id)
        if user_data['points'] >= farmer_price:
            farm_data['farmer'] = name
            Usuario.update(ctx.author.id, user_data['points'] - farmer_price, user_data['roles'])
            Farm.update_farmer(ctx.author.id, name)
            await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, you have purchased the {name} farmer role.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have enough eggbux to purchase the {name} farmer role.")

    async def devolve_chicken(self, chicken):
        """Devolve a chicken if its happiness is 0"""
        devolveChance = randint(1, 3)
        cr = chicken['rarity']
        if cr in ChickenRarity.__members__ and cr != 'COMMON':
            if devolveChance == 1 and chicken['happiness'] <= 0:
                rarity_list = list(ChickenRarity)
                index = rarity_list.index(ChickenRarity[cr])
                devolded_rarity = rarity_list[index - 1].name
                chicken['happiness'] = 100
                chicken['rarity'] = devolded_rarity
                chicken['egg_value'] = ChickenMultiplier[devolded_rarity].value
                chicken['price'] = chicken_default_value * ChickenRarity[devolded_rarity].value
                chicken['upkeep_multiplier'] = self.determine_upkeep_rarity(chicken)
                return
        elif cr == 'COMMON' and chicken['happiness'] <= 0 and devolveChance == 1:
            chicken['rarity'] = 'DEAD'
            chicken['happiness'] = 0
            chicken['egg_value'] = 0
            chicken['price'] = 0
            chicken['upkeep_multiplier'] = 0
            return

    def get_max_chicken_limit(self):
        """Get the maximum chicken limit"""
        return 10

    def determine_upkeep_rarity(self, chicken):
        chicken_upkeep = chicken['upkeep_multiplier']
        min_upkeep = find_min_upkeep_value(chicken)
        if min_upkeep != 1:
            max_upkeep = min_upkeep * 2
        else:
            max_upkeep = ((ChickenMultiplier[chicken['rarity']].value * 2) // 5) * 2
        ratio = (chicken_upkeep - min_upkeep) / (max_upkeep - min_upkeep)
        for rarity, value in chicken_rarities.items():
            if ratio >= value:
                return rarity
                    
    async def drop_eggs(self):
        """Drop eggs periodically"""
        plrDict = {}
        for player in Farm.readAll():
            bank_data = Bank.read(player['user_id'])
            bank_money = 0
            if not bank_data:
                bank_money = 0
            else:
                bank_money = bank_data['bank']
            if len(player['chickens']) > 0:
                player_id = player['user_id']
                plrDict[player_id] = {
                    "chicken_list" : player['chickens'],
                    "totalEggs" : 0,
                    "Farmer" : player["farmer"],
                    "bank" : bank_money, 
                }
                totalUpkeep = 0
                for chicken in plrDict[player_id]['chicken_list']:
                    if chicken['rarity'] == 'DEAD':
                        continue
                    totalUpkeep += chicken['upkeep_multiplier']
                    egg_produced = (chicken['egg_value'] * chicken['happiness']) // 100
                    if plrDict[player_id]['Farmer'] == "Rich Farmer":
                        bonus = self.load_farmer_upgrades(player_id)
                        egg_produced += (egg_produced * bonus) // 100
                    plrDict[player_id]['totalEggs'] += egg_produced
                    chicken['eggs_generated'] += egg_produced
                    if chicken['happiness'] > 0:
                        chicken['happiness'] -= randint(1, 5)
                    if chicken['happiness'] < 0:
                        chicken['happiness'] = 0
                    if chicken['happiness'] == 0:
                        await self.devolve_chicken(chicken)
                if plrDict[player_id]['bank'] < totalUpkeep:
                    plrDict[player_id]['totalEggs'] = 0
                    devolved_chicken = randint(0, len(plrDict[player_id]['chicken_list']) - 1)
                    await self.devolve_chicken(plrDict[player_id]['chicken_list'][devolved_chicken])
                else:
                    plrDict[player_id]['bank'] -= totalUpkeep
        for player_id, player in plrDict.items():
            Farm.update(player_id, Farm.read(player_id)['farm_name'], player['chicken_list'], Farm.read(player_id)['eggs_generated'] + player['totalEggs'])
            if player['totalEggs'] > 0:
                Usuario.update(player_id, Usuario.read(player_id)['points'] + player['totalEggs'], Usuario.read(player_id)['roles'])
            Bank.update(player_id, player['bank'])
        print("Eggs dropped!")
    
    async def feed_eggs_auto(self):
        """Feed the chickens automatically"""
        for player in Farm.readAll():
            if player['farmer'] == "Sustainable Farmer":
                for chicken in player['chickens']:
                    if chicken['happiness'] == 100:
                        continue
                    totalUpkeep = chicken['upkeep_multiplier']
                    if Usuario.read(player['user_id'])['points'] > totalUpkeep:
                        Usuario.update(player['user_id'], Usuario.read(player['user_id'])['points'] - totalUpkeep, Usuario.read(player['user_id'])['roles'])
                        generated_happines = randint(20, 60)
                        cHappiness = chicken['happiness'] + generated_happines
                        if cHappiness > 100:
                            cHappiness = 100
                        chicken['happiness'] = cHappiness
                Farm.update(player['user_id'], player['farm_name'], player['chickens'], player['eggs_generated'])
        print("Chickens fed automatically!")

    async def make_eggs_periodically(self):
        """Make eggs periodically"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await asyncio.sleep(3600 - time() % 3600)
            await self.drop_eggs()

    async def feed_chickens_periodically(self):
        """Feed the chickens periodically"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await asyncio.sleep(14400 - time() % 14400)
            await self.feed_eggs_auto()
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.reset_periodically())
        self.bot.loop.create_task(self.make_eggs_periodically())
        self.bot.loop.create_task(self.feed_chickens_periodically())

async def setup(bot):
    await bot.add_cog(ChickenCommands(bot))