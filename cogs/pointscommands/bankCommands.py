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
    async def deposit(self, ctx, amount: int):
        """Deposits points in the bank"""
        if Usuario.read(ctx.author.id) and amount > 0:
            if Bank.read(ctx.author.id):
                if amount > Usuario.read(ctx.author.id)["points"]:
                    await create_embed_without_title(ctx, f"{ctx.author.display_name} You don't have enough eggbux.")
                    return
                currentAmount = Bank.read(ctx.author.id)['bank']
                currentAmount += amount
                maxAmount = 5000
                if currentAmount > maxAmount:
                    await create_embed_without_title(ctx, f"{ctx.author.display_name} You can't have more than {maxAmount} eggbux in the bank.")
                else:
                    await create_embed_without_title(ctx, f":dollar: {ctx.author.display_name} You deposited {amount} eggbux in the bank.")
                    Usuario.update(ctx.author.id, Usuario.read(ctx.author.id)["points"] - amount, Usuario.read(ctx.author.id)["roles"])
                    Bank.update(ctx.author.id, currentAmount)
            else:
                await create_embed_without_title(ctx, f"{ctx.author.display_name}, since you didn't have an account, one was created for you. Try again.")
                await self.register_bank(ctx.author)
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You don't have permission to do this.")

    @commands.hybrid_command("withdraw", aliases=["with"], brief="Withdraws eggubux from the bank", parameters=["amount: int"], examples=["withdraw 1000"], description="Withdraws points from the bank.")
    @pricing()
    async def withdraw(self, ctx, amount: int):
        """Withdraws points from the bank"""
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

    @commands.hybrid_command("balance", aliases=["bal"], brief="Shows the balance of the bank account", parameters=["user: discord.Member"], examples=["balance @user"], description="Shows the balance of the bank account.")
    @pricing()
    async def balance(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        if Bank.read(user.id):
            await create_embed_without_title(ctx, f":bank: {user.display_name} has {Bank.read(user.id)['bank']} eggbux in the bank.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} doesn't have a bank account.")
    

async def setup(bot):
    await bot.add_cog(BankCommands(bot))
