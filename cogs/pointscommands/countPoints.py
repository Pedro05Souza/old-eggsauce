from discord.ext import commands
import discord
from db.userDB import Usuario
import math
import time
from tools.embed import create_embed_without_title
from tools.pricing import pricing

class CountCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.joinTime = {}

    async def update_points(self, User: discord.Member):
        """Updates the points of the user every 10 seconds."""
        userId = User.id
        if userId in self.joinTime.keys():
                addPoints = (math.ceil(time.time()) - self.joinTime[userId]) // 10
                print(math.ceil(time.time()))
                print(addPoints)
                totalPoints = Usuario.read(userId)["points"] + addPoints
                Usuario.update(userId, totalPoints, Usuario.read(userId)["roles"])
                self.joinTime[userId] = math.ceil(time.time())
                return totalPoints
        else:
            print(f"{User.name} not found in dict")
            return
        
    async def count_points(self, User: discord.Member):
        """Counts the points of the user every time he enters a voice channel."""
        userId = User.id
        if User.bot:
            return
        if userId not in self.joinTime.keys():
            self.joinTime[userId] = math.ceil(time.time())
        else:
            return

    def automatic_register(self, User: discord.Member):
        """Automatically registers the user in the database."""
        if Usuario.read(User.id) and User.bot:
            return
        else:
            Usuario.create(User.id, 0)
            print(f"User created: {User.name}")
 
    @commands.command()
    @pricing()
    async def points(self, ctx, User: discord.Member = None):
        """Shows the amount of points the user has."""
        if User is None:
            User = ctx.author
        user_data = Usuario.read(User.id)
        if user_data and isinstance(user_data, dict) and "points" in user_data:
            points = await self.update_points(User)
            if points is None:
                points = user_data["points"]
            await create_embed_without_title(ctx, f":coin: {User.display_name} has {points} eggbux.")
        else:
            await create_embed_without_title(ctx, f"{User.display_name} has no eggbux :cry:")

    @commands.Cog.listener()
    async def on_voice_state_update(self, User: discord.Member, before, after):
        """Listens to the voice state update event."""
        if User.bot:
            return
        if Usuario.read(User.id) and before.channel is None and after.channel is not None:
            await self.count_points(User)
        elif not Usuario.read(User.id) and before.channel is None and after.channel is not None:
            self.automatic_register(User)
            if User.voice is not None:
                await self.count_points(User)
        elif Usuario.read(User.id) and before.channel is not None and after.channel is None:
            await self.update_points(User)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Points commands are ready!")
        for guild in self.bot.guilds:
            for vc in guild.voice_channels:
                for member in vc.members:
                    if member.voice is not None:
                        await self.count_points(member)

async def setup(bot):
    await bot.add_cog(CountCommands(bot))