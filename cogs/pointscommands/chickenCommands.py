import asyncio
from discord.ext import commands
from db.farmDB import Farm
from time import time
from tools.chickenInfo import ChickenRarity, ChickenUpkeep, TradeData
from db.userDB import Usuario
from tools.chickenSelection import ChickenSelectView
from tools.chickenInfo import rollRates, defineRarityEmojis
from random import uniform, randint
import discord
from tools.pricing import pricing
from tools.embed import create_embed_without_title, create_embed_with_title
roll_limit = {}

class ChickenCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="createfarm", aliases=["cf"], usage="createFarm", description="Create a farm to start farming eggs.")
    @pricing()
    async def create_farm(self, ctx):
        """Farm some eggs"""
        if Usuario.read(ctx.author.id):
            if Farm.read(ctx.author.id):
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You already have a farm.")
            else:
                Farm.create(ctx.author.id, ctx)
                await create_embed_without_title(ctx, f"{ctx.author.display_name} You have created a farm.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You are not registered in the database.")

    @commands.hybrid_command(name="market", aliases=["m"], usage="market", description="Market that generates 10 random chickens to buy.")
    @pricing()
    async def market(self, ctx):
        """Market to buy chickens"""
        if ctx.author.id not in roll_limit:
            roll_limit[ctx.author.id] = {
                "limit": 0,
                "chickens": []
            }

        if roll_limit[ctx.author.id]['limit'] >= 20:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You have reached the limit of chickens you can buy today.")
            return
        roll_limit[ctx.author.id]['limit'] += 1
        generated_chickens = self.generate_chickens(*self.roll_rates_sum(), 10)
        roll_limit[ctx.author.id]['chickens'] = generated_chickens
        message = discord.Embed(title=f":chicken: {ctx.author.display_name} here are the chickens you generated to buy: \n", description="\n".join([f" {self.get_rarity_emoji(chicken['Name'])} **{index + 1}.** **{chicken['Name']}**: {chicken['Price']}" for index, chicken in enumerate(generated_chickens)]))
        view = ChickenSelectView(chickens=generated_chickens, author=ctx.author.id, action="M", message=message, chicken_emoji=self.get_rarity_emoji)
        await ctx.send(embed=message, view=view)
  
    def roll_rates_sum(self):
        """Roll the sum of the rates of the chicken rarities"""
        return sum(rollRates.values()), rollRates
    
    def generate_chickens(self, rollRatesSum, rollRates, quant):
        """Generate chickens according to the roll rates"""
        default_value = 175
        generated_chickens = []
        for _ in range(quant):
            randomRoll = uniform(1, rollRatesSum)
            print(randomRoll)
            for rarity, rate in rollRates.items():
                if randomRoll <= rate:
                    generated_chickens.append({
                        "Name" : f"{rarity} Chicken",
                        "Price" : f" {default_value * ChickenRarity[rarity].value} eggbux.",
                        "Bought" : False
                    })
                    break
                randomRoll -= rate
        return generated_chickens
    
    def get_rarity_emoji(self, rarity):
        return defineRarityEmojis[rarity.split()[0]]
    
    async def reset_periodically(self):
        """Reset the roll limit every 24 hours"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            roll_limit.clear()
            await asyncio.sleep(86400)
    
    @commands.hybrid_command(name="farm", aliases=["f"], usage="farm OPTIONAL [user]", description="Check the chickens in the farm.")
    @pricing()
    async def farm(self, ctx, user: discord.Member = None):
        """Check the chickens in the farm"""
        if user is None:
            user = ctx.author
        if Farm.read(user.id):
            await ctx.send(embed=self.get_usr_farm(user))
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, doesn't have a farm.")

    @commands.hybrid_command(name="sellchicken", aliases=["sc"], usage="sellChicken", description="Deletes a chicken from the farm.")
    @pricing()
    async def sell_chicken(self, ctx):
        """Deletes a chicken from the farm"""
        if Farm.read(ctx.author.id):
            if not Farm.read(ctx.author.id)['chickens']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You don't have any chickens.")
                return
            farm_data = Farm.read(ctx.author.id)
            message = self.get_usr_farm(ctx.author)
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
            farm_data['Name'] = nickname
            Farm.update(ctx.author.id, nickname, farm_data['chickens'], farm_data['eggs_generated'])
            await create_embed_without_title(ctx, f"{ctx.author.display_name} Your farm has been renamed to {nickname}.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You do not have a farm.")

    @commands.hybrid_command(name="showchickenupkeep", aliases=["su"], usage="showChickenUpkeep", description="Show the upkeep of chickens per rarity.")
    async def show_chicken_upkeep(self, ctx):
        """Show the upkeep of the chickens"""
        upkeep_info = "\n".join([f"{self.get_rarity_emoji(rarity)} **{rarity}**: {ChickenUpkeep[rarity].value}x" for rarity in ChickenRarity.__members__])
        await create_embed_with_title(ctx, "Chicken Upkeep multiplier per rarity:", upkeep_info)

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
                    chicken_arr[i]['Name'] = chicken['Name'].replace(chicken['Name'].split()[1], nickname)
                    break
            farm_data['chickens'] = chicken_arr
            Farm.update(ctx.author.id, farm_data['farm_name'], farm_data['chickens'], farm_data['eggs_generated'])
            await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, the chicken has been renamed to {nickname}.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have a farm.")

    @commands.command("tradechicken", aliases=["trade"])
    @pricing()
    async def trade_chicken(self, ctx, User: discord.Member):
        """Trade a chicken(s) with another user"""
        author_involved_in_trade = TradeData.read(ctx.author.id)
        target_involved_in_trade = TradeData.read(User.id)
        if author_involved_in_trade:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you already have a trade in progress.")
            return
        if target_involved_in_trade:
            await create_embed_without_title(ctx, f":no_entry_sign: {User.display_name} already has a trade request in progress.")
            return
        
        if Farm.read(ctx.author.id) and Farm.read(User.id):
            farm_data = Farm.read(ctx.author.id)
            if not farm_data['chickens'] and not Farm.read(User.id)['chickens']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, {User.display_name} doesn't have any chickens.")
                return
            if User.id == ctx.author.id:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't trade with yourself.")
                return
            t = TradeData()
            t.identifier = [ctx.author.id, User.id]
            msg = await create_embed_without_title(ctx, f":chicken: {ctx.author.display_name} has sent a trade request to {User.display_name}. You have 20 seconds to react with ✅ to accept or ❌ to decline.")
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            reaction, usr = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == User and reaction.message == msg, timeout=40)
            if reaction.emoji == "✅":
                if not author_involved_in_trade and not target_involved_in_trade:
                    await self.trade_chickens(ctx, User, t)
            elif reaction.emoji == "❌":
                await create_embed_without_title(ctx, f":no_entry_sign: {User.display_name} has declined the trade request.")
                TradeData.remove(t)
                return
                
    @commands.hybrid_command(name="feedchicken", aliases=["fc"], usage="feedChicken <index>", description="Feed a chicken in the farm.")
    @pricing()
    async def feed_chicken(self, ctx, index: int):
        """Feed a chicken"""
        index -= 1
        if Usuario.read(ctx.author.id):
            if Farm.read(ctx.author.id):
                farm_data = Farm.read(ctx.author.id)
                if not farm_data['chickens']:
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have any chickens.")
                    return
                if index > len(farm_data['chickens']) or index < 0:
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
                    return
                baseUpkeep = ChickenUpkeep[farm_data['chickens'][index]['Name'].split()[0]].value
                chicken_arr = farm_data['chickens']
                if Usuario.read(ctx.author.id)['points'] > baseUpkeep:
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)['points'] - baseUpkeep, Usuario.read(ctx.author.id)['roles'])
                    for i, chicken in enumerate(chicken_arr):
                        if index == i:
                            if chicken['Happiness'] == 100:
                                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the chicken is already at maximum happiness.")
                                Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)['points'] + baseUpkeep, Usuario.read(ctx.author.id)['roles'])
                                return
                            generated_happines = randint(20, 60)
                            cHappiness = chicken['Happiness'] + generated_happines
                            if cHappiness > 100:
                                cHappiness = 100
                            chicken_arr[i]['Happiness'] = cHappiness
                            break
                    farm_data['chickens'] = chicken_arr
                    Farm.update(ctx.author.id, farm_data['farm_name'], farm_data['chickens'], farm_data['eggs_generated'])
                    await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, the chicken has been fed and its happiness is now **{cHappiness}%**. The upkeep cost was **{baseUpkeep}** :money_with_wings:.")
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have a farm.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you are not registered in the database.")

    @commands.hybrid_command(name="feedallchickens", aliases=["fac"], usage="feedAllChickens", description="Feed all the chickens in the user's farm.")
    @pricing()
    async def feed_all_chickens(self, ctx):
        """Feed all the chickens in the user's inventory"""
        if Farm.read(ctx.author.id):
            farm_data = Farm.read(ctx.author.id)
            if not farm_data['chickens']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have any chickens.")
                return
            totalUpkeep = 0
            for chiken in farm_data['chickens']:
                totalUpkeep += ChickenUpkeep[chiken['Name'].split()[0]].value
            if Usuario.read(ctx.author.id)['points'] > totalUpkeep:
                Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)['points'] - totalUpkeep, Usuario.read(ctx.author.id)['roles'])
                if all(c['Happiness'] == 100 for c in farm_data['chickens']):
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, all the chickens are already at maximum happiness.")
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)['points'] + totalUpkeep, Usuario.read(ctx.author.id)['roles'])
                    return
                for chicken in farm_data['chickens']:
                    if chicken['Happiness'] == 100:
                        continue
                    generated_happines = randint(20, 40)
                    cHappiness = chicken['Happiness'] + generated_happines
                    if cHappiness > 100:
                        cHappiness = 100
                    chicken['Happiness'] = cHappiness
                Farm.update(ctx.author.id, farm_data['farm_name'], farm_data['chickens'], farm_data['eggs_generated'])
                await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, all the chickens have been fed. The upkeep cost was **{totalUpkeep}** :money_with_wings:.")
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have enough eggbux to feed all the chickens.")

    @commands.hybrid_command(name="farmprofit", aliases=["fp"], usage="farmprofit OPTIONAL [user]", description="Check the farm profit.")
    async def farm_profit(self, ctx, user: discord.Member = None):
        """Check the farm profit"""
        if user is None:
            user = ctx.author
        if Farm.read(user.id):
            farm_data = Farm.read(user.id)
            totalProfit = 0
            totalLoss = 0
            if len(farm_data['chickens']) == 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, you don't have any chickens.")
                return
            for chicken in farm_data['chickens']:
                totalProfit += (chicken['Egg_value'] * chicken['Happiness']) // 100
                totalLoss += chicken['Upkeep_multiplier']
            result = totalProfit - totalLoss
            if result > 0:
                await create_embed_without_title(ctx, f":white_check_mark: {user.display_name}, your farm is expected to generate a profit of **{result}** per hour :money_with_wings:.\n:chicken: Chicken upkeep: **{totalLoss}**\n:egg: Profit: **{totalProfit}**")
            elif result < 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, your farm is expected to generate a loss of **{result}** per hour :money_with_wings:.\n:chicken: Chicken upkeep: **{totalLoss}**\n:egg: Profit: **{totalProfit}**")
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, your farm is expected to generate neither profit nor loss.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, you don't have a farm.")

    async def trade_chickens(self, ctx, User: discord.Member, t):
        """Trade the chickens"""
        author_data = Farm.read(ctx.author.id)
        user_data = Farm.read(User.id)
        authorEmbed = self.get_usr_farm(ctx.author)
        userEmbed = self.get_usr_farm(User)
        trade_data = [author_data['chickens'], user_data['chickens']]
        members_data = [ctx.author, User]
        embeds = [authorEmbed, userEmbed]
        view_author = ChickenSelectView(chickens=trade_data, author=members_data, action="T", message=embeds, chicken_emoji=self.get_rarity_emoji, role="author", trade_data=t)
        view_user = ChickenSelectView(chickens=trade_data, author=members_data, action="T", message=embeds, chicken_emoji=self.get_rarity_emoji, role="user", trade_data=t, instance_bot = self.bot)
        await ctx.send(embed=authorEmbed, view=view_author)
        await ctx.send(embed=userEmbed, view=view_user)

    def get_usr_farm(self, User: discord.Member):
        """Get the user's farm"""
        if Farm.read(User.id):
            user_data = Farm.read(User.id)
            msg = discord.Embed(title=f":chicken: {user_data['farm_name']}\n:egg: **Eggs generated**: {user_data['eggs_generated']}", description="\n".join([f"{self.get_rarity_emoji(chicken['Name'])}  **{index + 1}.** **{chicken['Name']}** \n:partying_face: Happiness: **{chicken['Happiness']}%**" for index, chicken in enumerate(user_data['chickens'])]))
            return msg
        else:
            return None

    @commands.hybrid_command(name="chickenrarities", aliases=["cr"], usage="chickenRarities", description="Check the rarities of the chickens.")
    async def check_chicken_rarities(self, ctx):
        """Check the rarities of the chickens"""
        rarity_info = "\n".join([f"{self.get_rarity_emoji(rarity)} **{rarity}**: {round(rate/100, 4)}%" for rarity, rate in rollRates.items()])
        await create_embed_with_title(ctx, "Chicken Rarities:", rarity_info)

    async def devolve_chicken(self, chicken):
        """Devolve a chicken if its happiness is 0"""
        devolveChance = randint(1, 3)
        aux = chicken['Name'].split()[0]
        aux2 = chicken['Name'].split()[1]
        if aux in ChickenRarity.__members__ and aux != 'COMMON':
            if devolveChance == 1 and chicken['Happiness'] <= 0:
                rarity_list = list(ChickenRarity)
                index = rarity_list.index(ChickenRarity[aux])
                devolded_rarity = rarity_list[index - 1].name
                chicken['Name'] = f"{rarity_list[index - 1].name} {aux2}"
                chicken['Happiness'] = 100
                chicken['Egg_value'] = ChickenRarity[devolded_rarity].value
                chicken['Price'] = f"{175 * ChickenRarity[devolded_rarity].value} eggbux."
                chicken['Upkeep_multiplier'] = ChickenUpkeep[devolded_rarity].value
                return
        elif aux == 'COMMON' and chicken['Happiness'] <= 0 and devolveChance == 1:
            chicken['Name'] = f"DEAD {aux2}"
            chicken['Happiness'] = 0
            chicken['Egg_value'] = 0
            chicken['Price'] = "0 eggbux."
            chicken['Upkeep_multiplier'] = 0
            return
                
    async def drop_eggs(self):
        """Drop eggs periodically"""
        plrDict = {}
        for player in Farm.readAll():
            if len(player['chickens']) > 0:
                player_id = player['user_id']
                plrDict[player_id] = {
                    "chicken_list" : player['chickens'],
                    "totalEggs" : 0
                }
            for chicken in plrDict[player_id]['chicken_list']:
                if chicken['Name'].split()[0] == 'DEAD':
                    continue
                plrDict[player_id]['totalEggs'] += (chicken['Egg_value'] * chicken['Happiness']) // 100
                if chicken['Happiness'] > 0:
                    chicken['Happiness'] -= randint(0, 10)
                if chicken['Happiness'] < 0:
                    chicken['Happiness'] = 0
                if chicken['Happiness'] == 0:
                    await self.devolve_chicken(chicken)
        for player_id, player in plrDict.items():
            Farm.update(player_id, Farm.read(player_id)['farm_name'], player['chicken_list'], Farm.read(player_id)['eggs_generated'] + player['totalEggs'])
            if player['totalEggs'] > 0:
                Usuario.update(player_id, Usuario.read(player_id)['points'] + player['totalEggs'], Usuario.read(player_id)['roles'])
        print("Eggs dropped!")

    async def make_eggs_periodically(self):
        """Make eggs periodically"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await asyncio.sleep(3600)
            await self.drop_eggs()
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.reset_periodically())
        self.bot.loop.create_task(self.make_eggs_periodically())

async def setup(bot):
    await bot.add_cog(ChickenCommands(bot))



