from discord.ext import commands
from random import randint
from db.userDB import User
from tools.shared import create_embed_without_title, is_dev
from db.bankDB import Bank
from db.farmDB import Farm
from tools.chickenshared import ChickenMultiplier, ChickenRarity, determine_chicken_upkeep
from cogs.pointscommands.chickencmds import RollLimit
import tools.pointscore
import discord
import tools

class DevCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command("addPoints") 
    async def add_points(self, ctx, amount: int, user: discord.Member = None):
        """Add points to a user. If no user is specified, the author of the command will receive the points."""
        if user is None:
            user = ctx.author
        user_data = User.read(user.id)
        if user_data:
            if is_dev(ctx):
                User.update_points(user.id, user_data["points"] + amount)
                await create_embed_without_title(ctx, f"{user.display_name} received {amount} eggbux")
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} do not have permission to do this.")
        else:
            await create_embed_without_title(ctx, ":no_entry_sign: user not found in the database.")

    @commands.command("removePoints")
    async def remove_points(self, ctx, amount: int, user: discord.Member = None):
        """Remove points from a user. If no user is specified, the author of the command will lose the points."""
        if user is None:
            user = ctx.author
        user_data = User.read(user.id)
        if user_data:
            if is_dev(ctx):
                User.update_points(user.id, user_data["points"] - amount)
                await create_embed_without_title(ctx, f"{user.display_name} lost {amount} eggbux")
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} do not have permission to do this.")
        else:
            await create_embed_without_title(ctx, ":no_entry_sign: user not found in the database.")

    @commands.command("latency", aliases=["ping"])
    async def latency(self, ctx):
        """Check the bot's latency."""
        if is_dev(ctx):
            await create_embed_without_title(ctx, f":ping_pong: {round(self.bot.latency * 1000)}ms")

    @commands.command("deleteDB")
    async def delete_db(self, ctx,  user: discord.Member):
        """Delete a user from the database."""
        user = user.id
        if User.read(user):
            if is_dev(ctx):
                User.delete(user)
                await create_embed_without_title(ctx, f":warning: {user.display_name} has been deleted from the database.")
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} do not have permission to do this.")
        else:
                await create_embed_without_title(ctx, ":no_entry_sign: user not found in the database.")
            
    @commands.command()
    async def reset(self, ctx, user: discord.Member):
        """Reset a user from the database."""
        if is_dev(ctx) and User.read(user.id):
            if Bank.read(user.id):
                Bank.update(user.id, 0)
            User.update_all(user.id, 0, "")
            await create_embed_without_title(ctx, f"{user.display_name} has been reset.")
        else:
            await create_embed_without_title(ctx, ":no_entry_sign: You do not have permission to do this.")
    
    @commands.command("giveRolls")
    async def give_rolls(self, ctx, rolls : int, user: discord.Member):
        """Add more chicken roles to a user."""
        userObj = RollLimit.read(user.id)
        if is_dev(ctx):
            if userObj:
                userObj.current += rolls
                await create_embed_without_title(ctx, f"{user.display_name} received {rolls} rolls.")
            else:
                await create_embed_without_title(ctx, ":no_entry_sign: user didn't roll chickens in the market yet.")
        else:
            await create_embed_without_title(ctx, ":no_entry_sign: You do not have permission to do this.")

    @commands.command("checkbotServers", aliases=["cbs"])
    async def check_bot_servers(self, ctx):
        """Check the servers the bot is in."""
        if is_dev(ctx):
            servers = self.bot.guilds
            total_servers = len(servers)
            await create_embed_without_title(ctx, f"```The bot is currently in: {total_servers} servers```")
        else:
            await create_embed_without_title(ctx, ":no_entry_sign: You do not have permission to do this.")
    
    @commands.command("totalusers")
    async def total_users(self, ctx):
        """Check the total number of users in the database."""
        if is_dev(ctx):
            users = User.readAll()
            total_users = len(list(users))
            farms_created = Farm.readAll()
            total_farms = len(list(farms_created))
            banks_created = Bank.readAll()
            total_banks = len(list(banks_created))
            await create_embed_without_title(ctx, f"```The bot has {total_users} users, {total_farms} farms and {total_banks} banks accounts registered.```")
        else:
            await create_embed_without_title(ctx, ":no_entry_sign: You do not have permission to do this.")

    @commands.command("spawnChicken")
    async def spawn_chicken(self, ctx, user: discord.Member, rarity):
        """Add a chicken to a user."""
        if is_dev(ctx):
            rarity = rarity.upper()
            farm_data = Farm.read(user.id)
            if farm_data:
                chicken = {
                    "rarity": rarity,
                    "name": "Chicken",
                    "price": ChickenRarity[rarity].value * 150,
                    "happiness": randint(60, 100),
                    "egg_value" : ChickenMultiplier[rarity].value,
                    "eggs_generated": 0,
                    "upkeep_multiplier": 0,
                }
                chicken['upkeep_multiplier'] = determine_chicken_upkeep(chicken)
                farm_data['chickens'].append(chicken)
                Farm.update_chickens(user.id, farm_data['chickens'])
                await create_embed_without_title(ctx, f"{user.display_name} received a **{rarity}** chicken.")
    
    @commands.command("chickenlogs")
    async def circulation_chickens(self, ctx):
        """Check the total number of chickens in circulation."""
        rarity_dictionary = ChickenRarity.__members__.keys()
        rarity_dictionary = {rarity: 0 for rarity in rarity_dictionary}
        if is_dev(ctx):
            total_chickens = 0
            for farm in Farm.readAll():
                if 'chickens' in farm:
                    for chicken in farm['chickens']:
                        rarity_dictionary[chicken['rarity']] += 1
                        total_chickens += 1
            await create_embed_without_title(ctx, f"```Total chickens in circulation: {total_chickens}```\n Rarities: \n{' '.join([f'{rarity}: {count}' for rarity, count in rarity_dictionary.items()])}")
        else:
            await create_embed_without_title(ctx, ":no_entry_sign: You do not have permission to do this.")
    
    @commands.command("removeChicken")
    async def remove_chicken(self, ctx, user: discord.Member, index):
        farm_data = Farm.read(user.id)
        if farm_data:
            if is_dev(ctx):
                if index.upper() == "ALL":
                    farm_data['chickens'].clear()
                    Farm.update_chickens(user.id, farm_data['chickens'])
                    await create_embed_without_title(ctx, f"{user.display_name} lost all chickens.")
                    return
                index = int(index)
                farm_data['chickens'].pop(index)
                Farm.update_chickens(user.id, farm_data['chickens'])
                await create_embed_without_title(ctx, f"{user.display_name} lost a chicken.")
            else:
                await create_embed_without_title(ctx, ":no_entry_sign: You do not have permission to do this.")
    
    @commands.command(name="purge")
    async def purge(self, ctx, amount: int):
        """Deletes a certain amount of messages."""
        if is_dev(ctx):
            if amount > 0 and amount <= 25:
                await ctx.channel.purge(limit=amount + 1)
    
    @commands.command(name="devMode")
    async def developer_mode(self, ctx):
        """Activates the developer mode in the bot."""
        if is_dev(ctx):
            tools.pointscore.dev_mode = not tools.pointscore.dev_mode
            await create_embed_without_title(ctx, f":warning: Developer mode is now {'enabled' if tools.pointscore.dev_mode else 'disabled'}.")

async def setup(bot):
    await bot.add_cog(DevCommands(bot))