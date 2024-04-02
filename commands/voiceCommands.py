# Description: Cog that contains commands that affect in some way the voice channels

from discord.ext import commands
import discord
import os
from dotenv import load_dotenv

class VoipCommands(commands.Cog):
    
    def __init__(self, bot):
        load_dotenv()
        self.bot = bot
        self.gods = []
        self.devs = os.getenv("DEVS").split(",")

    
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
        if user.top_role.position <= ctx.guild.me.top_role.position or str(user.id) in self.devs:
            self.gods.append(ctx.author)
            await ctx.send(f"{ctx.author} foi adicionado a lista de deuses")
            

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


async def setup(bot):
    await bot.add_cog(VoipCommands(bot))