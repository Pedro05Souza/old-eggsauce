from discord.ext import commands
from tools.embed import create_embed_without_title
from db.bankDB import Bank
from db.userDB import Usuario
import discord
from tools.pricing import pricing


class BankCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def register_bank(self, User: discord.Member):
        """Registers the user in the bank database."""
        Bank.create(User.id, 0)

    @commands.command("deposit", aliases=["dep"])
    @pricing()
    async def deposit(self, ctx, amount: int):
        """Deposits points in the bank"""
        if Usuario.read(ctx.author.id) and amount > 0:
            if Bank.read(ctx.author.id):
                if amount > Usuario.read(ctx.author.id)["points"]:
                    await create_embed_without_title(ctx, f"{ctx.author.display_name} You don't have enough eggbux.")
                    return
                currentAmount = Bank.read(ctx.author.id)['bank']
                currentAmount += amount
                if currentAmount >= 1000:
                    await create_embed_without_title(ctx, f"{ctx.author.display_name} You can't have more than 1000 eggbux in the bank.")
                else:
                    await create_embed_without_title(ctx, f"{ctx.author.display_name} You deposited {amount} eggbux in the bank.")
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] - amount, Usuario.read(ctx.author.id)["roles"])
                    Bank.update(ctx.author.id, currentAmount + amount)
            else:
                await create_embed_without_title(ctx, f"{ctx.author.display_name}, since you didn't have an account, one was created for you. Try again.")
                await self.register_bank(ctx.author)
        else:
            await create_embed_without_title(ctx, f"{ctx.author.display_name} You don't have permission to do this.")

    @commands.command("withdraw", aliases=["with"])
    @pricing()
    async def withdraw(self, ctx, amount: int):
        """Withdraws points from the bank"""
        if Bank.read(ctx.author.id):
            currentAmount = Bank.read(ctx.author.id)['bank']
            if currentAmount >= amount:
                await create_embed_without_title(ctx, f"{ctx.author.display_name} You withdrew {amount} eggbux from the bank.")
                Bank.update(ctx.author.id, currentAmount - amount)
                Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + amount, Usuario.read(ctx.author.id)["roles"])
            else:
                await create_embed_without_title(ctx, f"{ctx.author.display_name} You don't have enough eggbux in the bank.")
        else:
            await create_embed_without_title(ctx, f"{ctx.author.display_name}, since you didn't have an account, one was created for you. Try again.")
            await self.register_bank(ctx.author)

    @commands.command("balance", aliases=["bal"])
    @pricing()
    async def balance(self, ctx, User: discord.Member = None):
        if User is None:
            User = ctx.author
        if Bank.read(User.id):
            await create_embed_without_title(ctx, f":bank: {User.display_name} has {Bank.read(User.id)['bank']} eggbux in the bank.")
        else:
            await create_embed_without_title(ctx, f"{User.display_name} doesn't have a bank account.")

async def setup(bot):
    await bot.add_cog(BankCommands(bot))
