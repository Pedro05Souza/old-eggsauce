# Description: cog that contains administration and fun commands
import asyncio
from discord.ext import commands
import discord
from db.userDB import Usuario
from db.channelDB import ChannelDB
import os
import random
from tools.pricing import pricing, refund

# This class is responsible for handling the text commands.
class TextCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        bot.remove_command('help')

    @commands.Cog.listener()
    async def on_ready(self):
        asyncio.create_task(self.work_periodically())


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
            await ctx.send("Please, insert a number between 1 and 25.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def kick(self, ctx, User: discord.Member):
        if User.id == ctx.author.id:
                await ctx.send("You can't kick yourself.")
                await refund(ctx.author, ctx) 
                return
        if User.top_role.position <= ctx.guild.me.top_role.position:
            await User.kick()
            await ctx.send(f"{User.mention} was kicked.")
        else:
            await ctx.send("I don't have permission to do that.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def ban(self, ctx, User: discord.Member):
        if User.id == ctx.author.id:
                await ctx.send("You can't ban yourself.")
                await refund(ctx.author, ctx)
                return
        if User.top_role.position <= ctx.guild.me.top_role.position:
            await User.ban()
            await ctx.send(f"{User.mention} was banned.")
        else:
            await ctx.send("I don't have permission to do that.")
            await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def changeNickname(self, ctx, User: discord.Member, *, apelido: str):
        if User.top_role.position <= ctx.guild.me.top_role.position:
            if User.id == ctx.me.id:
                await ctx.send("I can't change my own nickname.")
                await refund(ctx.author, ctx)
                return
            else:
                await User.edit(nick=apelido)
                await ctx.send(f"{User.mention}'s nickname has changed to {apelido}.")   
        else:
            await refund(ctx.author, ctx)
            await ctx.send("I don't have permission to do that.")

    @commands.command()
    @pricing()
    async def pardon(self, ctx, id: str):
        User = await self.bot.fetch_user(id)
        if await ctx.guild.fetch_ban(User):
            await ctx.guild.unban(User)
            await ctx.send(f"{User.mention} has been unbanned.")
        else:
            await ctx.send("This user is not banned.")
            await refund(ctx.author, ctx)
            
    @commands.command()
    @pricing()
    async def lowWageRole(self, ctx):
         if Usuario.read(ctx.author.id):    
            permissions = discord.Permissions(
                move_members = True,
            )
            role = discord.utils.get(ctx.guild.roles, name="low wage worker")
            if role is None:
                role = await ctx.guild.create_role(name="low wage worker", permissions=permissions, color=discord.Color.from_rgb(165, 42, 42))
                await role.edit(position=9, hoist=True, mentionable=True)
            if ctx.author in role.members:
                await ctx.send("You already have this role.")
                return
            if Usuario.read(ctx.author.id)["roles"] == "":
                await ctx.author.add_roles(role)
                await ctx.send(f"{ctx.author.mention} received the low wage worker role.")


    @commands.command()
    @pricing()
    async def lowClassRole(self, ctx):
        if Usuario.read(ctx.author.id):    
             permissions = discord.Permissions(
                 move_members = True,
                 mute_members = True,
                 deafen_members = True
             )
             role = discord.utils.get(ctx.guild.roles, name="Peasant")
             if role is None:
                    role = await ctx.guild.create_role(name="Peasant", permissions=permissions, color=discord.Color.from_rgb(255, 0, 0))
                    await role.edit(position=8, hoist=True, mentionable=True)
             if ctx.author in role.members:
                    await ctx.send("You already have this role.")
                    await refund(ctx.author, ctx)
                    return
             if Usuario.read(ctx.author.id)["roles"] == "T":
                await ctx.author.add_roles(role)
                await ctx.send(f"{ctx.author.mention} received the low class role.")
             else:
                await ctx.send("You don't have one or more of the necessary roles.")
                await refund(ctx.author, ctx)   

    @commands.command()
    @pricing()
    async def middleClassRole(self, ctx):
        if Usuario.read(ctx.author.id):    
             permissions = discord.Permissions(
                 move_members = True,
                 mute_members = True,
                 deafen_members = True,
                 manage_messages = True
             )
             role = discord.utils.get(ctx.guild.roles, name="brokie who thinks they are rich")
             if role is None:
                    role = await ctx.guild.create_role(name="brokie who thinks they are rich", permissions=permissions, color=discord.Color.from_rgb(0, 0, 255))
                    await role.edit(position=7, hoist=True, mentionable=True)
             if ctx.author in role.members:
                    await ctx.send("You already have this role.")
                    await refund(ctx.author, ctx)
                    return
             if Usuario.read(ctx.author.id)["roles"] == "TB":
                await ctx.author.add_roles(role)
                await ctx.send(f"{ctx.author.mention} received the middle class role.")
             else:
                    await ctx.send("You don't have one or more of the necessary roles.")
                    await refund(ctx.author, ctx)

    @commands.command()
    @pricing()
    async def highClassRole(self, ctx):
         if Usuario.read(ctx.author.id):    
             permissions = discord.Permissions(
                 move_members = True,
                 mute_members = True,
                 deafen_members = True,
                 manage_messages = True,
                 manage_channels = True
             )
             role = discord.utils.get(ctx.guild.roles, name="magnate")
             if role is None:
                    role = await ctx.guild.create_role(name="magnate", permissions=permissions, color=discord.Color.from_rgb(0, 0, 0))
                    await role.edit(position=6, hoist=True, mentionable=True)
             if ctx.author in role.members:
                    await ctx.send("You already have this role.")
                    await refund(ctx.author, ctx)
                    return
             if Usuario.read(ctx.author.id)["roles"] == "TBM":
                await ctx.author.add_roles(role)
                await ctx.send(f"{ctx.author.mention} received the high class role.")
             else:
                  await ctx.send("You don't have one or more of the necessary roles.")
                  await refund(ctx.author, ctx)

    def salarioCargo(self, User:discord.Member):
        salarios = {
            "T": 50,
            "B": 100,
            "M": 200,
            "A": 300
        }
        if Usuario.read(User.id):
            return salarios[Usuario.read(User.id)["roles"] [-1]]
        else:
            return 0
        
    async def work_periodically(self):
        while True:
            for guild in self.bot.guilds:
                for member in guild.members:
                        user_data = Usuario.read(member.id)
                        if user_data:
                            if user_data["roles"] != "":
                                Usuario.update(member.id, Usuario.read(member.id)["points"] + self.salarioCargo(member), Usuario.read(member.id)["roles"])
                await asyncio.sleep(1600)

    @commands.command()
    async def salary(self, ctx, User: discord.Member = None):
        if User is None:
            User = ctx.author
        user_data = Usuario.read(User.id)
        if user_data:
            if user_data["roles"] != "":
                await ctx.send(f"{User.display_name} earns {self.salarioCargo(User)} eggbux of salary.")
                return   
            await ctx.send(f"{User.display_name} doesn't have a custom role that receives a salary.")
        else:
            await ctx.send(f"{User.display_name} is not registered in the database.")
            await refund(ctx.author, ctx)
            
    @commands.command()
    async def nuke(self, ctx):
         await Usuario.deleteAll()
              
async def setup(bot):
    await bot.add_cog(TextCommands(bot))