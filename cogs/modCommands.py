import os
import discord
from discord.ext import commands
from db.userDB import Usuario
from db.channelDB import ChannelDB
from dotenv import load_dotenv

# This ModCommands class is specifically for testing purposes;
class ModCommands(commands.Cog):
    
    def __init__(self, bot):
        load_dotenv()
        self.devs = os.getenv("DEVS").split(",")
        self.bot = bot

    @commands.command() 
    async def addPoints(self, ctx, amount: int, User: discord.Member = None):
        """Add points to a user. If no user is specified, the author of the command will receive the points."""
        if User is None:
            User = ctx.author
            if str(User.id) in self.devs:
                Usuario.update(User.id, Usuario.read(User.id)["points"] + amount, Usuario.read(User.id)["roles"])
                await ctx.send(f"{User.mention} received {amount} eggbux")
            else:
                await ctx.send("You do not have permission to do this.")
        else:
            if Usuario.read(User.id):
                if str(ctx.author.id) in self.devs:
                    Usuario.update(User.id, Usuario.read(User.id)["points"] + amount, Usuario.read(User.id)["roles"])
                    await ctx.send(f"{User.mention} received {amount} eggbux")
                else:
                    await ctx.send("You do not have permission to do this.")
            else:
                await ctx.send("User not found in the database.")

    @commands.command()
    async def removePoints(self, ctx, amount: int, User: discord.Member = None):
        """Remove points from a user. If no user is specified, the author of the command will lose the points."""
        if User is None:
            User = ctx.author
            if str(User.id) in self.devs:
                Usuario.update(User.id, Usuario.read(User.id)["points"] - amount, Usuario.read(User.id)["roles"])
                await ctx.send(f"{User.mention} lost {amount} eggbux.")
            else:
                await ctx.send("You do not have permission to do this.")
        else:
            if Usuario.read(User.id):
                if str(ctx.author.id) in self.devs:
                    Usuario.update(User.id, Usuario.read(User.id)["points"] - amount, Usuario.read(User.id)["roles"])
                    await ctx.send(f"{User.mention} perdeu {amount} eggbux")
                else:
                    await ctx.send("You do not have permission to do this.")
            else:
                await ctx.send("User not found in the database.")

    @commands.command()
    async def deleteDB(self, ctx,  User: discord.Member):
        """Delete a user from the database."""
        User = User.id
        if Usuario.read(User):
            if str(ctx.author.id) in self.devs:
                Usuario.delete(User)
                await ctx.send(f"{User} has been deleted from the database.")
            else:
                await ctx.send("You do not have permission to do this.")
        else:
            await ctx.send(f"{User} not found in the database.")

    @commands.command()
    async def removeRole(self, ctx ,User:discord.Member, role: str):
        """Remove one one of the custom roles created by the bot."""
        possibleRoles = {"T": "Low wage worker", "B" : "Peasant", "M" : "Brokie who thinks they are rich", "A" : "Magnate"}
        if str(ctx.author.id) in self.devs:
            user_data = Usuario.read(User.id)
            if user_data:
                if len(user_data["roles"]) > 0 and role in possibleRoles.keys():
                    if role in user_data["roles"]:
                        roles = Usuario.read(User.id)["roles"]
                        roles = roles.replace(role, "")
                        roleRemove = discord.utils.get(ctx.guild.roles, name=possibleRoles[role])
                        if roleRemove:
                            await User.remove_roles(roleRemove)
                            Usuario.update(User.id, Usuario.read(User.id)["points"], roles)
                            await ctx.send(f"{User.mention} lost the role {possibleRoles[role]}.")
                    else:
                        await ctx.send(f"{User.mention} lost the role {role}")
            else:
                await ctx.send(f"{User.mention} is not registered in the database.")
        else:
            await ctx.send("You do not have permission to do this.")
            
    @commands.command()
    async def removeAllRoles(self, ctx, User: discord.Member):
        """Remove all custom roles created by the bot."""
        if str(ctx.author.id) in self.devs:
            user_data = Usuario.read(User.id)
            if user_data:
                roles = user_data["roles"]
                for role in roles:
                    roleRemove = discord.utils.get(ctx.guild.roles, name=role)
                    if roleRemove:
                        await User.remove_roles(roleRemove)
                Usuario.update(User.id, Usuario.read(User.id)["points"], "")
                await ctx.send(f"{User.mention} lost all custom roles.")
            else:
                await ctx.send(f"{User.mention} is not registered in the database!")
        else:
            await ctx.send("You do not have permission to do this.")

    @commands.command()
    async def setChannel(self, ctx):
        if ctx.author.guild_permissions.administrator or str(ctx.author.id in self.devs):
            if ChannelDB.read(server_id=ctx.guild.id):
                ChannelDB.update(ctx.channel.id)
                print(f"Channel updated for guild {ctx.guild.name}")
                await ctx.send("Commands channel has been updated.")
            else:
                ChannelDB.create(ctx.guild.id, ctx.channel.id)
                print(f"New channel registered for guild {ctx.guild.name}")
                await ctx.send("Commands channel has been set.")
        else:
            await ctx.send(f"You do not have permission to do this.")


    # Event listeners; these functions are called when the event they are listening for is triggered

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            roles = ""
            role_order = ["Low wage worker", "Peasant", "Brokie who thinks they are rich", "Magnate"]
            role_letters = {"Low wage worker": "T", "Peasant": "B", "Brokie who thinks they are rich": "M", "Magnate": "A"}
            lost_role = None
            for role in before.roles:
                if role not in after.roles:
                    lost_role = role
                    break
            if lost_role:
                if lost_role.name in role_order:
                    Usuario.update(after.id, Usuario.read(after.id)["points"], Usuario.read(after.id)["roles"].replace(role_letters[lost_role.name], ""))
                    print("removed role: " + lost_role.name)
                for role_name in role_order[role_order.index(lost_role.name):]:
                    role = discord.utils.get(after.guild.roles, name=role_name)
                    if role in after.roles:
                        await after.remove_roles(role)
                        if role_letters[role_name] in Usuario.read(after.id)["roles"]:
                            Usuario.update(after.id, Usuario.read(after.id)["points"], Usuario.read(after.id)["roles"].replace(role_letters[role_name], ""))
                            print("removed role: " + role_name)
            else:
                for role_name in role_order:
                    if any(role.name == role_name for role in after.roles):
                        roles += role_letters[role_name]
                Usuario.update(after.id, Usuario.read(after.id)["points"], roles)
                print("added roles: " + roles)  
                
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if Usuario.read(member.id):
            Usuario.update(member.id, Usuario.read(member.id)["roles"], "")
        else:
            print("User not found in the database.")

async def setup(bot):
     await bot.add_cog(ModCommands(bot))