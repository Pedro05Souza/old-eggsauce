from time import time
from discord.ext import commands
from db.farmDB import Farm
from db.userDB import User
from tools.shared import create_embed_without_title, make_embed_object, regular_command_cooldown
from tools.pointscore import pricing
from tools.chickenshared import update_player_corn, calculate_corn
import discord

class CornCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="cornfield", aliases=["c", "corn"], usage="chickenfood", descripton="Opens the food farm to generated food for the chickens.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def corn_field(self, ctx, user: discord.Member = None):
        """Displays the user's corn field."""
        if user is None:
            user = ctx.author
        if Farm.read(user.id):
            await ctx.send(embed=await self.show_plr_food_farm(ctx, user))
    
    @commands.hybrid_command(name="renamecornfield", aliases=["rcf"], usage="renameCornfield <nickname>", description="Rename the cornfield.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def rename_corn_field(self, ctx, nickname: str):
        """Rename the cornfield"""
        if Farm.read(ctx.author.id):
            farm_data = Farm.read(ctx.author.id)
            if len(nickname) > 20:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} The cornfield name must have a maximum of 15 characters.")
                return
            farm_data['plant_name'] = nickname
            Farm.update(ctx.author.id, plant_name=nickname)
            await create_embed_without_title(ctx, f"{ctx.author.display_name} Your cornfield has been renamed to {nickname}.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You don't have a farm.")

    async def show_plr_food_farm(self, ctx, user: discord.Member):
        """Show the player's food farm"""
        farm_data = Farm.read(user.id)
        if user is None:
            user = ctx.author
        farm_data = await update_player_corn(farm_data, user)
        if farm_data:
            food_embed = await make_embed_object(title=f":corn: {farm_data['plant_name']}", description=f":corn: Corn balance: {farm_data['corn']}/{farm_data['corn_limit']}\n:moneybag: Corn expected to generate in 30 minutes: {calculate_corn(farm_data)}\n:seedling: **Plots**: {farm_data['plot']}")
            food_embed.set_thumbnail(url=user.display_avatar)
            return food_embed
    
    @commands.hybrid_command(name="buyplot", aliases=["bp"], usage="buyPlot", description="Buy a plot to increase the corn production.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def buy_plot(self, ctx):
        """Buy a plot for corn production"""
        end_time = time() + 60
        farm_data = Farm.read(ctx.author.id)
        user_data = User.read(ctx.author.id)
        if farm_data:
            actual_plot = farm_data['plot']
            if actual_plot == 8:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you have reached the maximum number of plots.")
                return
            plot_price = (actual_plot ** 2) * 150
            msg = await create_embed_without_title(ctx, f":seedling: {ctx.author.display_name}, currently have {farm_data['plot']} plots. The next plot will cost {plot_price} eggbux. React with ✅ to buy the plot or ❌ to cancel.")
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            while True:
                actual_time = end_time - time()
                if actual_time <= 0:
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you have not responded to the purchase request.")
                    break
                reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.message == msg, timeout=40)
                farm_data = Farm.read(ctx.author.id)
                user_data = User.read(ctx.author.id)
                if reaction.emoji == "✅":
                    if user_data['points'] >= plot_price:
                        farm_data['plot'] += 1
                        User.update_points(ctx.author.id, user_data['points'] - plot_price)
                        Farm.update(ctx.author.id, plot=farm_data['plot'])
                        await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, you have bought a new plot.")
                        break
                    else:
                        await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have enough eggbux to buy the plot.")
                elif reaction.emoji == "❌":
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you have cancelled the purchase.")
                    break

    @commands.hybrid_command(name="upgradecornlimit", aliases=["ucl"], usage="upgradeCornLimit", description="Upgrade the corn limit.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def upgrade_corn_limit(self, ctx):
        """Upgrades the player corn limit."""
        end_time = time() + 60
        farm_data = Farm.read(ctx.author.id)
        user_data = User.read(ctx.author.id)
        if farm_data:
            range_corn = int((farm_data['corn_limit'] * 50)  // 100)
            if farm_data['corn_limit'] == 1702:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you have reached the maximum corn limit.")
                return
            price_corn = farm_data['corn_limit'] * 2
            msg = await create_embed_without_title(ctx, f":corn: {ctx.author.display_name}, currently have a corn limit of {farm_data['corn_limit']}. The next upgrade will cost {price_corn} eggbux and it will upgrade to {farm_data['corn_limit'] + range_corn}. React with ✅ to upgrade the corn limit or ❌ to cancel.")
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            while True:
                actual_time = end_time - time()
                if actual_time <= 0:
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you have not responded to the upgrade request.")
                    break
                farm_data = Farm.read(ctx.author.id)
                user_data = User.read(ctx.author.id)
                reaction, user = await ctx.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.message == msg, timeout=40)
                if reaction.emoji == "✅":
                    if user_data['points'] >= price_corn:
                        farm_data['corn_limit'] += range_corn
                        User.update_points(ctx.author.id, user_data['points'] - price_corn)
                        Farm.update(ctx.author.id, corn_limit=farm_data['corn_limit'])
                        await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, you have upgraded the corn limit.")
                        break
                    else:
                        await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have enough eggbux to upgrade the corn limit.")
                elif reaction.emoji == "❌":
                    await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you have cancelled the upgrade.")
                    break
    
    @commands.hybrid_command(name="buycorn", aliases=["bc"], usage="buyCorn <quantity>", description="Buy corn for the chickens.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def buy_corn(self, ctx, quantity: int):
        """Buy corn for the chickens"""
        farm_data = Farm.read(ctx.author.id)
        user_data = User.read(ctx.author.id)
        if quantity < 30:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the minimum amount of corn you can buy is 30.")
            return
        if farm_data and user_data:
            corn_price = quantity // 2
            if user_data['points'] < corn_price:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have enough eggbux to buy the corn.")
                return
            if farm_data['corn'] + quantity > farm_data['corn_limit']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't buy more corn than your corn limit.")
                return
            farm_data['corn'] += quantity
            User.update_points(ctx.author.id, user_data['points'] - corn_price)
            Farm.update(ctx.author.id, corn=farm_data['corn'])
            await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, you have bought {quantity} corn for {corn_price} eggbux.")

    @commands.hybrid_command(name="sellcorn", aliases=["sf"], usage="sellCorn <quantity>", description="Sell corn for the chickens.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def sell_corn(self, ctx, quantity: int):
        """Sell corn"""
        farm_data = await update_player_corn(Farm.read(ctx.author.id), ctx.author)
        user_data = User.read(ctx.author.id)
        if farm_data:
            if quantity > farm_data['corn']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have enough corn to sell.")
                return
            if quantity < 30:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the minimum amount of corn you can sell is 30.")
                return
            corn_price = quantity // 3
            farm_data['corn'] -= quantity
            User.update_points(ctx.author.id, user_data['points'] + corn_price)
            Farm.update(ctx.author.id, corn=farm_data['corn'])
            await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, you have sold {quantity} corn for {corn_price} eggbux.")

async def setup(bot):
    await bot.add_cog(CornCommands(bot))