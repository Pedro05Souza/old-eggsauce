from discord.ext import commands
from random import randint
import discord
from db.userDB import Usuario
from db.channelDB import ChannelDB
import os
import asyncio
from tools.pricing import pricing, Prices, refund
from tools.pagination import PaginationView

# This PointsCommands class is specifically for the points system;
class PointsCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.tasks = {}

    @commands.Cog.listener()
    async def on_ready(self):
        self.drop_eggbux_task = self.bot.loop.create_task(self.drop_periodically())
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.voice is not None and member.id not in self.tasks:
                    self.tasks[member.id] = asyncio.create_task(self.count_points(member))

    async def count_points(self, User: discord.Member):
        if User.bot:
            return
        if Usuario.read(User.id):
            while True:
                User = discord.utils.get(self.bot.get_all_members(), id=User.id)
                if User.voice is None and User.id in self.tasks:
                    self.tasks[User.id].cancel()
                    break
                Usuario.update(User.id, Usuario.read(User.id)["points"] + 1, Usuario.read(User.id)["roles"])
                await asyncio.sleep(10)      
        else:
            self.registrarAutomatico(User)
            if User.id not in self.tasks:
                self.tasks[User.id] = asyncio.create_task(self.count_points(User))

    def registrarAutomatico(self, User: discord.Member):
        if Usuario.read(User.id) and User.bot:
            return
        else:
            Usuario.create(User.id, 0)
            print(f"Usuário criado: {User.name}")
 
    @commands.command("pontos" , aliases=["verpontos", "money" , "eggbux"])
    async def points(self, ctx, User: discord.Member = None):
        if User is None:
            await ctx.send(f"{ctx.author.mention} tem " + str(Usuario.read(ctx.author.id)["points"]) + " eggbux :money_with_wings:")
        elif Usuario.read(User.id):
            await ctx.send(f"{User.mention} tem " + str(Usuario.read(User.id)["points"]) + " eggbux :money_with_wings:")
        else:
            await ctx.send(f"{User.mention} não tem eggbux!")
    
    @commands.command("shop", aliases=["loja", "comprar", "store"])
    @pricing()
    async def shop(self, ctx):
        data = []
        for member in Prices.__members__:
            data.append({"title": member, "value": str(Prices.__members__[member].value) + " eggbux"})
        view = PaginationView(data)
        await view.send(ctx, title="Shop", description="Compre comandos com seus eggbux:", color=0x00ff00)

    @commands.command("leaderboard", aliases=["ranking"])
    async def leaderboard(self, ctx):
        users = Usuario.readAll()
        users = sorted(users, key=lambda x: x["points"], reverse=True)
        guild = ctx.guild
        data = []
        for i in users:
            member = discord.utils.get(self.bot.get_all_members(), id=i["user_id"])
            if member is not None and member in guild.members:
                data.append({"title": member.name, "value": i["points"]})
        view = PaginationView(data)
        await view.send(ctx, title="Leaderboard", description="Ranking de eggbux", color=0x00ff00)

    async def drop_eggbux_for_guild(self, guild):
        server = ChannelDB.read(server_id=guild.id)
        if server:
            channel = self.bot.get_channel(server["channel_id"])
            chance = randint(0, 100)
            if chance <= 20:  # 20% de chance de dropar
                quantEgg = randint(1, 750) 
                await channel.send(f"uma bolsa com {quantEgg} eggbux foi dropada no chat! :money_with_wings:. Digite !claim para pegar, lembrando você tem 5 minutos para pegar!")
                try:
                    Message = await asyncio.wait_for(self.bot.wait_for('message', check=lambda message: message.content == "!claim" and message.channel == channel), timeout=300)
                    if Usuario.read(Message.author.id):
                        Usuario.update(Message.author.id, Usuario.read(Message.author.id)["points"] + quantEgg, Usuario.read(Message.author.id)["roles"])
                        await channel.send(f"{Message.author.mention} pegou {quantEgg} eggbux")
                    else:
                        Usuario.create(Message.author.id, quantEgg)
                        await channel.send(f"{Message.author.mention} pegou {quantEgg} eggbux")
                except asyncio.TimeoutError:
                    await channel.send(f"A bolsa com {quantEgg} eggbux foi perdida. :cry:")

    async def drop_eggbux(self):
        await asyncio.gather(*(self.drop_eggbux_for_guild(guild) for guild in self.bot.guilds))
            
    async def drop_periodically(self):
        while True:
            await self.drop_eggbux()
            await asyncio.sleep(1000)

    @commands.command()
    @pricing()
    async def doarPontos(self, ctx, User:discord.Member, amount: int):
        if Usuario.read(ctx.author.id) and Usuario.read(User.id):
            if ctx.author.id == User.id:
                await ctx.send("Você não pode doar para si mesmo")
            elif Usuario.read(ctx.author.id)["points"] >= amount:
                if amount <= 0:
                    await ctx.send("Você não pode doar 0 ou uma quantidade negativa de eggbux")
                    return
                else:
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] - amount, Usuario.read(ctx.author.id)["roles"])
                    Usuario.update(User.id, Usuario.read(User.id)["points"] + amount, Usuario.read(User.id)["roles"])
                    await ctx.send(f"{ctx.author.mention} doou {amount} eggbux para {User.mention}")
            else:
                await ctx.send(f"{ctx.author.mention} você não tem eggbux suficiente para fazer essa doação")
        else:
            await ctx.send("Você não tem permissão para fazer isso")

    @commands.command("cassino", aliases=["roleta", "roulette"]) 
    async def cassino(self, ctx, amount: int, cor: str):
        cor = cor.upper()
        coresPossiveis = ["RED", "BLACK", "GREEN"]
        corEmoji = {"RED": "🟥", "BLACK": "⬛", "GREEN": "🟩"}
        vermelhos = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        roleta = {i : "RED" if i in vermelhos else ("BLACK" if i != 0 else "GREEN") for i in range(0, 37)}
        if Usuario.read(ctx.author.id) and cor in coresPossiveis:
            if Usuario.read(ctx.author.id)["points"] >= amount and amount >= 50:
                cassino = randint(0, 36)
                corSorteada = roleta[cassino]
                if corSorteada == "GREEN" and cor == "GREEN":
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + (amount * 14), Usuario.read(ctx.author.id)["roles"])
                    await ctx.send(f"{ctx.author.display_name} ganhou!")
                elif corSorteada == cor:
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + amount, Usuario.read(ctx.author.id)["roles"])
                    await ctx.send(f"{ctx.author.display_name} ganhou!")
                else:
                    await ctx.send(f"{ctx.author.display_name} perdeu, a cor sorteada foi {corSorteada} {corEmoji[corSorteada]}")                        
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] - amount, Usuario.read(ctx.author.id)["roles"])
                    return
            else:
                await ctx.send(f"{ctx.author.display_name} não tem pontos suficientes")
                return  
        else:
            await ctx.send("Selecione uma cor válida.")

    @cassino.error
    async def cassino_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Por favor, insira um valor e uma cor.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Por favor, insira um valor válido.")
        else:
            await ctx.send("Ocorreu um erro inesperado.")

    @commands.command("roubarPontos", aliases=["stealPoints", "roubar", "steal"])
    @pricing()
    async def stealPoints(self, ctx, User: discord.Member):
        if Usuario.read(ctx.author.id):
            chance  = randint(0, 100)
            if User.bot:
                await ctx.send("Você não pode roubar de um bot")
                await refund(ctx.author, ctx)
                return
            if Usuario.read(User.id):
                if ctx.author.id == User.id:
                    await ctx.send("Você não pode roubar de si mesmo")
                    await refund(ctx.author, ctx)
                elif chance >= 10: # 10% de chance de falhar
                    quantUser = Usuario.read(User.id)["points"]
                    randomInteiro = randint(0, int(quantUser/2)) # 50% do total de pontos do usuário
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + randomInteiro, Usuario.read(ctx.author.id)["roles"])
                    Usuario.update(User.id, Usuario.read(User.id)["points"] - randomInteiro, Usuario.read(User.id)["roles"])
                    await ctx.send(f"{ctx.author.mention} roubou {randomInteiro} eggbux de {User.mention}")
                else:
                    await ctx.send(f"{ctx.author.mention} falhou ao tentar roubar de {User.mention}")
            else:
                await ctx.send("Você não tem permissão para fazer isso")
                await refund(ctx.author, ctx)
        else:
            await ctx.send("Você não tem permissão para fazer isso")

    @commands.Cog.listener()
    async def on_voice_state_update(self, User: discord.Member, before, after):
        if User.bot:
            return
        if Usuario.read(User.id) and before.channel is None and after.channel is not None:
            if User.id in self.tasks and not self.tasks[User.id].done():
                return 
            self.tasks[User.id] = asyncio.create_task(self.count_points(User))
        elif not Usuario.read(User.id) and before.channel is None and after.channel is not None:
            self.registrarAutomatico(User)
            if User.voice is not None:
                if User.id in self.tasks and not self.tasks[User.id].done():
                    return 
                self.tasks[User.id] = asyncio.create_task(self.count_points(User))

async def setup(bot):   
    await bot.add_cog(PointsCommands(bot))
            