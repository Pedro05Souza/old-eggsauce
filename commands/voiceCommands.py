# Description: Cog that contains commands that affect in some way the voice channels

from discord.ext import commands
from db.Usuario import Usuario
import os
from dotenv import load_dotenv
from tools.pricing import pricing, Prices

class VoipCommands(commands.Cog):
    
    def __init__(self, bot):
        load_dotenv()
        self.bot = bot
        self.gods = []
        self.devs = os.getenv("DEVS").split(",")

    
    @commands.command()
    @pricing()
    async def momentoDeSilencio(self, ctx):
        servidor = ctx.me.guild
        user = ctx.author
        if user.voice.channel is not None:
            for membro in user.voice.channel.members:
                await membro.edit(mute = True)
        else:
            await ctx.send("Você não está em um canal de voz.")
            Usuario.update(user.id, Usuario.read(user.id)["points"] + Prices.momentoDeSilencio.value)

    @commands.command()
    @pricing()
    async def god(self, ctx):
        user = ctx.author
        if user not in self.gods:
            self.gods.append(ctx.author)
            await ctx.send(f"{ctx.author.mention} foi adicionado a lista de deuses", ephemeral=True)
        elif user in self.gods:
            await ctx.send(f"{user.mention} já é um deus", ephemeral=True)
            

    @commands.command()
    @pricing()
    async def radinho(self, ctx):
        servidor = ctx.me.guild
        user = ctx.author
        channel = user.voice.channel #channel
        if user.voice.channel is not None: 
            await channel.edit(bitrate = 8000)
        else:
            await ctx.send("Você não está em um canal de voz.")
            Usuario.update(user.id, Usuario.read(user.id)["points"] + Prices.radinho.value)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member in self.gods and not before.mute and after.mute:
            await member.edit(mute=False)
            print(f"{member.name} foi mutado, mas era um Deus e foi desmutado")
        if member in self.gods and not before.deaf and after.deaf:
            await member.edit(deafen=False)
            print(f"{member.name} foi ensurdecido, mas era um Deus e foi desensurdecido")



async def setup(bot):
    await bot.add_cog(VoipCommands(bot))