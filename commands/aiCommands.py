import discord
import asyncio
from discord.ext import commands
from tools.pricing import pricing
from db.userDB import Usuario
from tools.processing import Processing

class AICommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @pricing()
    async def amor(self, ctx, User: discord.Member, User2: discord.Member):
        try:
            if Usuario.read(ctx.author.id):
                async with ctx.typing():
                    data = {"role": "user", "content":f"faça uma história curta de amor entre {User.display_name} e {User2.display_name}. Não escreva histórias incompletas, use no máximo seu limite de tokens que é de 100."}
                    processing = Processing(data)
                    processing.start()
                    loop = asyncio.get_event_loop()
                    history = await loop.run_in_executor(None, processing.future.result)
                    content = "".join(chunk.choices[0].delta.content for chunk in history if chunk.choices[0].delta.content is not None)
                    if(len(content) > 0):
                        await ctx.send(content)
                    else:
                        await ctx.send("Erro! AI não gerou conteúdo.")
            else:
                await ctx.send("Você precisa se registrar para usar este comando.")
        except Exception as e:
            ctx.send("Ocorreu um problema inesperado!")

    @commands.command()
    async def speak(self, ctx, *, content):
        try:
            async with ctx.typing():
                data ={"role" : "user", "content" : content + ". De preferência escreva mensagens curtas."}
                processing = Processing(data)
                processing.start()
                loop = asyncio.get_event_loop()
                history = await loop.run_in_executor(None, processing.future.result)
                content = "".join(chunk.choices[0].delta.content for chunk in history if chunk.choices[0].delta.content is not None)
                if(len(content) > 0):
                    await ctx.send(content)
                else:
                    await ctx.send("Erro! AI não gerou conteúdo.")
        except Exception as e:
            ctx.send("Ocorreu um problema inesperado!")

        


async def setup(bot):
    await bot.add_cog(AICommands(bot))