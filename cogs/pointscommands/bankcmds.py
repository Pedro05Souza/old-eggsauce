"""
This module contains the bank commands.
"""
from discord.ext import commands
from tools.shared import send_bot_embed, confirmation_embed
from tools.settings import REGULAR_COOLDOWN
from db.bankDB import Bank
from db.userDB import User
from tools.pointscore import pricing
from tools.listeners import on_user_transaction
from discord.ext.commands import Context
import discord
class BankCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def register_bank(self, User: discord.Member):
        """Registers the user in the bank database."""
        Bank.create(User.id, 0)

    @commands.hybrid_command("deposit", aliases=["dep"], brief="Deposits points in the bank", parameters=["amount: int"], description=f"Deposits points in the bank.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def deposit(self, ctx: Context, amount) -> None:
        """Deposits points in the bank"""
        user_data = ctx.data["user_data"]
        if amount.upper() == "ALL":
            amount = user_data["points"]
        else:
            try:
                amount = int(amount)
            except ValueError:
                await send_bot_embed(ctx, description=f"{ctx.author.display_name}, please enter a valid amount.")
                return
        if amount > 0:
            bank_data = ctx.data["bank_data"]
            if amount > user_data["points"]:
                await send_bot_embed(ctx, description=f"{ctx.author.display_name}, you don't have enough eggbux.")
                return
            bankAmount = bank_data['bank']
            maxAmount = 10000 * bank_data['upgrades']
            if bankAmount >= maxAmount: 
                await send_bot_embed(ctx, description=f":bank: {ctx.author.display_name}, you can't have more than **{maxAmount}** eggbux in the bank.")
                return
            if bankAmount + amount > maxAmount:
                amount = maxAmount - bankAmount
                if amount <= 0:
                    await send_bot_embed(ctx, description=f":bank: {ctx.author.display_name}, you can't have more than **{maxAmount}** eggbux in the bank.")
                    return
            Bank.update(ctx.author.id, bankAmount + amount)
            User.update_points(ctx.author.id, user_data["points"] - amount)
            await send_bot_embed(ctx, description=f":dollar: {ctx.author.display_name}, you deposited {amount} eggbux in the bank.")
            await on_user_transaction(ctx, amount, 1)
            return
        else:
            await send_bot_embed(ctx, description=f"{ctx.author.display_name}, please enter a valid amount.")

    @commands.hybrid_command("withdraw", aliases=["with"], brief="Withdraws eggubux from the bank", parameters=["amount: int"], examples=["withdraw 1000"], description="Withdraws points from the bank.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def withdraw(self, ctx: Context, amount) -> None:
        """Withdraws points from the bank"""
        bank_data = ctx.data["bank_data"]
        if amount.upper() == "ALL":
            amount = bank_data["bank"]
        else:
            try:
                amount = int(amount)
            except ValueError:
                await send_bot_embed(ctx, description=f"{ctx.author.display_name}, please enter a valid amount.")
                return
        if amount <= 0:
            await send_bot_embed(ctx, description=f"{ctx.author.display_name}, please enter a valid amount.")
            return
        currentAmount = bank_data['bank']
        if currentAmount >= amount:
            await send_bot_embed(ctx, description=f":dollar: {ctx.author.display_name} You withdrew {amount} eggbux from the bank.")
            Bank.update(ctx.author.id, currentAmount - amount)
            User.update_points(ctx.author.id, User.read(ctx.author.id)["points"] + amount)
            await on_user_transaction(ctx, amount, 0)
        else:
            await send_bot_embed(ctx, description=f"{ctx.author.display_name} You don't have enough eggbux in the bank.")
            return
    
    @commands.hybrid_command("upgradebanklimit", aliases=["ubl"], brief="Upgrades the bank", description="Upgrades the bank. The bank can be upgraded up to 5 times.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def upgrade_bank_limit(self, ctx: Context) -> None:
        """Upgrades the bank limit."""
        user_data = ctx.data["user_data"]
        bank_data = ctx.data["bank_data"]
        upgrades_formula = 10000 * bank_data['upgrades']
        if user_data['points'] < upgrades_formula:
            await send_bot_embed(ctx, description=f":bank: {ctx.author.display_name}, you currently have {bank_data['upgrades'] - 1} upgrades. You need **{upgrades_formula}** eggbux to upgrade the bank.")
            return
        confirmation = await confirmation_embed(ctx, ctx.author, f"{ctx.author.display_name}, are you sure you want to upgrade the bank to level **{bank_data['upgrades']}** for **{upgrades_formula}** eggbux?")
        if confirmation:
            User.update_points(ctx.author.id, user_data['points'] - upgrades_formula)
            upgrades = bank_data['upgrades'] + 1
            Bank.update_upgrades(ctx.author.id, upgrades)
            await send_bot_embed(ctx, description=f":bank: {ctx.author.display_name}, you upgraded the bank to level {upgrades - 1}. Now you can have up to **{upgrades * 10000}** eggbux in the bank.")
            await on_user_transaction(ctx, upgrades_formula, 1)
            return
        else:
            await send_bot_embed(ctx, description=f"{ctx.author.display_name}, you have cancelled the bank upgrade.")
            return
        
async def setup(bot):
    await bot.add_cog(BankCommands(bot))