import discord
import asyncio
from discord.ext import commands
from tools.pricing import pricing
from db.userDB import Usuario
from tools.processing import Processing

# This class is responsible for handling the AI commands.
class AICommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @pricing()
    async def love(self, ctx, User: discord.Member, User2: discord.Member):
        try:
            if Usuario.read(ctx.author.id):
                async with ctx.typing():
                    data = {"role": "user", "content":f"Make a short love story between {User.display_name} and {User2.display_name}. Don't write incomplete stories, Use a maximum of 100 tokens."}
                    processing = Processing(data)
                    processing.start()
                    loop = asyncio.get_event_loop()
                    history = await loop.run_in_executor(None, processing.future.result)
                    content = "".join(chunk.choices[0].delta.content for chunk in history if chunk.choices[0].delta.content is not None)
                    if(len(content) > 0):
                        await ctx.send(content)
                    else:
                        await ctx.send("Error! AI didn't generate content.")
            else:
                await ctx.send("You need to be registered to use this command. Join any voice channels to register.")
        except Exception as e:
            ctx.send("An unexpected problem occurred!")

    @commands.command()
    @pricing()
    async def speak(self, ctx, *, content):
        try:
            async with ctx.typing():
                data ={"role" : "user", "content" : content + ". Prefelaby send a short message. If the user message requires more, write more than one message."}
                processing = Processing(data)
                processing.start()
                loop = asyncio.get_event_loop()
                history = await loop.run_in_executor(None, processing.future.result)
                content = "".join(chunk.choices[0].delta.content for chunk in history if chunk.choices[0].delta.content is not None)
                if(len(content) > 0):
                    await ctx.send(content)
                else:
                    await ctx.send("Error! AI didn't generate content.")
        except Exception as e:
            ctx.send("An unexpected problem occurred!")

        
async def setup(bot):
    await bot.add_cog(AICommands(bot))