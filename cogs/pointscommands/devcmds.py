"""
This file contains the developer commands for the bot.
"""

from discord.ext import commands
from db.userDB import User
from tools.shared import make_embed_object, send_bot_embed, is_dev, retrieve_threads
from db.bankDB import Bank
from db.farmDB import Farm
from db.marketDB import Market
from tools.chickens.chickenshared import create_chicken
from tools.chickens.chickeninfo import ChickenRarity
from tools.chickens.chickenhandlers import RollLimit
from tools.cache.init import cache_initiator
from .. import botcore
from discord.ext.commands import Context
from typing import Any
import discord
import tools

class DevCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command("addPoints") 
    async def add_points(self, ctx: Context, amount: int, user: discord.Member = None) -> None:
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
    async def remove_points(self, ctx: Context, amount: int, user: discord.Member = None) -> None:
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
    async def latency(self, ctx: Context) -> None:
        """Check the bot's latency."""
        if is_dev(ctx):
            await send_bot_embed(ctx, description=f":ping_pong: {round(self.bot.latency * 1000)}ms")

    @commands.command("deleteDB")
    async def delete_db(self, ctx: Context, user: discord.Member) -> None:
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
    async def reset(self, ctx: Context, user: discord.Member) -> None:
        """Reset a user from the database."""
        if is_dev(ctx) and User.read(user.id):
            if Bank.read(user.id):
                Bank.update(user.id, 0)
            User.update_all(user.id, 0, "")
            await send_bot_embed(ctx, description=f"{user.display_name} has been reset.")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")
    
    @commands.command("giveRolls")
    async def give_rolls(self, ctx: Context, rolls : int, user: discord.Member) -> None:
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
    async def check_bot_servers(self, ctx: Context) -> None:
        """Check the servers the bot is in."""
        if is_dev(ctx):
            servers = self.bot.guilds
            total_servers = len(servers)
            await send_bot_embed(ctx, description=f"```The bot is currently in: {total_servers} servers```")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")
    
    @commands.command("totalusers")
    async def total_users(self, ctx: Context) -> None:
        """Check the total number of users in the database."""
        if is_dev(ctx):
            total_users = User.count_users()
            await send_bot_embed(ctx, description=f"```Total users in the database: {total_users}```")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")

    @commands.command("spawnChicken")
    async def spawn_chicken(self, ctx: Context, user: discord.Member, rarity: str) -> None:
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
    async def circulation_chickens(self, ctx: Context) -> None:
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
    async def remove_chicken(self, ctx: Context, user: discord.Member, index: Any) -> None:
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
    async def purge(self, ctx: Context, amount: int) -> None:
        """Deletes a certain amount of messages."""
        if is_dev(ctx):
            if amount > 0 and amount <= 25:
                await ctx.channel.purge(limit=amount + 1)
                  
    @commands.command(name="marketLogs")
    async def market_logs(self, ctx: Context) -> None:
     """Check the total number of active offers in the market."""
     if is_dev(ctx):
        total_offers = Market.count_all_offers()
        await send_bot_embed(ctx, description=f"```Total active offers in the player market: {total_offers}```")
     else:
        await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")
    
    @commands.command(name="reloadBot")
    async def reload_cog(self, ctx: Context, folder: str, cog_name: str) -> None:
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
    async def unload_cog(self, ctx: Context, cog_name: str) -> None:
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
    async def developer_panel(self, ctx: Context) -> None:
        if is_dev(ctx):
            user, guild = await cache_initiator.get_memory_usage()
            embed_obj = await make_embed_object(title="⚙️ Developer Panel")
            embed_obj.add_field(name="🔧 Cache Memory Usage:", value=f"User Cache: {user} bytes\nGuild Cache: {guild} bytes")
            embed_obj.add_field(name="🧰 Current active threads:", value=f"{retrieve_threads()}")
            await ctx.send(embed=embed_obj)

    @commands.command(name="sync")
    async def sync(self, ctx: Context) -> None:
        if is_dev(ctx):
            await self.bot.tree.sync()
            await send_bot_embed(ctx, description=":warning: bot data has been synced.")
        else:
            await send_bot_embed(ctx, description=":no_entry_sign: You do not have permission to do this.")

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