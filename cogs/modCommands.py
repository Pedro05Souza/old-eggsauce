import asyncio
import os
import sys
import signal
import discord
from discord.ext import commands
from db.userDB import Usuario
from db.toggleDB import ToggleDB
from db.bankDB import Bank
from tools.pricing import Prices, refund, pricing
from tools.embed import create_embed_without_title
from db.channelDB import ChannelDB
from dotenv import load_dotenv

# This ModCommands class is specifically for testing purposes;
class ModCommands(commands.Cog):
    
    def __init__(self, bot):
        load_dotenv()
        self.devs = os.getenv("DEVS").split(",")
        self.bot = bot
        self.logs = []

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

    @commands.command("removeRole")
    async def remove_role(self, ctx ,User:discord.Member, role: str):
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
                            await create_embed_without_title(ctx, f"{User.mention} lost the role {roleRemove}")
                    else:
                        await create_embed_without_title(ctx, f"{User.display_name} does not have the role {possibleRoles[role]}")
            else:
                await create_embed_without_title(ctx, f"{User.display_name} is not registered in the database!")
        else:
            await create_embed_without_title(ctx, ":no_entry_sign: You do not have permission to do this.")

    @commands.command("setChannel")
    async def set_channel(self, ctx):
        """Set the channel where the bot will listen for commands."""
        if ctx.author.guild_permissions.administrator or str(ctx.author.id in self.devs):
            if ChannelDB.read(server_id=ctx.guild.id):
                ChannelDB.update(ctx.guild.id ,ctx.channel.id)
                await create_embed_without_title(ctx, ":white_check_mark: Commands channel has been updated.")
            else:
                ChannelDB.create(ctx.guild.id, ctx.channel.id)
                print(f"New channel registered for guild {ctx.guild.name}")
                await create_embed_without_title(ctx, ":white_check_mark: Commands channel has been set.")
        else:
            await create_embed_without_title(ctx, ":no_entry_sign: You do not have permission to do this.")

    @commands.command("togglePoints")
    async def toggle_points(self, ctx):
        """Enable or disable the points commands."""
        if ctx.guild.owner_id == ctx.author.id or str(ctx.author.id) in self.devs:
            if ToggleDB.read(ctx.guild.id)["toggle"]:
                ToggleDB.update(ctx.guild.id, False)
                await create_embed_without_title(ctx, ":warning: Points commands are now disabled.")
            else:
                ToggleDB.update(ctx.guild.id, True)
                await create_embed_without_title(ctx, ":white_check_mark: Points commands are now enabled.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you do not have permission to do this.")
            
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

    async def restart_client(self):
        try:
            print("Attempting to restart the bot.")
            await self.bot.close()
            command = [sys.executable, 'main.py'] + sys.argv[1:]
            await asyncio.sleep(5)
            print("Bot has been restarted.")
            os.execv(sys.executable, command)
        except Exception as e:
            print(e)

    @commands.command("r", aliases=["restart"])
    async def force_restart(self, ctx):
        """Restart the bot."""
        if str(ctx.author.id) in self.devs:
            await create_embed_without_title(ctx, ":warning: Restarting...")
            await self.restart_client()

    async def restart_every_week(self):
        while True:
            await asyncio.sleep(604800)
            command = [sys.executable, 'main.py'] + sys.argv[1:]
            os.execv(sys.executable, command)

    # Event listeners; these functions are called when the event they are listening for is triggered
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if not ToggleDB.read(guild.id):
            ToggleDB.create(guild.id, True)
        print(f"Joined guild {guild.name}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        ToggleDB.delete(guild.id)
        ChannelDB.delete(guild.id)
        print(f"Left guild {guild.name}")
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.restart_every_week())

    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    #     if ToggleDB.read(ctx.guild.id) and not ToggleDB.read(ctx.guild.id)['toggle']:
    #         return
    #     if isinstance(error, commands.CommandError):
    #         if ctx is not None:
    #             if hasattr(ctx, "predicate_result") and ctx.predicate_result:
    #                 enumPricing = Prices.__members__
    #                 if ctx.command.name in enumPricing:
    #                     if enumPricing[ctx.command.name].value > 0:
    #                         await create_embed_without_title(ctx, f":no_entry_sign: {error} The {ctx.command.name} command has been cancelled and refunded.")
    #                         await refund(ctx.author, ctx)
    #     print(error)
async def setup(bot):
     await bot.add_cog(ModCommands(bot))