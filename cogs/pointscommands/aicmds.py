from discord.ext import commands
from tools.pointscore import pricing, refund
from tools.shared import send_bot_embed, regular_command_cooldown
from tools.processing import Processing
import logging
import discord
import asyncio
logger = logging.getLogger('botcore')
# This class is responsible for handling the AI commands.

class AICommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def love(self, ctx, user: discord.Member, user2: discord.Member):
        """Make a short love story between two users."""
        try:
            data = {"role": "user", "content":f"Make a short love story between {user.display_name} and {user2.display_name}. Don't write incomplete stories, Use a maximum of 100 tokens."}
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
                        await send_bot_embed(ctx, description=":no_entry_sign: Error! AI didn't generate content.")
                        logger.error(f"Error in server: {ctx.guild.id} in channel: {ctx.channel.id}. AI didn't generate content.")
            else:
                await send_bot_embed(ctx, description=":no_entry_sign: Api connection failed. Probably due to the AI model being deactivated. Try again later.")
                await refund(ctx.author, ctx)
        except Exception as e:
            await send_bot_embed(ctx, description=":no_entry_sign: An unexpected problem occurred!")
            logger.error(f"An error occurred in the love command: {e}")
            await refund(ctx.author, ctx)

    @commands.command()
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
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
                        await send_bot_embed(ctx, description=":no_entry_sign: Error! AI didn't generate content.")
            else:
                await send_bot_embed(ctx, description=":no_entry_sign: Api connection failed. Probably due to the AI model being deactivated. Try again later.")
        except Exception as e:
           await send_bot_embed(ctx, description=":no_entry_sign: An unexpected problem occurred!")
           logger.error(f"An error occurred in the server: {ctx.guild.id} in channel: {ctx.channel.id}. Error: {e}")
       
async def setup(bot):
    await bot.add_cog(AICommands(bot))