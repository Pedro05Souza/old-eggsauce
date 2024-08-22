"""
This file contains the developer commands for the bot.
"""

from discord.ext import commands
from db.userDB import User
from tools.shared import make_embed_object, send_bot_embed, is_dev, retrieve_threads
from db.bankDB import Bank
from db.farmDB import Farm
from db.MarketDB import Market
from tools.chickens.chickenshared import create_chicken
from tools.chickens.chickeninfo import ChickenRarity
from tools.chickens.chickenhandlers import RollLimit
from tools.cache.init import cache_initiator
from .. import botcore
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
                await send_bot_embed(ctx, description=f"{user.display_name} received {amount} eggbux")
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} do not have permission to do this.")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: user not found in the database.")

    @commands.command("removePoints")
    async def remove_points(self, ctx, amount: int, user: discord.Member = None):
        """Remove points from a user. If no user is specified, the author of the command will lose the points."""
        if user is None:
            user = ctx.author
        user_data = User.read(user.id)
        if user_data:
            if is_dev(ctx):
                User.update_points(user.id, user_data["points"] - amount)
                await send_bot_embed(ctx, description=f"{user.display_name} lost {amount} eggbux")
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} do not have permission to do this.")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: user not found in the database.")

    @commands.command("latency", aliases=["ping"])
    async def latency(self, ctx):
        """Check the bot's latency."""
        if is_dev(ctx):
            await send_bot_embed(ctx, description=f":ping_pong: {round(self.bot.latency * 1000)}ms")

    @commands.command("deleteDB")
    async def delete_db(self, ctx,  user: discord.Member):
        """Delete a user from the database."""
        user = user.id
        if User.read(user):
            if is_dev(ctx):
                User.delete(user)
                await send_bot_embed(ctx, description=f":warning: {user.display_name} has been deleted from the database.")
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} do not have permission to do this.")
        else:
                await send_bot_embed(ctx, description=":no_entry_sign: user not found in the database.")
            
    @commands.command()
    async def reset(self, ctx, user: discord.Member):
        """Reset a user from the database."""
        if is_dev(ctx) and User.read(user.id):
            if Bank.read(user.id):
                Bank.update(user.id, 0)
            User.update_all(user.id, 0, "")
            await send_bot_embed(ctx, description=f"{user.display_name} has been reset.")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")
    
    @commands.command("giveRolls")
    async def give_rolls(self, ctx, rolls : int, user: discord.Member):
        """Add more chicken roles to a user."""
        userObj = RollLimit.read(user.id)
        if is_dev(ctx):
            if userObj:
                userObj.current += rolls
                await send_bot_embed(ctx, description=f"{user.display_name} received {rolls} rolls.")
            else:
                await send_bot_embed(ctx, description=":no_entry_sign: user didn't roll chickens in the market yet.")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")

    @commands.command("checkbotServers", aliases=["cbs"])
    async def check_bot_servers(self, ctx):
        """Check the servers the bot is in."""
        if is_dev(ctx):
            servers = self.bot.guilds
            total_servers = len(servers)
            await send_bot_embed(ctx, description=f"```The bot is currently in: {total_servers} servers```")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")
    
    @commands.command("totalusers")
    async def total_users(self, ctx):
        """Check the total number of users in the database."""
        if is_dev(ctx):
            total_users = User.count_users()
            await send_bot_embed(ctx, description=f"```Total users in the database: {total_users}```")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")

    @commands.command("spawnChicken")
    async def spawn_chicken(self, ctx, user: discord.Member, rarity):
        """Add a chicken to a user."""
        if is_dev(ctx):
            rarity = rarity.upper()
            farm_data = Farm.read(user.id)
            if farm_data:
                chicken = await create_chicken(rarity, "dev")
                if not chicken:
                    await send_bot_embed(ctx, description=":no_entry_sign: Invalid rarity.")
                    return
                farm_data['chickens'].append(chicken)
                Farm.update(user.id, chickens=farm_data['chickens'])
                await send_bot_embed(ctx, description=f"{user.display_name} received a **{rarity}** chicken.")
    
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
            await send_bot_embed(ctx, description=f"```Total chickens in circulation: {total_chickens}```\n Rarities: \n{' '.join([f'{rarity}: {count}' for rarity, count in rarity_dictionary.items()])}")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")
    
    @commands.command("removeChicken")
    async def remove_chicken(self, ctx, user: discord.Member, index):
        farm_data = Farm.read(user.id)
        if farm_data:
            if is_dev(ctx):
                if index.upper() == "ALL":
                    farm_data['chickens'].clear()
                    Farm.update(user.id, chickens=farm_data['chickens'])
                    await send_bot_embed(ctx, description=f"{user.display_name} lost all chickens.")
                    return
                index = int(index)
                farm_data['chickens'].pop(index)
                Farm.update(user.id, chickens=farm_data['chickens'])
                await send_bot_embed(ctx, description=f"{user.display_name} lost a chicken.")
            else:
                await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")
    
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
            await send_bot_embed(ctx, description=f":warning: Developer mode is now {'enabled' if tools.pointscore.dev_mode else 'disabled'}.")

    @commands.command(name="mm")
    async def monitor_mode(self, ctx):
        """Activates the monitor mode in the bot."""
        if is_dev(ctx):
            botcore.monitor_mode = not botcore.monitor_mode
            print("Monitor mode is now: ", botcore.monitor_mode)
    
    @commands.command(name="marketLogs")
    async def market_logs(self, ctx):
     """Check the total number of active offers in the market."""
     if is_dev(ctx):
        total_offers = Market.count_all_offers()
        await send_bot_embed(ctx, description=f"```Total active offers in the player market: {total_offers}```")
     else:
        await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")
    
    @commands.command(name="reloadBot")
    async def reload_cog(self, ctx, folder, cog_name):
     """Reload a cog."""
     folders = {"p": "pointscommands", "c": "chickenscommands"}
     if is_dev(ctx):
        if folder not in folders:
            cog_full_name = f"cogs.{cog_name}"
        else:
            cog_full_name = f"cogs.pointscommands/{folders[folder]}/{cog_name}"
        if cog_full_name in self.bot.extensions:
            try:
                await self.bot.reload_extension(cog_full_name)
                await send_bot_embed(ctx, description=f":warning: {cog_name} has been reloaded.")
            except Exception as e:
                await send_bot_embed(ctx, description=f":no_entry_sign: Failed to reload {cog_name}. Error: {e}")
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {cog_name} is not loaded.")
     else:
        await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")

    @commands.command(name="unloadBot")
    async def unload_cog(self, ctx, cog_name):
        """Unload a cog."""
        if is_dev(ctx):
            cog_full_name = f"cogs.pointscommands.{cog_name}"
            if cog_full_name in self.bot.extensions:
                try:
                    await self.bot.unload_extension(cog_full_name)
                    await send_bot_embed(ctx, description=f":warning: {cog_name} has been unloaded.")
                except Exception as e:
                    await send_bot_embed(ctx, description=f":no_entry_sign: Failed to unload {cog_name}. Error: {e}")
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: {cog_name} is not loaded.")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")

    @commands.command(name="devpanel")
    async def developer_panel(self, ctx):
        if is_dev(ctx):
            user, guild = await cache_initiator.get_memory_usage()
            embed_obj = await make_embed_object(title="⚙️ Developer Panel")
            embed_obj.add_field(name="🔧 Cache Memory Usage:", value=f"User Cache: {user} bytes\nGuild Cache: {guild} bytes")
            embed_obj.add_field(name="🧰 Current active threads:", value=f"{retrieve_threads()}")
            await ctx.send(embed=embed_obj)
            
async def setup(bot):
    await bot.add_cog(DevCommands(bot))