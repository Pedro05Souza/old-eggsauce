"""
This file contains the developer commands for the bot.
"""
from discord.ext import commands
from db.userdb import User
from tools.shared import make_embed_object, send_bot_embed, is_dev, retrieve_threads
from db.bankdb import Bank
from db.farmdb import Farm
from db.marketdb import Market
from tools.chickens.chickenshared import create_chicken
from tools.listeners import listener_manager
from tools.cache import cache_initiator
from discord.ext.commands import Context
import psutil
import discord
import logging
logger = logging.getLogger('botcore')

class DevCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command("addPoints") 
    async def add_points(self, ctx: Context, amount: int, user: discord.Member = None) -> None:
        """
        Adds points to a user.

        Args:
            amount (int): The amount of points to add.
            user (discord.Member): The user to add the points to. Defaults to None. If None, the author of the command will receive the points.

        Returns:
            None
        """
        if user is None:
            user = ctx.author
        user_data = await User.read(user.id)
        if user_data:
            if is_dev(ctx):
                await User.update_points(user.id, user_data["points"] + amount)
                await send_bot_embed(ctx, description=f"{user.display_name} received {amount} eggbux")
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} do not have permission to do this.")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: user not found in the database.")

    @commands.command("removePoints")
    async def remove_points(self, ctx: Context, amount: int, user: discord.Member = None) -> None:
        """
        Removes points from a user.

        Args:
            amount (int): The amount of points to remove.
            user (discord.Member): The user to remove the points from. Defaults to None. If None, the author of the command will lose the points.

        Returns:
            None
        """
        if user is None:
            user = ctx.author
        user_data = await User.read(user.id)
        if user_data:
            if is_dev(ctx):
                await User.update_points(user.id, user_data["points"] - amount)
                await send_bot_embed(ctx, description=f"{user.display_name} lost {amount} eggbux")
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} do not have permission to do this.")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: user not found in the database.")

    @commands.command("latency", aliases=["ping"])
    async def latency(self, ctx: Context) -> None:
        """
        Check the bot's latency.

        Args:
            ctx (Context): The context of the command.

        Returns:
            None
        """
        if is_dev(ctx):
            await send_bot_embed(ctx, description=f":ping_pong: {round(self.bot.latency * 1000)}ms")

    @commands.command("deleteDB")
    async def delete_db(self, ctx: Context, user: discord.Member) -> None:
        """
        Delete an user from the database.

        Args:
            user (discord.Member): The user to delete from the database.

        Returns:
            None
        """
        if await User.read(user.id):
            if is_dev(ctx):
                await User.delete(user.id)
                await Bank.delete(user.id)
                await Farm.delete(user.id)
                await Market.delete(user.id)
                await send_bot_embed(ctx, description=f":warning: {user.display_name} has been deleted from the database.")
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} do not have permission to do this.")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: user not found in the database.")
            
    @commands.command()
    async def reset(self, ctx: Context, user: discord.Member) -> None:
        """
        Resets an user from the database.

        Args:
            user (discord.Member): The user to reset from the database.
        
        Returns:
            None
        """
        if is_dev(ctx) and User.read(user.id):
            if await Bank.read(user.id):
                await Bank.update(user.id, 0)
            await User.update_all(user.id, 0, "")
            await send_bot_embed(ctx, description=f"{user.display_name} has been reset.")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")

    @commands.command("checkbotServers", aliases=["cbs"])
    async def check_bot_servers(self, ctx: Context) -> None:
        """
        Check the servers the bot is in.

        Args:
            ctx (Context): The context of the command.

        Returns:
            None
        """
        if is_dev(ctx):
            servers = self.bot.guilds
            total_servers = len(servers)
            await send_bot_embed(ctx, description=f"```The bot is currently in: {total_servers} servers```")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")
    
    @commands.command("totalusers")
    async def total_users(self, ctx: Context) -> None:
        """
        Check the total number of users in the database.

        Args:
            ctx (Context): The context of the command.

        Returns:
            None
        """
        if is_dev(ctx):
            total_users = await User.count_users()
            await send_bot_embed(ctx, description=f"```Total users in the database: {total_users}```")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")

    @commands.command("spawnChicken")
    async def spawn_chicken(self, ctx: Context, user: discord.Member, rarity: str) -> None:
        """
        Adds a chicken to an user's farm.

        Args:
            user (discord.Member): The user to add the chicken to.
            rarity (str): The rarity of the chicken.

        Returns:
            None
        """
        if is_dev(ctx):
            rarity = rarity.upper()
            farm_data = await Farm.read(user.id)
            if farm_data:
                chicken = await create_chicken(rarity, "dev")
                if not chicken:
                    await send_bot_embed(ctx, description=":no_entry_sign: Invalid rarity.")
                    return
                farm_data['chickens'].append(chicken)
                await Farm.update(user.id, chickens=farm_data['chickens'])
                await send_bot_embed(ctx, description=f"{user.display_name} received a **{rarity}** chicken.")
                              
    @commands.command(name="marketLogs")
    async def market_logs(self, ctx: Context) -> None:
     """
    Checks the total number of active offers in the market.

    Args:
        ctx (Context): The context of the command.

    Returns: 
        None
         
     """
     if is_dev(ctx):
        total_offers = await Market.count_all_offers()
        await send_bot_embed(ctx, description=f"```Total active offers in the player market: {total_offers}```")
     else:
        await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")
    
    @commands.command(name="devpanel")
    async def developer_panel(self, ctx: Context) -> None:
        """
        Check the developer panel. It shows the memory usage, active threads, CPU usage and memory usage.

        Args:
            ctx (Context): The context of the command.

        Returns:
            None
        """
        if is_dev(ctx):
            process = psutil.Process()
            cache = await cache_initiator.get_cache_memory_consuption()
            embed_obj = await make_embed_object(title="⚙️ Developer Panel")
            embed_obj.add_field(name="🔧 Cache Memory Usage:", value=f"{cache} bytes")
            embed_obj.add_field(name="🧰 Current active threads:", value=f"{retrieve_threads()}")
            embed_obj.add_field(name="📊 CPU Usage:", value=f"{process.cpu_percent()}%")
            embed_obj.add_field(name="🧠 Memory Usage:", value=f"{process.memory_info().rss / 1024 ** 2} MB")
            await ctx.send(embed=embed_obj)

    @commands.command(name="sync")
    async def sync(self, ctx: Context) -> None:
        """
        Sync the bot commands globally.

        Args:
            ctx (Context): The context of the command.

        Returns:
            None
        """
        if is_dev(ctx):
            await self.bot.tree.sync()
            await send_bot_embed(ctx, description=":warning: bot data has been synced.")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")

    @commands.command(name="givecorn")
    async def give_corn(self, ctx: Context, amount: int, user: discord.Member= None) -> None:
        """
        Gives corn to a user.

        Args:
            amount (int): The amount of corn to give.
            user (discord.Member): The user to give the corn to. Defaults to None. If None, the author of the command will receive the corn.
        
        Returns:
            None
        """
        if is_dev(ctx):
            user = ctx.author if user is None else user
            farm_data = await Farm.read(user.id)
            if farm_data:
                farm_data['corn'] = min(amount + farm_data['corn'], farm_data['corn_limit'])
                await Farm.update(user.id, corn=farm_data['corn'])
                await send_bot_embed(ctx, description=f"{user.display_name} received {amount} corn.")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")

    @commands.command(name="lastPurchase", aliases=["lp"])
    async def get_last_purchase(self, ctx: Context, user: discord.Member) -> None:
        """
        Check the last listener of an user.

        Args:
            user (discord.Member): The user to check the last listener.

        Returns:
            None
        """
        if is_dev(ctx):
            last_listener = await listener_manager.get_last_listener(user.id)
            if last_listener:
                await send_bot_embed(ctx, description=await listener_manager.return_listener_description(last_listener))     
            else:
                await send_bot_embed(ctx, description=":no_entry_sign: No listener found.")

    @commands.command(name="lastPurchases", aliases=["lps"])
    async def get_last_purchases(self, ctx: Context, user: discord.Member, n: int) -> None:
        """
        Check the last n listeners of an user.

        Args:
            user (discord.Member): The user to check the last listeners.
            n (int): The number of listeners to check.

        Returns:
            None
        """
        if is_dev(ctx):
            last_listeners = await listener_manager.get_n_last_listeners(user.id, n)
            if last_listeners:
                description = ""
                for listener in last_listeners:
                    description += await listener_manager.return_listener_description(listener)
                await send_bot_embed(ctx, description=description)
            else:
                await send_bot_embed(ctx, description=":no_entry_sign: No listener found.")

    @commands.command(name="changechickenupkeep" , aliases=["ccu"])
    async def change_chicken_upkeep(self, ctx: Context, new_upkeep: int, index: int, user: discord.Member):
        """
        Change the upkeep of a chicken.

        Args:
            ctx (Context): The context of the command.
            new_upkeep (float): The new upkeep of the chicken.
            index (int): The index of the chicken.
            user (discord.Member): The user to change the upkeep of the chicken.

        Returns:
            None
        """
        if is_dev(ctx):
            farm_data = await Farm.read(user.id)
            if farm_data:
                
                if new_upkeep < 0 or new_upkeep > 75:
                    await send_bot_embed(ctx, description=":no_entry_sign: Upkeep must be between 0 and .75.")
                    return
                
                new_upkeep = new_upkeep / 100
                index -= 1

                if index < 0 or index >= len(farm_data['chickens']):
                    await send_bot_embed(ctx, description=":no_entry_sign: Invalid index.")
                    return
                
                farm_data['chickens'][index]['upkeep_multiplier'] = new_upkeep
                await Farm.update(user.id, chickens=farm_data['chickens'])
                await send_bot_embed(ctx, description=f"{user.display_name}'s chicken upkeep has been changed.")
                
async def setup(bot):
    await bot.add_cog(DevCommands(bot))