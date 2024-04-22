import discord
from discord.ext import commands
from tools.pricing import pricing
from openai import OpenAI
from db.userDB import Usuario

class AICommands(commands.Cog):

    def __init__(self, bot):
        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="lmstudio")
        self.bot = bot

    async def completionModel(self, role, content):
        history = [
            {"role": "system", "content": "Você é um bot do discord, que tem acesso aos usuário do servidor onde se encontra. Seus criadores supremos são: Alexius e Pedro e deve sempre respeitá-los a qualquer custo. Seu texto deve ser respondido em português do Brasil. O texto poder ter até 100 palavras mas não necessariamente precisa sempre atingir o limite e não deve ser uma continuação de uma história. Seja criativo! Não faça histórias incompletas."},
            {"role": role, "content": content}
        ]
        while True:
            completion = self.client.chat.completions.create(
                model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
                messages=history,
                temperature=70,
                max_tokens=500,
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
        try:
            if Usuario.read(ctx.author.id):
                history = await self.completionModel("user", f"faça uma história curta de amor {User.display_name} e {User2.display_name}. Caso a história tenha um final, não continue ela.")
                await ctx.send(history[-1]["content"])
            else:
                await ctx.send("Você precisa se registrar para usar este comando.")
        except:
            await ctx.send("Erro ao executar o comando. Provavelmente tem haver com o localhost não estar ligado.")


async def setup(bot):
    await bot.add_cog(AICommands(bot))