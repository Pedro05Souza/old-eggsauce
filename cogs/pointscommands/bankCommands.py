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

    @commands.hybrid_command("deposit", aliases=["dep"], brief="Deposits points in the bank", parameters=["amount: int"], examples=["deposit 1000"], description="Deposits points in the bank. You can't have more than 5000 eggbux in the bank.")
    @pricing()
    async def deposit(self, ctx, amount):
        """Deposits points in the bank"""
        if amount.upper() == "ALL":
            amount = Usuario.read(ctx.author.id)["points"]
        else:
            try:
                amount = int(amount)
            except ValueError:
                await create_embed_without_title(ctx, f"{ctx.author.display_name}, please enter a valid amount.")
                return
        if amount > 0:
            if Bank.read(ctx.author.id):
                if amount > Usuario.read(ctx.author.id)["points"]:
                    await create_embed_without_title(ctx, f"{ctx.author.display_name}, you don't have enough eggbux.")
                    return
                bankAmount = Bank.read(ctx.author.id)['bank']
                maxAmount = 10000
                if bankAmount >= maxAmount: 
                    await create_embed_without_title(ctx, f":bank: {ctx.author.display_name}, you can't have more than 10000 eggbux in the bank.")
                    return
                if bankAmount + amount > maxAmount:
                    amount = maxAmount - bankAmount
                    if amount <= 0:
                        await create_embed_without_title(ctx, f":bank: {ctx.author.display_name}, you can't have more than 10000 eggbux in the bank.")
                        return
                Bank.update(ctx.author.id, bankAmount + amount)
                Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] - amount, Usuario.read(ctx.author.id)["roles"])
                await create_embed_without_title(ctx, f":dollar: {ctx.author.display_name}, you deposited {amount} eggbux in the bank.")
                return
            else:
                await create_embed_without_title(ctx, f"{ctx.author.display_name}, since you didn't have an account, one was created for you. Try again.")
                await self.register_bank(ctx.author)

    @commands.hybrid_command("withdraw", aliases=["with"], brief="Withdraws eggubux from the bank", parameters=["amount: int"], examples=["withdraw 1000"], description="Withdraws points from the bank.")
    @pricing()
    async def withdraw(self, ctx, amount):
        """Withdraws points from the bank"""
        if amount.upper() == "ALL":
            amount = Bank.read(ctx.author.id)['bank']
        else:
            try:
                amount = int(amount)
            except ValueError:
                await create_embed_without_title(ctx, f"{ctx.author.display_name}, please enter a valid amount.")
                return
        if Bank.read(ctx.author.id):
            currentAmount = Bank.read(ctx.author.id)['bank']
            if currentAmount >= amount:
                await create_embed_without_title(ctx, f":dollar: {ctx.author.display_name} You withdrew {amount} eggbux from the bank.")
                Bank.update(ctx.author.id, currentAmount - amount)
                Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] + amount, Usuario.read(ctx.author.id)["roles"])
            else:
                await create_embed_without_title(ctx, f"{ctx.author.display_name} You don't have enough eggbux in the bank.")
        else:
            await create_embed_without_title(ctx, f"{ctx.author.display_name}, since you didn't have an account, one was created for you. Try again.")
            await self.register_bank(ctx.author)

async def setup(bot):
    await bot.add_cog(BankCommands(bot))
