import asyncio
import os
from discord.ext import commands
from dotenv import load_dotenv
import discord
import asyncio

class PointsCommands(commands.Cog):

    def __init__(self, bot):
        load_dotenv()
        self.bot = bot
        self.points = self.load_Database() # {user_id: points}
        self.devs = os.getenv("DEVS").split(",")

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

    def deleteFromDB(self, user_id):
        with open("Database.txt", "r") as file:
            lines = file.readlines()
        with open("Database.txt", "w") as file:
            for line in lines:
                if line.split(":")[0] != user_id:   
                    file.write(line)
        if user_id in self.points:
            del self.points[user_id]

    @commands.command()
    async def pontos(self, ctx):
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


    @commands.command()
    async def leaderboard(self, ctx):
        sorted_points = {k: v for k, v in sorted(self.points.items(), key=lambda item: item[1], reverse=True)}
        message = "Leaderboard:\n"
        for i, (user_id, points) in enumerate(sorted_points.items()):
            user = discord.utils.get(ctx.guild.members, id=int(user_id))
            message += f"{i+1}. {user.mention} - {points} pontos\n"
        await ctx.send(message)

    
    @commands.command()
    async def shop(self, ctx):
        embed = discord.Embed(title="Shop", description="Compre comandos com seus pontos:", color=0xeee657)
        embed.add_field(name="1. Moggar um usuário", value="100 pontos", inline=False)
        embed.add_field(name="2. Balls", value="50 pontos", inline=False)
        embed.add_field(name="3. ChangeNickname", value="200 pontos", inline=False)
        embed.add_field(name="4. purge (deletar até 25 mensagens no chat)", value="250 pontos", inline=False)
        embed.add_field(name="5. implode (desconectar geral do canal de voz presente)", value="300 pontos", inline=False)
        await ctx.send(embed=embed)


    # mod commands
    @commands.command()
    async def addPontos(self, ctx, User: discord.Member, amount: int):
        user = ctx.author
        owner = ctx.guild.owner.id
        if str(user.id) in self.devs:
            self.points[str(User.id)] += amount
            self.save_Database(str(User.id), self.points[str(User.id)])
            await ctx.send(f"{User.mention} recebeu {amount} pontos")
        else:
            await ctx.send("Você não tem permissão para fazer isso")

    @commands.command()
    async def deleteDB(self, ctx, User: discord.Member):
        user = ctx.author
        owner = ctx.guild.owner.id
        if str(user.id) in self.devs:
            self.deleteFromDB(str(User.id))
            await ctx.send(f"{User.mention} foi deletado do banco de dados")
        elif str(user.id) not in self.devs:
            await ctx.send("Você não tem permissão para fazer isso")
        else:
            await ctx.send("Usuário não encontrado no banco de dados")


async def setup(bot):   
    await bot.add_cog(PointsCommands(bot))
    
