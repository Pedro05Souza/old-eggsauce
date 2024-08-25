"""
This file contains the corn commands for the chicken food farm.
"""

from discord.ext import commands
from db.farmDB import Farm
from db.userDB import User
from tools.chickens.chickeninfo import ChickenFood
from tools.shared import send_bot_embed, make_embed_object, confirmation_embed, return_data
from tools.settings import regular_command_cooldown, max_corn_limit, max_plot_limit, farm_drop
from tools.pointscore import pricing
from tools.chickens.chickenshared import preview_corn_produced, update_player_corn
from tools.listeners import on_user_transaction
from better_profanity import profanity
from discord.ext.commands import Context
import discord

class CornCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="cornfield", aliases=["c", "corn"], usage="chickenfood", descripton="Opens the food farm to generated food for the chickens.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def corn_field(self, ctx: Context, user: discord.Member = None) -> None:
        """Displays the user's corn field."""
        data, user = await return_data(ctx, user)
        if data:
            await ctx.send(embed=await self.show_plr_food_farm(ctx, user, data))
    
    @commands.hybrid_command(name="renamecornfield", aliases=["rcf"], usage="renameCornfield <nickname>", description="Rename the cornfield.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def rename_corn_field(self, ctx: Context, nickname: str) -> None:
        """Rename the cornfield"""
        farm_data = ctx.data["farm_data"]
        censor = profanity.contains_profanity(nickname)
        if censor:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} The cornfield name contains profanity.")
            return
        if len(nickname) > 20:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} The cornfield name must have a maximum of 15 characters.")
            return
        farm_data['plant_name'] = nickname
        Farm.update(ctx.author.id, plant_name=nickname)
        await send_bot_embed(ctx, description=f"{ctx.author.display_name} Your cornfield has been renamed to {nickname}.")

    async def show_plr_food_farm(self, ctx: Context, user: discord.Member, data: dict) -> discord.Embed:
        """Show the player's food farm"""
        if not data.get("farm_data", None):
            return await make_embed_object(title=f":no_entry_sign: {user.display_name}", description=f":no_entry_sign: {user.display_name} You don't have a farm.")
        farm_data = data["farm_data"]
        if user.id != ctx.author.id:
            farm_data['corn'] = await update_player_corn(user, farm_data)
        food_embed = await make_embed_object(title=f":corn: {farm_data['plant_name']}", description=f":corn: Corn balance: {farm_data['corn']}/{farm_data['corn_limit']}\n:moneybag: Corn expected to generate in **{farm_drop // 3600}** hour(s): **{await preview_corn_produced(farm_data)}** :money_with_wings:\n:seedling: **Plots**: {farm_data['plot']}")
        food_embed.set_thumbnail(url=user.display_avatar)
        return food_embed
    
    @commands.hybrid_command(name="buyplot", aliases=["bp"], usage="buyPlot", description="Buy a plot to increase the corn production.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def buy_plot(self, ctx: Context) -> None:
        """Buy a plot for corn production"""
        farm_data = ctx.data["farm_data"]
        actual_plot = farm_data['plot']
        if actual_plot == max_plot_limit:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you have reached the maximum number of plots.")
            return
        plot_price = (actual_plot ** 1.7) * 100
        plot_price = int(plot_price)
        confirmation = await confirmation_embed(ctx, ctx.author, f":seedling: {ctx.author.display_name}, currently have **{farm_data['plot']}** plots. The next plot will cost **{plot_price}** eggbux.")
        if confirmation:
            farm_data = Farm.read(ctx.author.id)
            user_data = User.read(ctx.author.id)
            if user_data['points'] >= plot_price:
                farm_data['plot'] += 1
                User.update_points(ctx.author.id, user_data['points'] - plot_price)
                Farm.update(ctx.author.id, plot=farm_data['plot'])
                await on_user_transaction(ctx.author.id, plot_price, 1)
                await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, you have bought a new plot.")
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have enough eggbux to buy the plot.")
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you have cancelled the purchase or the offer has expired.")
            
    @commands.hybrid_command(name="upgradecornlimit", aliases=["ucl"], usage="upgradeCornLimit", description="Upgrade the corn limit.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def upgrade_corn_limit(self, ctx: Context) -> None:
        """Upgrades the player corn limit."""
        farm_data = ctx.data["farm_data"]
        range_corn = int((farm_data['corn_limit'] * 50)  // 100)
        if farm_data['corn_limit'] == max_corn_limit:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you have reached the maximum corn limit.")
            return
        price_corn = farm_data['corn_limit'] * 2
        confirmation = await confirmation_embed(ctx, ctx.author, f":seedling: {ctx.author.display_name}, you currently have a corn limit of **{farm_data['corn_limit']}**. The next upgrade will cost **{price_corn}** eggbux and will increase the corn limit by **{range_corn}**.")
        if confirmation:
            farm_data = Farm.read(ctx.author.id)
            user_data = User.read(ctx.author.id)
            if user_data['points'] >= price_corn:
                farm_data['corn_limit'] += range_corn
                User.update_points(ctx.author.id, user_data['points'] - price_corn)
                Farm.update(ctx.author.id, corn_limit=farm_data['corn_limit'])
                await on_user_transaction(ctx.author.id, price_corn, 1)
                await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, you have upgraded the corn limit.")
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have enough eggbux to upgrade the corn limit.")
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you have cancelled the upgrade or the offer has expired.")
    
    @commands.hybrid_command(name="buycorn", aliases=["bc"], usage="buyCorn <quantity>", description="Buy corn for the chickens.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def buy_corn(self, ctx: Context, quantity) -> None:
        """Buy corn for the chickens"""
        if quantity == ("all" or "ALL"):
            quantity = ctx.data["farm_data"]['corn_limit'] - ctx.data["farm_data"]['corn']
        else:
            try:
                quantity = int(quantity)
            except ValueError:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, the quantity must be a number or 'all'.")
                return
        farm_data = ctx.data["farm_data"]
        user_data = ctx.data["user_data"]
        if quantity < 30:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, the minimum amount of corn you can buy is 30.")
            return
        corn_price = quantity // 2
        if user_data['points'] < corn_price:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have enough eggbux to buy the corn.")
            return
        if farm_data['corn'] + quantity > farm_data['corn_limit']:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't buy more corn than your corn limit.")
            return
        farm_data['corn'] += quantity
        User.update_points(ctx.author.id, user_data['points'] - corn_price)
        Farm.update(ctx.author.id, corn=farm_data['corn'])
        await on_user_transaction(ctx.author.id, corn_price, 1)
        await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, you have bought {quantity} corn for {corn_price} eggbux.")

    @commands.hybrid_command(name="sellcorn", aliases=["sf"], usage="sellCorn <quantity>", description="Sell corn for the chickens.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def sell_corn(self, ctx, quantity: int) -> None:
        """Sell corn"""
        farm_data = ctx.data["farm_data"]
        user_data = ctx.data["user_data"]
        if quantity > farm_data['corn']:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have enough corn to sell.")
            return
        if quantity < 30:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, the minimum amount of corn you can sell is 30.")
            return
        corn_price = quantity // 3
        farm_data['corn'] -= quantity
        User.update_points(ctx.author.id, user_data['points'] + corn_price)
        Farm.update(ctx.author.id, corn=farm_data['corn'])
        await on_user_transaction(ctx.author.id, corn_price, 0)
        await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, you have sold {quantity} corn for {corn_price} eggbux.")

    @commands.hybrid_command(name="feedallchicken", aliases=["fac"], usage="feedallchicken", description="Feed a chicken.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def feed_all_chickens(self, ctx: Context) -> None:
        """Feed all the chickens"""
        farm_data = ctx.data["farm_data"]
        total_chickens = len(farm_data['chickens'])
        chickens_fed = 0
        if farm_data['corn'] == 0:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have any corn.")
            return
        total_cost = 0
        all_happiness = 0
        for chicken in farm_data['chickens']:
            if chicken['happiness'] == 100:
                all_happiness += 1
                continue
            cost_to_feed = ChickenFood[chicken['rarity']].value
            if farm_data['corn'] >= cost_to_feed:
                total_cost += cost_to_feed
                chicken['happiness'] = 100
                chickens_fed += 1
                all_happiness += 1
                farm_data['corn'] -= cost_to_feed
            else:
                break
        if total_cost == 0 and all_happiness != len(farm_data['chickens']):
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't afford to feed any chickens.")
            return
        elif total_cost == 0 and all_happiness == len(farm_data['chickens']):
            await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, all the chickens are already fed.")
        Farm.update(ctx.author.id, corn=farm_data['corn'], chickens=farm_data['chickens'])
        await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, **{chickens_fed}** out of **{total_chickens}** chickens have been fed.\n:corn:The corn cost was {total_cost}.")

async def setup(bot):
    await bot.add_cog(CornCommands(bot))