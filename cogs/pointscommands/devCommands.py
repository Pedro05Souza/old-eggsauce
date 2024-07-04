import os
import ast
from discord.ext import commands
import discord
from db.userDB import Usuario
from tools.embed import create_embed_without_title
from db.bankDB import Bank
from dotenv import load_dotenv
from db.farmDB import Farm
from cogs.pointscommands.chickenCommands import RollLimit

class DevCommands(commands.Cog):
    def __init__(self, bot):
        load_dotenv()
        self.bot = bot
        self.devs = os.getenv("DEVS").split(",")
    
    @commands.command("addPoints") 
    async def add_points(self, ctx, amount: int, User: discord.Member = None):
        """Add points to a user. If no user is specified, the author of the command will receive the points."""
        if User is None:
            User = ctx.author
            if str(User.id) in self.devs:
                Usuario.update(User.id, Usuario.read(User.id)["points"] + amount, Usuario.read(User.id)["roles"])
                await create_embed_without_title(ctx, f"{User.display_name} received {amount} eggbux")
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} do not have permission to do this.")
        else:
            if Usuario.read(User.id):
                if str(ctx.author.id) in self.devs:
                    Usuario.update(User.id, Usuario.read(User.id)["points"] + amount, Usuario.read(User.id)["roles"])
                    await create_embed_without_title(ctx, f"{User.display_name} received {amount} eggbux")
                else:
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} do not have permission to do this.")
            else:
                await create_embed_without_title(ctx, ":no_entry_sign: User not found in the database.")

    @commands.command("removePoints")
    async def remove_points(self, ctx, amount: int, User: discord.Member = None):
        """Remove points from a user. If no user is specified, the author of the command will lose the points."""
        if User is None:
            User = ctx.author
            if str(User.id) in self.devs:
                Usuario.update(User.id, Usuario.read(User.id)["points"] - amount, Usuario.read(User.id)["roles"])
                await create_embed_without_title(ctx, f"{User.display_name} lost {amount} eggbux")
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} do not have permission to do this.")
        else:
            if Usuario.read(User.id):
                if str(ctx.author.id) in self.devs:
                    Usuario.update(User.id, Usuario.read(User.id)["points"] - amount, Usuario.read(User.id)["roles"])
                    await create_embed_without_title(ctx, f"{User.display_name} lost {amount} eggbux")
                else:
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} do not have permission to do this.")
            else:
                await create_embed_without_title(ctx, ":no_entry_sign: User not found in the database.")

    @commands.command("latency", aliases=["ping"])
    async def latency(self, ctx):
        """Check the bot's latency."""
        if str(ctx.author.id) in self.devs:
            await create_embed_without_title(ctx, f":ping_pong: {round(self.bot.latency * 1000)}ms")

    @commands.command("deleteDB")
    async def delete_db(self, ctx,  User: discord.Member):
        """Delete a user from the database."""
        User = User.id
        if Usuario.read(User):
            if str(ctx.author.id) in self.devs:
                Usuario.delete(User)
                await create_embed_without_title(ctx, f":warning: {User.display_name} has been deleted from the database.")
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} do not have permission to do this.")
        else:
                await create_embed_without_title(ctx, ":no_entry_sign: User not found in the database.")
            
    @commands.command()
    async def reset(self, ctx, User: discord.Member):
        """Reset a user from the database."""
        if str(User.id) in self.devs and Usuario.read(User.id):
            if Bank.read(User.id):
                Bank.update(User.id, 0)
            Usuario.update(User.id, 0, "")
            await create_embed_without_title(ctx, f"{User.display_name} has been reset.")
        else:
            await create_embed_without_title(ctx, ":no_entry_sign: You do not have permission to do this.")
    
    @commands.command("giveRolls")
    async def give_rolls(self, ctx, rolls : int, User: discord.Member):
        """Add more chicken roles to a user."""
        userObj = RollLimit.read(User.id)
        if str(ctx.author.id) in self.devs:
            if userObj:
                userObj.current += rolls
                await create_embed_without_title(ctx, f"{User.display_name} received {rolls} rolls.")
            else:
                await create_embed_without_title(ctx, ":no_entry_sign: User didn't roll chickens in the market yet.")
        else:
            await create_embed_without_title(ctx, ":no_entry_sign: You do not have permission to do this.")

    @commands.command("checkbotServers", aliases=["cbs"])
    async def check_bot_servers(self, ctx):
        """Check the servers the bot is in."""
        if str(ctx.author.id) in self.devs:
            servers = self.bot.guilds
            total_servers = len(servers)

            await create_embed_without_title(ctx, f"```The bot is currently in: {total_servers} servers```")
        else:
            await create_embed_without_title(ctx, ":no_entry_sign: You do not have permission to do this.")
    
    @commands.command("totalUsers")
    async def total_users(self, ctx):
        """Check the total number of users in the database."""
        if str(ctx.author.id) in self.devs:
            users = Usuario.readAll()
            total_users = len(list(users))
            farms_created = Farm.readAll()
            total_farms = len(list(farms_created))
            banks_created = Bank.readAll()
            total_banks = len(list(banks_created))
            await create_embed_without_title(ctx, f"```The bot has {total_users} users, {total_farms} farms and {total_banks} banks accounts registered.```")
        else:
            await create_embed_without_title(ctx, ":no_entry_sign: You do not have permission to do this.")
    

async def setup(bot):
    await bot.add_cog(DevCommands(bot))

    