from discord.ext import commands
from db.botConfigDB import BotConfig
from tools.sharedmethods import create_embed_with_title, create_embed_without_title, make_embed_object
from db.bankDB import Bank
from db.userDB import User
from tools.pricing import pricing, refund
from db.botConfigDB import BotConfig
import math
import time
import discord
class PointsConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_time = {}
        self.init_time = math.ceil(time.time())

    @commands.hybrid_command(name="modulestatus", aliases=["status"], brief="Check the status of ptscmds.", usage="points_toggle", description="Check if the points commands are enabled or disabled in the server.")
    async def points_status(self, ctx):
        """Check the current module active in the server"""
        modules = {
            "T": "Total",
            "F": "Friendly",
            "H": "Hostile",
            "N": "None"
        }
        current_module = BotConfig.read(ctx.guild.id)['toggled_modules']
        await create_embed_without_title(ctx, f":warning: Points commands are currently set to: **{modules[current_module]}**")

    async def update_points(self, user: discord.Member):
        """Updates the points of the user every 10 seconds."""
        userId = user.id
        if userId in self.join_time.keys():
            print("User in join_time")
            add_points = (math.ceil(time.time()) - self.join_time[userId]) // 10
            total_points = User.read(userId)["points"] + add_points
            User.update_points(userId, total_points)
            self.join_time[userId] = math.ceil(time.time())
            return total_points
        
        if userId not in self.join_time.keys() and user.voice:
           print("User not in join_time")
           add_points = (math.ceil(time.time()) - self.init_time) // 10
           total_points = User.read(userId)["points"] + add_points
           User.update_points(userId, total_points)
           self.join_time[userId] = math.ceil(time.time())
           return total_points

    async def count_points(self, user: discord.Member):
        """Counts the points of the user every time he enters a voice channel."""
        userId = user.id
        if user.bot:
            return
        if userId not in self.join_time.keys():
            self.join_time[userId] = math.ceil(time.time())
        else:
            return

    def automatic_register(self, user: discord.Member):
        """Automatically registers the user in the database."""
        if user.read(user.id) and user.bot:
            return
        else:
            user.create(user.id, 0)
            print(f"User created: {user.name}")

    @commands.hybrid_command(name="register", aliases=["reg"], brief="Registers the user in the database.", usage="register", description="Registers the user in the database.")
    async def register(self, ctx):
        """Registers the user in the database."""
        if User.read(ctx.author.id):
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} is already registered.")
        else:
            User.create(ctx.author.id, 0)
            await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name} has been registered.")
 
    @commands.hybrid_command(name="points", aliases=["pts", "eggbux", "p"], brief="Shows the amount of points the user has.", usage="points OPTIONAL [user]", description="Shows the amount of points a usr has. If not usr, shows author's points.")
    @pricing()
    async def points(self, ctx, user: discord.Member = None):
        """Shows the amount of points the user has."""
        if user is None:
            user = ctx.author
        user_data = User.read(user.id)
        if user_data and isinstance(user_data, dict) and "points" in user_data:
            await self.update_user_points(user)
            if Bank.read(user.id):
                msg = await make_embed_object(title=f":egg: {user.display_name}'s eggbux", description=f":briefcase: Wallet: {user_data['points']}\n :bank: Bank: {Bank.read(user.id)['bank']}")
                msg.set_thumbnail(url=user.display_avatar)
                await ctx.send(embed=msg)
            else:
                msg = await make_embed_object(title=f":egg: {user.display_name}'s eggbux", description=f":briefcase: Wallet: {user_data['points']}")
                msg.set_thumbnail(url=user.display_avatar)
                await ctx.send(embed=msg)
        else:   
            await create_embed_without_title(ctx, f"{user.display_name} has no eggbux :cry:")

    async def update_user_points(self, user: discord.Member):
        """Updates the user's points."""
        user_data = User.read(user.id)
        if user_data:
            points = await self.update_points(user)
            if points is not None:
                user_data['points'] = points
            last_title_drop = time.time() - user_data["salary_time"]
            hours_passed = last_title_drop // 3600 if last_title_drop <= 3600 else 5
            salary = self.salary_role(user)
            if hours_passed >= 1:
                User.update_points(user.id, user_data["points"] + salary * hours_passed)
                User.update_salary_time(user.id)
            User.update_points(user.id, user_data["points"])

    @commands.hybrid_command(name="buytitles", aliases=["titles"], brief="Buy custom titles.", usage="Buytitles", description="Buy custom titles that comes with different salaries every 30 minutes.")
    @pricing()
    async def points_Titles(self, ctx):
        end_time = time.time() + 60
        roles = {
            "T" : "Egg Novice",
            "L" : "Egg Apprentice",
            "M" : "Egg wizard",
            "H" : "Egg King",
        }

        rolePrices = {
            "T" : 600,
            "L" : 800,
            "M" : 1200,
            "H" : 1500
        }
        message = await create_embed_with_title(ctx, "Custom Titles:", f":poop: **{roles['T']}**\nIncome: 25 eggbux. :money_bag: \nPrice: 600 eggbux.\n\n :farmer: **{roles['L']}** \nIncome: 50 eggbux. :money_bag:\n Price: 800 eggbux. \n\n:man_mage: **{roles['M']}** \n Income: 75 eggbux. :money_bag:\n Price: 1200 eggbux. \n\n:crown: **{roles['H']}** \n Income: 100 eggbux. :money_bag:\n Price: 1500 eggbux. \n**The titles are bought sequentially.**\nReact with ✅ to buy a title.")
        await message.add_reaction("✅")
        while True:
            actual_time = end_time - time.time()
            if actual_time <= 0:
                await message.clear_reactions()
                break
            check = lambda reaction, user: reaction.emoji == "✅" and reaction.message.id == message.id
            reaction, user = await self.bot.wait_for("reaction_add", check=check)
            if reaction.emoji == "✅":
                if User.read(user.id)["roles"] == "":
                    await self.buy_roles(ctx, user, rolePrices["T"], "T", roles["T"])
                elif User.read(user.id)["roles"][-1] == "T":
                    await self.buy_roles(ctx, user, rolePrices["L"], "L", roles["L"])
                elif User.read(user.id)["roles"][-1] == "L":
                    await self.buy_roles(ctx, user, rolePrices["M"], "M", roles["M"])
                elif User.read(user.id)["roles"][-1] == "M":
                    await self.buy_roles(ctx, user, rolePrices["H"], "H", roles["H"])

    async def buy_roles(self, ctx, user: discord.Member, roleValue, roleChar, roleName):
        """Buy roles."""
        if User.read(user.id)["points"] >= roleValue and roleChar not in User.read(user.id)["roles"]:
            User.update_all(user.id, User.read(user.id)["points"] - roleValue, User.read(user.id)["roles"] + roleChar)
            await create_embed_without_title(ctx, f":white_check_mark: {user.display_name} has bought the role **{roleName}**.")
        elif User.read(user.id)["points"] < roleValue:
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, you don't have enough eggbux to buy the role **{roleName}**.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} already has the role **{roleName}**.")

    def salary_role(self, user: discord.Member):
        """Returns the salary of a user based on their roles."""
        salarios = {
            "T": 25,
            "L": 50,
            "M": 75,
            "H": 100
        }
        user_data = User.read(user.id)
        if user_data:
            return salarios[user_data["roles"][-1]]
        else:
            return 0
        
    def get_user_title(self, user: discord.Member):
        userRoles = {
            "T" : "Egg Novice",
            "L" : "Egg Apprentice",
            "M" : "Egg wizard",
            "H" : "Egg King",
        }
        user_data = User.read(user.id)
        if user_data:
            if user_data["roles"] == "":
                return "Unemployed"
            return userRoles[user_data["roles"][-1]]

    @commands.hybrid_command(name="salary", aliases=["sal"], brief="Check the salary of a user.", usage="salary OPTIONAL [user]", description="Check the salary of a user. If not user, shows author's salary.")
    @pricing()
    async def salary(self, ctx, user: discord.Member = None):
        """Check the salary of a user."""
        if user is None:
            user = ctx.author
        user_data = User.read(user.id)
        if user_data:
            if user_data["roles"] != "":
                await create_embed_without_title(ctx, f":moneybag: {user.display_name} has the title of **{self.get_user_title(user)}** and earns {self.salary_role(user)} eggbux..")
                return   
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} doesn't have a title.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} isn't registered in the database.")
            await refund(ctx.author, ctx)
            
    @commands.Cog.listener()
    async def on_voice_state_update(self, user: discord.Member, before, after):
        """Listens to the voice state update event."""
        if not BotConfig.read(user.guild.id)['toggled_modules'] == "N":
            if user.bot:
                return
            if user.read(user.id) and before.channel is None and after.channel is not None:
                await self.count_points(user)
            elif not User.read(user.id) and before.channel is None and after.channel is not None:
                self.automatic_register(user)
                await self.count_points(user)
            elif User.read(user.id) and before.channel is not None and after.channel is None:
                await self.update_points(user)
            elif not User.read(user.id) and before.channel is not None and after.channel is None:
                self.automatic_register(user)
                await self.update_points(user)

async def setup(bot):
    await bot.add_cog(PointsConfig(bot))