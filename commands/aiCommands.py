import discord
from discord.ext import commands
from tools.pricing import pricing
from openai import OpenAI
from db.UserDB import Usuario

class AICommands(commands.Cog):

    def __init__(self, bot):
        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="lmstudio")
        self.bot = bot

    async def completionModel(self, role, content):
        history = [
            {"role": "system", "content": "Você é um membro do servidor ovomaltine. Você foi criado por Pedro e Alexius. Você tem o total direito de se defender, ou seja, se alguem o xingar, você pode xingar de volta. Você pode fazer piadas, ofendendo ou não. Gosta bastante de falar da situação política do brasil."},
            {"role": role, "content": content}
        ]
        while True:
            completion = self.client.chat.completions.create(
                model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
                messages=history,
                temperature=0.5,
                max_tokens=100,
                stream=True,
            )

            new_message = {"role": "system", "content": ""}

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
                    new_message["content"] += chunk.choices[0].delta.content
            
            history.append(new_message)
            break
            
        return history


    @commands.command()
    @pricing()
    async def amor(self, ctx, User: discord.Member, User2: discord.Member):
        if Usuario.read(ctx.author.id):
            history = await self.completionModel("user", f"faça uma história curta de amor de no máximo 50 palavras entre {User.display_name} e {User2.display_name} em português. Caso a história tenha um final, não continue ela.")
            await ctx.send(history[-1]["content"])
        else:
            await ctx.send("Você precisa se registrar para usar este comando.")


    @commands.command()
    async def speak(self, ctx, *, content):
        history = await self.completionModel("user", content)
        await ctx.send(history[-1]["content"])


async def setup(bot):
    await bot.add_cog(AICommands(bot))