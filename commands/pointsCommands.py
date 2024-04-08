from discord.ext import commands
from random import randint
import discord
from db.Usuario import Usuario
import asyncio
from tools.pricing import pricing

class PointsCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.voice is not None:
                    asyncio.create_task(self.count_points(member))

    @commands.Cog.listener()
    async def on_voice_state_update(self, User: discord.Member, before, after):
        if Usuario.read(User.id) and not User.bot and before.channel is None and after.channel is not None:
            await self.count_points(User)
        elif not Usuario.read(User.id) and before.channel is None and after.channel is not None:
            self.registrarAutomatico(User)
            if User.voice is not None:
                await self.count_points(User)

    async def count_points(self, User: discord.Member):
        if Usuario.read(User.id):
            while True:
                User = discord.utils.get(self.bot.get_all_members(), id=User.id)
                if User.voice is None:
                    break
                Usuario.update(User.id, Usuario.read(User.id)["points"] + 1)
                await asyncio.sleep(10)
                
        else:
            self.registrarAutomatico(User)
            await self.count_points(User)

    def registrarAutomatico(self, User: discord.Member):
        if Usuario.read(User.id) and User.bot:
            return
        else:
            Usuario.create(User.id, 0)
            print(f"Usuário criado: {User.name}")

        
    @commands.command()
    async def pontos(self, ctx, User: discord.Member = None):
        if User is None:
            await self.pontos(ctx, ctx.author)
        elif Usuario.read(User.id):
            await ctx.send(f"{User.mention} tem " + str(Usuario.read(User.id)["points"]) + " eggbux :money_with_wings:")
        else:
            await ctx.send(f"{User.mention} não tem eggbux!")

    @commands.command()
    async def verPontos(self, ctx, User: discord.Member = None):
        await self.pontos(ctx, User)
    

    @commands.command()
    async def shop(self, ctx):
        embed = discord.Embed(title="Shop", description="Compre comandos com seus eggbux:", color=0x00ff00)
        embed.add_field(name="1. Balls", value="50 eggbux", inline=False)
        embed.add_field(name="2. Mog", value="100 eggbux", inline=False)
        embed.add_field(name="3. mute (mutar um usuário)", value="150 eggbux", inline=False)
        embed.add_field(name="4. changeNickname", value="200 eggbux", inline=False)
        embed.add_field(name="5. purge (deletar até 25 mensagens no chat)", value="250 eggbux", inline=False)
        embed.add_field(name="6. kick (kickar um usuário)", value="350 eggbux", inline=False)
        embed.add_field(name="7. ban (banir um usuário)", value="450 eggbux", inline=False)
        embed.add_field(name="8. roubarPontos (Rouba no máximo 20%% da fortuna de eggbux de um usuário)", value="500 eggbux", inline=False)
        embed.add_field(name="9. Pardon (desbanir um usuário)", value="500 eggbux", inline=False)
        embed.add_field(name="10. Momento De silêncio (Muta todo mundo do server)", value="500 eggbux", inline=False)
        embed.add_field(name="11. implode (Desconecta geral da call)", value="750 eggbux", inline=False)
        embed.add_field(name= "12. explode (Deleta a call)", value="850 eggbux", inline=False)
        embed.add_field(name="12. god (Nunca é mutado por ninguém)", value="1000 eggbux", inline=False)
        await ctx.send(embed=embed)


    @commands.command()
    async def leaderboard(self, ctx):
        users = Usuario.readAll()
        users = sorted(users, key=lambda x: x["points"], reverse=True)
        embed = discord.Embed(title="Leaderboard", description="Ranking de eggbux", color=0x00ff00)
        for i in users:
            member = discord.utils.get(self.bot.get_all_members(), id=i["user_id"])
            embed.add_field(name=member.name, value=i["points"], inline=False)
        await ctx.send(embed=embed)


    @commands.command()
    @pricing()
    async def roubarPontos(self, ctx, User: discord.Member):
        chance  = randint(0, 100)
        if Usuario.read(ctx.author.id) and Usuario.read(User.id):
            if chance >= 10: # 10% de chance de falhar
                quantUser = Usuario.read(User.id)["points"]
                randomInteiro = randint(0, int(quantUser/5) + 1) # 20% do total de pontos do usuário
                Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + randomInteiro)
                Usuario.update(User.id, Usuario.read(User.id)["points"] - randomInteiro)
                await ctx.send(f"{ctx.author.mention} roubou {randomInteiro} eggbux de {User.mention}")
            else:
                await ctx.send(f"{ctx.author.mention} tentou roubar {User.mention}, mas falhou miseravelmente")

    # mod commands
    @commands.command()
    async def addPontos(self, ctx, amount: int, User: discord.Member = None):
        if User is None:
            User = ctx.author
            Usuario.update(User.id, Usuario.read(User.id)["points"] + amount)
            await ctx.send(f"{User.mention} recebeu {amount} eggbux")
        else:
            if Usuario.read(User.id):
                Usuario.update(User.id, Usuario.read(User.id)["points"] + amount)
                await ctx.send(f"{User.mention} recebeu {amount} eggbux")
            else:
                await ctx.send("Você não tem permissão para fazer isso")

        

    @commands.command()
    async def deleteDB(self, ctx,  User: discord.Member):
        if Usuario.read(User):
            Usuario.delete(User)
        else:
            ctx.send(f"{User} não está registrado no Banco de Dados!")


            
async def setup(bot):   
    await bot.add_cog(PointsCommands(bot))
            