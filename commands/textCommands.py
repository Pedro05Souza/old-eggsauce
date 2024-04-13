# Description: cog that contains administration and fun commands
from discord.ext import commands
import discord
from db.UserDB import Usuario
import os
import random
from tools.pricing import pricing, refund

class TextCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        bot.remove_command('help')

    @commands.command()
    @pricing()
    async def balls(self, ctx):
        await ctx.send("balls")

    @commands.command()
    @pricing()
    async def mog(self, ctx, User: discord.Member):
            path = random.choice(os.listdir("images/mogged/"))
            await ctx.send(file=discord.File("images/mogged/"+path))
            await ctx.send(f"{User.mention} bye bye 🤫🧏‍♂️")

    @commands.command()
    @pricing()
    async def purge(self, ctx, amount: int):
        if amount > 0 and amount <= 25:
            await ctx.channel.purge(limit=amount + 1)
        else:
            await ctx.send("Por favor, insira um número menor ou igual a 25 e maior que 0.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def kick(self, ctx, User: discord.Member):
        if User.id == ctx.author.id:
                await ctx.send("Você não pode se kickar.")
                await refund(ctx.author, ctx) 
                return
        if User.top_role.position <= ctx.guild.me.top_role.position:
            await User.kick()
            await ctx.send(f"{User.mention} foi kickado")
        else:
            await ctx.send("Você não tem permissão para fazer isso.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def ban(self, ctx, User: discord.Member):
        if User.id == ctx.author.id:
                await ctx.send("Você não pode se banir.")
                await refund(ctx.author, ctx)
                return
        if User.top_role.position <= ctx.guild.me.top_role.position:
            await User.kick()
            await ctx.send(f"{User.mention} foi kickado")
        else:
            await ctx.send("não tenho permissão para fazer isso.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def mudarApelido(self, ctx, User: discord.Member, *, apelido: str):
        if User.top_role.position <= ctx.guild.me.top_role.position:
            if User.id == ctx.me.id:
                await ctx.send("Eu não posso mudar meu próprio apelido.")
                await refund(ctx.author, ctx)
                return
            else:
                await User.edit(nick=apelido)
                await ctx.send(f"Apelido de {User.mention} foi alterado para {apelido}")   
        else:
            await refund(ctx.author, ctx)
            await ctx.send("Você não pode alterar o apelido de um usuário com cargo maior ou igual ao meu.")

    @commands.command()
    @pricing()
    async def perdoar(self, ctx, id: str):
        User = await self.bot.fetch_user(id)
        if await ctx.guild.fetch_ban(User):
            await ctx.guild.unban(User)
            await ctx.send(f"{User.mention} foi perdoado")
        else:
            await ctx.send("Este usuário não está banido")
            await refund(ctx.author, ctx)

    @commands.command()
    async def cargoPobre(self, ctx):
         if Usuario.read(ctx.author.id):    
             permissions = discord.Permissions(
                 mute_members = True,
                 deafen_members = True,
             )
             role = discord.utils.get(ctx.guild.roles, name="pobre que acha que é rico")
             if role is None:
                    role = await ctx.guild.create_role(name="pobre que acha que é rico", permissions=permissions, color=discord.Color.from_rgb(165, 42, 42))
             if ctx.author in role.members:
                    await ctx.send("Você já tem esse cargo.")
                    return
             await ctx.author.add_roles(role)
             await ctx.send(f"{ctx.author.mention} agora tem um cargo podre.")


                  
async def setup(bot):
    await bot.add_cog(TextCommands(bot))