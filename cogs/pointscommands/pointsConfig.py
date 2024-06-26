from discord.ext import commands
from db.botConfigDB import BotConfig
from tools.embed import create_embed_without_title
from db.userDB import Usuario
from tools.pricing import pricing
import math
import time
import discord
class PointsConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_time = {}
        self.init_time = math.ceil(time.time())

    @commands.hybrid_command(name="points_toggle", aliases=["ptoggle"], brief="Check the status of ptscmds.", usage="points_toggle", description="Check if the points commands are enabled or disabled in the server.")
    async def points_status(self, ctx):
        """Check if the points commands are enabled or disabled in the server."""
        await create_embed_without_title(ctx, f":warning: The points commands are {'**enabled**' if BotConfig.read[ctx.guild.id]['toggle'] else '**disabled**'} in this server.")

    async def update_points(self, User: discord.Member):
        """Updates the points of the user every 10 seconds."""
        userId = User.id
        if userId in self.join_time.keys():
            add_points = (math.ceil(time.time()) - self.join_time[userId]) // 10
            total_points = Usuario.read(userId)["points"] + add_points
            Usuario.update(userId, total_points, Usuario.read(userId)["roles"])
            self.join_time[userId] = math.ceil(time.time())
            return total_points
        
        if userId not in self.join_time.keys() and User.voice is not None:
           add_points = (math.ceil(time.time()) - self.init_time) // 10
           print(Usuario.read(userId)["points"])
           print(add_points)
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
 
    @commands.hybrid_command(name="points", aliases=["pts", "eggbux"], brief="Shows the amount of points the user has.", usage="points OPTIONAL [user]", description="Shows the amount of points a usr has. If not usr, shows author's points.")
    @pricing()
    async def points(self, ctx, user: discord.Member = None):
        """Shows the amount of points the user has."""
        if user is None:
            user = ctx.author
        user_data = Usuario.read(user.id)
        if user_data and isinstance(user_data, dict) and "points" in user_data:
            points = await self.update_points(user)
            if points is None:
                points = user_data["points"]
            await create_embed_without_title(ctx, f":coin: {user.display_name} has {points} eggbux.")
        else:
            await create_embed_without_title(ctx, f"{user.display_name} has no eggbux :cry:")

    @commands.Cog.listener()
    async def on_voice_state_update(self, User: discord.Member, before, after):
        """Listens to the voice state update event."""
        if User.bot:
            return
        if Usuario.read(User.id) and before.channel is None and after.channel is not None:
            await self.count_points(User)
        elif not Usuario.read(User.id) and before.channel is None and after.channel is not None:
            self.automatic_register(User)
            await self.count_points(User)
        elif Usuario.read(User.id) and before.channel is not None and after.channel is None:
            await self.update_points(User)
        elif not Usuario.read(User.id) and before.channel is not None and after.channel is None:
            self.automatic_register(User)
            await self.update_points(User)


async def setup(bot):
    await bot.add_cog(PointsConfig(bot))
