import asyncio
from discord.ext import commands
import discord
import asyncio

class PointsCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.points = self.load_Database() # {user_id: points}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.voice is not None:
                    asyncio.create_task(self.count_points(member))


    @commands.Cog.listener()
    async def on_voice_state_update(self, User: discord.Member, before, after):
        if str(User.id) in self.points and User.bot == False and before.channel is None and after.channel is not None:
            await self.count_points(User)
        elif str(User.id) not in self.points and before.channel is None and after.channel is not None:
            await self.registrarAutomatico(User)
            if User.voice is not None:
                await self.count_points(User)

    def load_Database(self):
        with open("Database.txt", "r") as file:
            lines = file.readlines()
            return {line.split(":")[0]: int(line.split(":")[1]) for line in lines}


    def save_Database(self, user_id, points):
        lines = []
        with open("Database.txt", "r") as file:
            lines = file.readlines()

        if any(line.split(":")[0] == user_id for line in lines):
            with open("Database.txt", "w") as file:
                for line in lines:
                    if line.split(":")[0] == user_id:
                        file.write(f"{user_id}:{points}\n")
                    else:
                        file.write(line)
        else:
            with open("Database.txt", "a") as file:
                file.write(f"{user_id}:{points}\n")

    @commands.command()
    async def verPontos(self, ctx):
        user = ctx.author   
        if str(user.id) in self.points:
            await ctx.send(f"Você tem {self.points[str(user.id)]} pontos")
        else:
            await ctx.send("Você não está registrado.")        

    async def registrarAutomatico(self, User: discord.Member):
        if(str(User.id)) in self.points:
            print("User is already in the database.👺👺👺👺👺👺👺") #Doesn't usually get here
        else:
            self.points[str(User.id)] = 0
            self.save_Database(str(User.id), 0)
            print("User registered sucessfully!🫃🫃🫃🫃🫃🫃🫃")
    
    async def count_points(self, User: discord.Member):
        if str(User.id) in self.points:
            while True:
                User = discord.utils.get(self.bot.get_all_members(), id=User.id)
                if User.voice is None:
                    break

                self.points[str(User.id)] += 1
                self.save_Database(str(User.id), self.points[str(User.id)])
                await asyncio.sleep(5)
        else:
            await self.registrarAutomatico(User)
            await self.count_points(User)



async def setup(bot):   
    await bot.add_cog(PointsCommands(bot))
    
