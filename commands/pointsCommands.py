import asyncio
import os
from discord.ext import commands
from random import randint
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

   
    @commands.command()
    async def pontos(self, ctx):
        user = ctx.author   
        if str(user.id) in self.points:
            await ctx.send(f"Você tem {self.points[str(user.id)]} eggbux 💸")
        else:
            await ctx.send("Você não está registrado.")        

    async def registrarAutomatico(self, User: discord.Member):
        if(str(User.id)) in self.points:
            print("User is already in the database.👺👺👺👺👺👺👺") #Doesn't usually get here
        else:
            self.points[str(User.id)] = 0
            print("User registered sucessfully!🫃🫃🫃🫃🫃🫃🫃")
    
    async def count_points(self, User: discord.Member):
        if str(User.id) in self.points:
            while True:
                User = discord.utils.get(self.bot.get_all_members(), id=User.id)
                if User.voice is None:
                    break
                self.points[str(User.id)] += 1
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
            message += f"{i+1}. {user.mention} - {points} eggbux\n"
        await ctx.send(message)

    
    @commands.command()
    async def shop(self, ctx):
        embed = discord.Embed(title="Shop", description="Compre comandos com seus eggbux:", color=0x000000)
        embed.add_field(name="1. Balls", value="50 eggbux", inline=False)
        embed.add_field(name="2. Moggar um usuário", value="100 eggbux", inline=False)
        embed.add_field(name="3. mute (mutar um usuário)", value="150 eggbux", inline=False)
        embed.add_field(name="4. changeNickname", value="200 eggbux", inline=False)
        embed.add_field(name="5. purge (deletar até 25 mensagens no chat)", value="250 eggbux", inline=False)
        embed.add_field(name="6. kick (kickar um usuário)", value="350 eggbux", inline=False)
        embed.add_field(name="7. ban (banir um usuário)", value="450 eggbux", inline=False)
        embed.add_field(name="8. Pardon (desbanir um usuário)", value="500 eggbux", inline=False)
        embed.add_field(name="8. Momento De silêncio (Muta todo mundo do server)", value="500 eggbux", inline=False)
        embed.add_field(name="9. god (Nunca é mutado por ninguém)", value="1000 eggbux", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def roubarPontos(self, ctx, User: discord.Member):
        if str(ctx.author.id) in self.points and str(User.id) in self.points:
            quantUser = self.points[str(User.id)]
            randomInteiro = randint(0, int(quantUser/5) + 1) # 20% do total de pontos do usuário
            self.points[str(User.id)] -= randomInteiro
            self.points[str(ctx.author.id)] += randomInteiro
            await ctx.send(f"{ctx.author.mention} roubou {randomInteiro} eggbux de {User.mention}")
        else:
            await ctx.send("Erro ao roubar pontos")


    # mod commands
    @commands.command()
    async def addPontos(self, ctx, User: discord.Member, amount: int):
        user = ctx.author
        owner = ctx.guild.owner.id
        if str(user.id) in self.devs:
            self.points[str(User.id)] += amount
            await ctx.send(f"{User.mention} recebeu {amount} eggbux")
        else:
            await ctx.send("Você não tem permissão para fazer isso")

    @commands.command()
    async def deleteDB(self, ctx, User: discord.Member):
        user = ctx.author
        owner = ctx.guild.owner.id
        if str(user.id) in self.devs:
            await ctx.send(f"{User.mention} foi deletado do banco de dados")
        elif str(user.id) not in self.devs:
            await ctx.send("Você não tem permissão para fazer isso")
        else:
            await ctx.send("Usuário não encontrado no banco de dados")

    


async def setup(bot):   
    await bot.add_cog(PointsCommands(bot))
    
