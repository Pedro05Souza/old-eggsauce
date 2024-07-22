from discord.ext import commands
from tools.shared import create_embed_without_title, regular_command_cooldown
from db.bankDB import Bank
from db.userDB import User
from tools.pointscore import pricing
import discord
class BankCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def register_bank(self, User: discord.Member):
        """Registers the user in the bank database."""
        Bank.create(User.id, 0)

    @commands.hybrid_command("deposit", aliases=["dep"], brief="Deposits points in the bank", parameters=["amount: int"], description="Deposits points in the bank. You can't have more than 10000 eggbux in the bank.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def deposit(self, ctx, amount):
        """Deposits points in the bank"""
        user_data = User.read(ctx.author.id)
        if amount.upper() == "ALL":
            amount = user_data["points"]
        else:
            try:
                amount = int(amount)
            except ValueError:
                await create_embed_without_title(ctx, f"{ctx.author.display_name}, please enter a valid amount.")
                return
        if amount > 0:
            bank_data = Bank.read(ctx.author.id)
            if bank_data:
                if amount > user_data["points"]:
                    await create_embed_without_title(ctx, f"{ctx.author.display_name}, you don't have enough eggbux.")
                    return
                bankAmount = bank_data['bank']
                maxAmount = 10000 * bank_data['upgrades']
                if bankAmount >= maxAmount: 
                    await create_embed_without_title(ctx, f":bank: {ctx.author.display_name}, you can't have more than **{maxAmount}** eggbux in the bank.")
                    return
                if bankAmount + amount > maxAmount:
                    amount = maxAmount - bankAmount
                    if amount <= 0:
                        await create_embed_without_title(ctx, f":bank: {ctx.author.display_name}, you can't have more than **{maxAmount}** eggbux in the bank.")
                        return
                Bank.update(ctx.author.id, bankAmount + amount)
                User.update_points(ctx.author.id, user_data["points"] - amount)
                await create_embed_without_title(ctx, f":dollar: {ctx.author.display_name}, you deposited {amount} eggbux in the bank.")
                return
            else:
                await create_embed_without_title(ctx, f"{ctx.author.display_name}, since you didn't have an account, one was created for you. Try again.")
                await self.register_bank(ctx.author)
        else:
            await create_embed_without_title(ctx, f"{ctx.author.display_name}, please enter a valid amount.")

    @commands.hybrid_command("withdraw", aliases=["with"], brief="Withdraws eggubux from the bank", parameters=["amount: int"], examples=["withdraw 1000"], description="Withdraws points from the bank.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def withdraw(self, ctx, amount):
        """Withdraws points from the bank"""
        bank_data = Bank.read(ctx.author.id)
        if amount.upper() == "ALL":
            amount = bank_data["bank"]
        else:
            try:
                amount = int(amount)
            except ValueError:
                await create_embed_without_title(ctx, f"{ctx.author.display_name}, please enter a valid amount.")
                return
        if amount <= 0:
            await create_embed_without_title(ctx, f"{ctx.author.display_name}, please enter a valid amount.")
            return
        if bank_data:
            currentAmount = bank_data['bank']
            if currentAmount >= amount:
                await create_embed_without_title(ctx, f":dollar: {ctx.author.display_name} You withdrew {amount} eggbux from the bank.")
                Bank.update(ctx.author.id, currentAmount - amount)
                User.update_points(ctx.author.id, User.read(ctx.author.id)["points"] + amount)
            else:
                await create_embed_without_title(ctx, f"{ctx.author.display_name} You don't have enough eggbux in the bank.")
        else:
            await create_embed_without_title(ctx, f"{ctx.author.display_name}, since you didn't have an account, one was created for you. Try again.")
            await self.register_bank(ctx.author)
    
    @commands.hybrid_command("upgradebanklimit", aliases=["ubl"], brief="Upgrades the bank", description="Upgrades the bank. The bank can be upgraded up to 5 times.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def upgrade_bank_limit(self, ctx):
        """Upgrades the bank limit."""
        user_data = User.read(ctx.author.id)
        bank_data = Bank.read(ctx.author.id)
        if not bank_data:
            await create_embed_without_title(ctx, f"{ctx.author.display_name}, since you didn't have an account, one was created for you. Try again.")
            await self.register_bank(ctx.author)
            return
        if bank_data['upgrades'] == 5:
            await create_embed_without_title(ctx, f"{ctx.author.display_name}, you can't upgrade the bank anymore.")
            return
        upgrades_formula = 10000 * bank_data['upgrades']
        if user_data['points'] < upgrades_formula:
            await create_embed_without_title(ctx, f":bank: {ctx.author.display_name}, you currently have {bank_data['upgrades'] - 1} upgrades. You need **{upgrades_formula}** eggbux to upgrade the bank.")
            return
        User.update_points(ctx.author.id, user_data['points'] - upgrades_formula)
        upgrades = bank_data['upgrades'] + 1
        Bank.update_upgrades(ctx.author.id, upgrades)
        await create_embed_without_title(ctx, f":bank: {ctx.author.display_name}, you upgraded the bank to level {upgrades - 1}. Now you can have up to **{upgrades * 10000}** eggbux in the bank.")
        return
    
    

async def setup(bot):
    await bot.add_cog(BankCommands(bot))