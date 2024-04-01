# Description: Cog que contém comandos de administração e diversão
from discord.ext import commands
import discord
import os


class CommandsCog(commands.Cog):
   
    def __init__(self, bot):
        self.bot = bot
        bot.remove_command('help')
        self.gods = []
        self.devs = os.getenv("DEVS").split(",")


    @commands.command()
    async def balls(self, ctx):
        await ctx.send("Hey doc")


    @commands.command()
    async def changeNickname(self, ctx, User: discord.Member, apelido: str):
        if User.top_role.position <= ctx.guild.me.top_role.position:
            await User.edit(nick=apelido)
            await ctx.send(f"Nickname changed to {apelido} for {User}")

        else:
            await ctx.send(f"User {User} has higher role than you")


    @commands.command()
    async def mogged(self, ctx, User: discord.Member):
            File = discord.File("mogged.png", filename="mogged.png")
            await ctx.send(file=File)
            await ctx.send(ctx.author.mention + " moggou " + User.mention + "!")

    @commands.command()
    async def momentoDeSilencio(self, ctx):
        servidor = ctx.me.guild
        user = ctx.author
        if user.id == servidor.owner_id or user.id in self.devs:
            for canal in servidor.voice_channels:
                for membro in canal.members:
                        if canal.name == "shffgjfj":
                                await membro.edit(mute=True)
                        await membro.edit(mute=True)
        
    @commands.command()
    async def god(self, ctx):
        user = ctx.author
        if user.top_role.position <= ctx.guild.me.top_role.position:
            self.gods.append(ctx.author)
            await ctx.send(f"{ctx.author} foi adicionado a lista de deuses")


    @commands.command()
    async def implode(self, ctx):
        user = ctx.author
        channel = user.voice.channel
        if user.top_role.position <= ctx.guild.me.top_role.position and channel is not None:
            for member in channel.members:
                await member.move_to(None)
            
            

    @commands.command()
    async def radinho(self, ctx):
        servidor = ctx.me.guild
        user = ctx.author
        channel = user.voice.channel #channel
        if user.id == servidor.owner_id or user.id in self.devs and user.voice is not None and user.voice.channel is not None: 
            await channel.edit(bitrate = 8000)



    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member in self.gods and not before.mute and after.mute:
            await member.edit(mute=False)
            print(f"{member.name} foi mutado, mas era um Deus e foi desmutado")
        if member in self.gods and not before.deaf and after.deaf:
            await member.edit(deafen=False)
            print(f"{member.name} foi ensurdecido, mas era um Deus e foi desensurdecido")
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Lista de comandos do commands", description="Hey", color=0xeee657)

        embed.add_field(name="mogged", value="Moga outro usuário", inline=False)
        embed.add_field(name="changeNickname", value="Muda o nome", inline=False)
        embed.add_field(name="balls", value="Hey doc", inline=False)

        
        await ctx.send(embed=embed)

async def setup(bot):
    bot.add_cog(CommandsCog(bot))