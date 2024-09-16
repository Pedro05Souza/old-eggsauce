"""
This file contains the developer commands for the bot.
"""
import time
from discord.ext import commands
from db.userdb import User
from tools.shared import make_embed_object, send_bot_embed, is_dev, retrieve_threads
from db.bankdb import Bank
from db.farmdb import Farm
from db.marketdb import Market
from db.botconfigdb import BotConfig
from tools.chickens.chickenshared import create_chicken
from tools.chickens.chickeninfo import ChickenRarity
from tools.chickens.chickenhandlers import RollLimit
from tools.listeners import listener_manager
from tools.cache import cache_initiator
from . import botcore
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
        if User.read(user.id):
            if is_dev(ctx):
                User.delete(user.id)
                Bank.delete(user.id)
                Farm.delete(user.id)
                Market.delete(user.id)
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
            if Bank.read(user.id):
                Bank.update(user.id, 0)
            User.update_all(user.id, 0, "")
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
            total_users = User.count_users()
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
            farm_data = Farm.read(user.id)
            if farm_data:
                chicken = await create_chicken(rarity, "dev")
                if not chicken:
                    await send_bot_embed(ctx, description=":no_entry_sign: Invalid rarity.")
                    return
                farm_data['chickens'].append(chicken)
                Farm.update(user.id, chickens=farm_data['chickens'])
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
        total_offers = Market.count_all_offers()
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
            user, guild = await cache_initiator.get_memory_usage()
            embed_obj = await make_embed_object(title="⚙️ Developer Panel")
            embed_obj.add_field(name="🔧 Cache Memory Usage:", value=f"User Cache: {user} bytes\nGuild Cache: {guild} bytes")
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
            farm_data = Farm.read(user.id)
            if farm_data:
                farm_data['corn'] = min(amount + farm_data['corn'], farm_data['corn_limit'])
                Farm.update(user.id, corn=farm_data['corn'])
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

    @commands.command(name="randomPurchases", aliases=["rps"])
    async def get_random_purchases(self, ctx: Context, n: int) -> None:
        """
        Check the random n listeners.

        Args:
            n (int): The number of listeners to check.

        Returns:
            None
        """
        if is_dev(ctx):
            random_listeners = await listener_manager.get_random_n_listeners(n)
            random_listeners = random_listeners[0]
            if random_listeners:
                description = ""
                for listener in random_listeners:
                    description += await listener_manager.return_listener_description(listener)
                await send_bot_embed(ctx, description=description)
            else:
                await send_bot_embed(ctx, description=":no_entry_sign: No listener found.")

    # @commands.command(name="announce")
    # async def announcements_message(self, ctx: Context) -> None:
    #     guild = ctx.guild
    #     patreon_id = 1277369929800355918
    #     donator_id = 1277390615738449961
    #     patreon_role = guild.get_role(patreon_id)
    #     donator_role = guild.get_role(donator_id)
    #     if is_dev(ctx):
    #         title = "📢 Hey, welcome to the community!\n"
    #         intro = "We are happy to welcome you to this server. In this server you will find out about new updates, events performed on the bot and much more."
    #         about_me = "I'm a bot that was created and developed for the purpose of entertainment and fun. I have so many commands i forgot the count of them, this is one of the problems of having way too many abilities."
    #         paid_features = "I currently don't have any paid features. Everything is **free** to use. But if you want to support me, you can always donate to my creator. Here is the link of the patreon: [Patreon](https://www.patreon.com/eggsaucebot)"
    #         bug_report = "Since the bot is still in development, there might be some bugs. If you find any, please report them to the creator of the bot."
    #         rewards = f"As a reward for a **patreon membership**, you will receive {patreon_role.mention} role. This role will give you access to a special channel where you can get exclusive acess to new features and updates. As for a **one-time donation**, you will receive {donator_role.mention} role and a special badge in the bot. As for **bug reports**, you will receive **in-game** prizes for your help, the prizes will vary depending on the bug."
    #         embed_obj = await make_embed_object(title=title)
    #         embed_obj.add_field(name="👋 Introduction:", value=intro, inline=False)
    #         embed_obj.add_field(name="🤖 About me:", value=about_me, inline=False)
    #         embed_obj.add_field(name="💰 Paid features:", value=paid_features, inline=False)
    #         embed_obj.add_field(name="🐞 Bug report:", value=bug_report, inline=False)
    #         embed_obj.add_field(name="🎁 Rewards:", value=rewards, inline=False)
    #         embed_obj.set_image(url="https://cdn.discordapp.com/attachments/755512000272007348/1277377900848484472/image.png?ex=66ccf260&is=66cba0e0&hm=d3da7fa594a155238e2342200cf1b245eef8d7efae7c63ae7305d579545b18d9&")
    #         await ctx.send(embed=embed_obj)
            
async def setup(bot):
    await bot.add_cog(DevCommands(bot))