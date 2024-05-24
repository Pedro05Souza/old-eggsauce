from discord.ext import commands
from random import randint
import discord
import time
import math
from db.userDB import Usuario
from db.channelDB import ChannelDB
import asyncio
from tools.pricing import pricing, Prices, refund
from tools.pagination import PaginationView

# This PointsCommands class is specifically for the points system;
class PointsCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.joinTime = {}

    @commands.Cog.listener()
    async def on_ready(self):
        self.drop_eggbux_task = self.bot.loop.create_task(self.drop_periodically())
        for guild in self.bot.guilds:
            for vc in guild.voice_channels:
                for member in vc.members:
                    if member.voice is not None:
                        await self.count_points(member)

    async def update_points(self, User: discord.Member):
        userId = User.id
        print(f"User id: {userId}")
        if userId in self.joinTime.keys():
            if Usuario.read(userId):
                print(f"Updating points for {User.name}")
                print((math.ceil(time.time()) - self.joinTime[userId]) // 10)
                Usuario.update(userId, ((Usuario.read(userId)["points"] + ((math.ceil(time.time()) - self.joinTime[userId])) // 10)), Usuario.read(userId)["roles"])
        else:
            print(self.joinTime)
            print("User not found in dict")
        
    async def count_points(self, User: discord.Member):
        userId = User.id
        if User.bot:
            return
        print(f"Counting points for {User.name}")
        print(f"User id: {userId}")
        if userId not in self.joinTime.keys():
            self.joinTime[userId] = math.ceil(time.time())
        else:
            return


    async def drop_eggbux(self):
        await asyncio.gather(*(self.drop_eggbux_for_guild(guild) for guild in self.bot.guilds))

    def registrarAutomatico(self, User: discord.Member):
        if Usuario.read(User.id) and User.bot:
            return
        else:
            Usuario.create(User.id, 0)
            print(f"User created: {User.name}")
 
    @commands.command()
    @pricing()
    async def points(self, ctx, User: discord.Member = None):
        if User is None:
            user_data = Usuario.read(ctx.author.id)
            if user_data and isinstance(user_data, dict) and "points" in user_data:
                await self.update_points(ctx.author)
                await ctx.send(f"{ctx.author.mention} has {user_data['points']} eggbux :money_with_wings:")
            else:
                await ctx.send(f"{ctx.author.mention} has no eggbux :cry:")
        else:
            user_data = Usuario.read(User.id)
            if user_data and isinstance(user_data, dict) and "points" in user_data:
                await self.update_points(User)
                await ctx.send(f"{User.mention} has {user_data['points']} eggbux :money_with_wings:")
            else:
                await ctx.send(f"{User.mention} has no eggbux :cry:")
        
    @commands.command("shop", aliases=["store"])
    @pricing()
    async def shop(self, ctx):
        data = []
        for member in Prices.__members__:
            if Prices.__members__[member].value > 0:
                data.append({"title": member, "value": str(Prices.__members__[member].value) + " eggbux"})
        view = PaginationView(data)
        await view.send(ctx, title="Shop", description="Buy commands with your eggbux:", color=0x00ff00)

    @commands.command("leaderboard", aliases=["ranking"])
    @pricing()
    async def leaderboard(self, ctx):
        users = Usuario.readAll()
        users = sorted(users, key=lambda x: x['points'], reverse=True)
        guild = ctx.guild
        data = []
        for i in users:
            member = discord.utils.get(self.bot.get_all_members(), id=i["user_id"])
            if member is not None and member in guild.members:
                data.append({"title": member.name, "value": i["points"]})
        view = PaginationView(data)
        await view.send(ctx, title="Leaderboard", description="Eggbux's ranking", color=0x00ff00)

    async def drop_eggbux_for_guild(self, guild):
        server = ChannelDB.read(server_id=guild.id)
        if server:
            channel = self.bot.get_channel(server["channel_id"])
            chance = randint(0, 100)
            if chance <= 8:  # 20% de chance de dropar
                quantEgg = randint(1, 750) 
                await channel.send(f"A bag with {quantEgg} eggbux has been dropped in the chat! :money_with_wings:. Type !claim to get it. Remember you only have 5 minutes to claim it.")
                try:
                    Message = await asyncio.wait_for(self.bot.wait_for('message', check=lambda message: message.content == "!claim" and message.channel == channel), timeout=300)
                    if Usuario.read(Message.author.id):
                        Usuario.update(Message.author.id, Usuario.read(Message.author.id)["points"] + quantEgg, Usuario.read(Message.author.id)["roles"])
                        await channel.send(f"{Message.author.mention} claimed {quantEgg} eggbux")
                    else:
                        Usuario.create(Message.author.id, quantEgg)
                        await channel.send(f"{Message.author.mention} claimed {quantEgg} eggbux")
                except asyncio.TimeoutError:
                    await channel.send(f"The bag with {quantEgg} eggbux has been lost. :cry:")
            
    async def drop_periodically(self):
        while True:
            await self.drop_eggbux()
            await asyncio.sleep(1000)

    @commands.command("donatePoints", aliases=["donate"])
    @pricing()
    async def donatePoints(self, ctx, User:discord.Member, amount: int):
        if Usuario.read(ctx.author.id) and Usuario.read(User.id):
            if ctx.author.id == User.id:
                await ctx.send("You can't donate to yourself")
            elif Usuario.read(ctx.author.id)["points"] >= amount:
                if amount <= 0:
                    await ctx.send("You can't donate zero or negative eggbux.")
                    return
                else:
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] - amount, Usuario.read(ctx.author.id)["roles"])
                    Usuario.update(User.id, Usuario.read(User.id)["points"] + amount, Usuario.read(User.id)["roles"])
                    await ctx.send(f"{ctx.author.mention} donated {amount} eggbux to {User.mention}")
            else:
                await ctx.send(f"{ctx.author.mention} doesn't have enough eggbux.")
        else:
            await ctx.send("You don't have permission to do this.")

    @commands.command("cassino", aliases=["roulette", "casino"])
    @pricing()
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
                    await ctx.send(f"{ctx.author.display_name} has won!")
                elif corSorteada == cor:
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + amount, Usuario.read(ctx.author.id)["roles"])
                    await ctx.send(f"{ctx.author.display_name} has won!")
                else:
                    await ctx.send(f"{ctx.author.display_name} lost, the selected color was {corSorteada} {corEmoji[corSorteada]}")                        
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] - amount, Usuario.read(ctx.author.id)["roles"])
                    return
            else:
                await ctx.send(f"{ctx.author.display_name} doesn't have enough eggbux or the amount is less than 50 eggbux.")
                return  
        else:
            await ctx.send("Select a valid color.")

    @cassino.error
    async def cassino_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please, insert the amount and the color.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Please, insert a valid amount.")
        else:
            await ctx.send("An unexpected error occurred.")

    @commands.command("stealPoints", aliases=["steal"])
    @pricing()
    async def stealPoints(self, ctx, User: discord.Member):
        if Usuario.read(ctx.author.id):
            chance  = randint(0, 100)
            if User.bot:
                await ctx.send("You can't steal from a bot.")
                await refund(ctx.author, ctx)
                return
            if Usuario.read(User.id):
                if ctx.author.id == User.id:
                    await ctx.send("You can't steal from yourself.")
                    await refund(ctx.author, ctx)
                elif chance >= 10: # 10% de chance de falhar
                    quantUser = Usuario.read(User.id)["points"]
                    randomInteiro = randint(0, int(quantUser/2)) # 50% do total de pontos do usuário
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + randomInteiro, Usuario.read(ctx.author.id)["roles"])
                    Usuario.update(User.id, Usuario.read(User.id)["points"] - randomInteiro, Usuario.read(User.id)["roles"])
                    await ctx.send(f"{ctx.author.mention} stole {randomInteiro} eggbux from {User.mention}")
                else:
                    await ctx.send(f"{ctx.author.mention} failed while trying to rob {User.mention}")
            else:
                await ctx.send("User not found in the database.")
                await refund(ctx.author, ctx)
        else:
            await ctx.send("You don't have permission to do this.")


    @commands.Cog.listener()
    async def on_voice_state_update(self, User: discord.Member, before, after):
        if User.bot:
            return
        if Usuario.read(User.id) and before.channel is None and after.channel is not None:
            await self.count_points(User)
        elif not Usuario.read(User.id) and before.channel is None and after.channel is not None:
            self.registrarAutomatico(User)
            if User.voice is not None:
                await self.count_points(User)
        elif Usuario.read(User.id) and before.channel is not None and after.channel is None:
            await self.update_points(User)

async def setup(bot):   
    await bot.add_cog(PointsCommands(bot))
            