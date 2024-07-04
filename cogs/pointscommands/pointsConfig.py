from discord.ext import commands
from db.botConfigDB import BotConfig
from tools.embed import create_embed_without_title, create_embed_with_title, make_embed_object
from db.bankDB import Bank
from db.userDB import Usuario
from tools.pricing import pricing
from db.botConfigDB import BotConfig
import math
import time
import discord
class PointsConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_time = {}
        self.init_time = math.ceil(time.time())

    @commands.hybrid_command(name="pointstoggled", aliases=["pstatus"], brief="Check the status of ptscmds.", usage="points_toggle", description="Check if the points commands are enabled or disabled in the server.")
    async def points_status(self, ctx):
        """Check if the points commands are enabled or disabled in the server."""
        await create_embed_without_title(ctx, f":warning: The points commands are {'**enabled**' if BotConfig.read[ctx.guild.id]['toggle'] else '**disabled**'} in this server.")

    async def update_points(self, User: discord.Member, *kwargs):
        """Updates the points of the user every 10 seconds."""
        userId = User.id
        if kwargs:
            left_channel = kwargs[0]
            print("Left channel")
            if left_channel:
                add_points = (math.ceil(time.time()) - self.join_time[userId]) // 10
                total_points = Usuario.read(userId)["points"] + add_points
                Usuario.update(userId, total_points, Usuario.read(userId)["roles"])
                self.join_time.pop(userId)
                return total_points
        
        if userId in self.join_time.keys():
            print("User in join_time")
            add_points = (math.ceil(time.time()) - self.join_time[userId]) // 10
            total_points = Usuario.read(userId)["points"] + add_points
            Usuario.update(userId, total_points, Usuario.read(userId)["roles"])
            self.join_time[userId] = math.ceil(time.time())
            return total_points
        
        if userId not in self.join_time.keys() and User.voice:
           print("User not in join_time")
           add_points = (math.ceil(time.time()) - self.init_time) // 10
           total_points = Usuario.read(userId)["points"] + add_points
           Usuario.update(userId, total_points, Usuario.read(userId)["roles"])
           self.join_time[userId] = math.ceil(time.time())
           return total_points

    async def count_points(self, User: discord.Member):
        """Counts the points of the user every time he enters a voice channel."""
        userId = User.id
        if User.bot:
            return
        if userId not in self.join_time.keys():
            self.join_time[userId] = math.ceil(time.time())
        else:
            return

    def automatic_register(self, User: discord.Member):
        """Automatically registers the user in the database."""
        if Usuario.read(User.id) and User.bot:
            return
        else:
            Usuario.create(User.id, 0)
            print(f"User created: {User.name}")

    @commands.hybrid_command(name="register", aliases=["reg"], brief="Registers the user in the database.", usage="register", description="Registers the user in the database.")
    async def register(self, ctx):
        """Registers the user in the database."""
        if Usuario.read(ctx.author.id):
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} is already registered.")
        else:
            Usuario.create(ctx.author.id, 0)
            await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name} has been registered.")
 
    @commands.hybrid_command(name="points", aliases=["pts", "eggbux", "p"], brief="Shows the amount of points the user has.", usage="points OPTIONAL [user]", description="Shows the amount of points a usr has. If not usr, shows author's points.")
    @pricing()
    async def points(self, ctx, user: discord.Member = None):
        """Shows the amount of points the user has."""
        if user is None:
            user = ctx.author
        user_data = Usuario.read(user.id)
        if user_data and isinstance(user_data, dict) and "points" in user_data:
            points = await self.update_points(user)
            print(points)
            if points is not None:
                user_data['points'] = points

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

    @commands.Cog.listener()
    async def on_voice_state_update(self, User: discord.Member, before, after):
        """Listens to the voice state update event."""
        if not BotConfig.read(User.guild.id)['toggled_modules'] == "N":
            if User.bot:
                return
            if Usuario.read(User.id) and before.channel is None and after.channel is not None:
                await self.count_points(User)
            elif not Usuario.read(User.id) and before.channel is None and after.channel is not None:
                self.automatic_register(User)
                await self.count_points(User)
            elif Usuario.read(User.id) and before.channel is not None and after.channel is None:
                await self.update_points(User, left_channel=True)
            elif not Usuario.read(User.id) and before.channel is not None and after.channel is None:
                self.automatic_register(User)
                await self.update_points(User, left_channel=True)



async def setup(bot):
    await bot.add_cog(PointsConfig(bot))

