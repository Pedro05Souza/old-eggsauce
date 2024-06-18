import discord
import asyncio
from discord.ext import commands
from tools.pricing import pricing
from db.userDB import Usuario
from tools.embed import create_embed_without_title
from tools.processing import Processing

# This class is responsible for handling the AI commands.

class AICommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @pricing()
    async def love(self, ctx, User: discord.Member, User2: discord.Member):
        """Make a short love story between two users."""
        try:
            if Usuario.read(ctx.author.id):
                data = {"role": "user", "content":f"Make a short love story between {User.display_name} and {User2.display_name}. Don't write incomplete stories, Use a maximum of 100 tokens."}
                processing = Processing(data)
                processing.start()
                await asyncio.sleep(5)
                if processing.exception is None:
                    async with ctx.typing():
                        loop = asyncio.get_event_loop()
                        history = await loop.run_in_executor(None, processing.future.result)
                        content = "".join(chunk.choices[0].delta.content for chunk in history if chunk.choices[0].delta.content is not None)
                        if(len(content) > 0):
                            await ctx.send(content)
                        else:
                            await create_embed_without_title(ctx, ":no_entry_sign: Error! AI didn't generate content.")
                else:
                    await create_embed_without_title(ctx, ":no_entry_sign: Api connection failed. Probably due to the AI model being deactivated. Try again later.")
            else:
                await create_embed_without_title(ctx, ":no_entry_sign: You are not registered in the database.")
        except Exception:
            await create_embed_without_title(ctx, ":no_entry_sign: An unexpected problem occurred!")

    @commands.command()
    @pricing()
    async def speak(self, ctx, *content):
        """Make the AI say something."""
        try:
            content = " ".join(content)
            data ={"role" : "user", "content" : content + ". Preferably send a short message. If the user message requires more, write more than one message."}
            processing = Processing(data)
            processing.start()
            await asyncio.sleep(5)
            if processing.exception is None:
                async with ctx.typing():
                    loop = asyncio.get_event_loop()
                    history = await loop.run_in_executor(None, processing.future.result)
                    content = "".join(chunk.choices[0].delta.content for chunk in history if chunk.choices[0].delta.content is not None)
                    if(len(content) > 0):
                        await ctx.send(content)
                    else:
                        await create_embed_without_title(ctx, ":no_entry_sign: Error! AI didn't generate content.")
            else:
                await create_embed_without_title(ctx, ":no_entry_sign: Api connection failed. Probably due to the AI model being deactivated. Try again later.")
        except Exception as e:
           await create_embed_without_title(ctx, ":no_entry_sign: An unexpected problem occurred!")
           print(e)
        
async def setup(bot):
    await bot.add_cog(AICommands(bot))