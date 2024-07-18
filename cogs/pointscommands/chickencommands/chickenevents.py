from discord.ext import commands
from db.farmDB import Farm
from tools.chickens.chickenshared import *
from db.userDB import User
from tools.chickens.chickenselection import ChickenSelectView
from tools.chickens.chickeninfo import ChickenRarity
from tools.chickens.chickenhandlers import GiftData, TradeData, SellData
from tools.chickens.chickenshared import get_rarity_emoji, determine_chicken_upkeep, get_max_chicken_limit
from tools.pointscore import pricing
from tools.shared import create_embed_without_title, create_embed_with_title, regular_command_cooldown
import asyncio
import logging
import discord
logger = logging.getLogger('botcore')

class ChickenEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="sellchicken", aliases=["sc"], usage="sellChicken", description="Deletes a chicken from the farm.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def sell_chicken(self, ctx):
        """Deletes a chicken from the farm"""
        if TradeData.read(ctx.author.id) or GiftData.read(ctx.author.id):
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't sell a chicken while in a trade or gift request.")
            return
        farm_data = Farm.read(ctx.author.id)
        if farm_data:
            if not farm_data['chickens']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} You don't have any chickens.")
                return
            message = await get_usr_farm(ctx.author)
            view = ChickenSelectView(message=message, chickens=farm_data['chickens'], author=ctx.author.id, action="D", chicken_emoji=get_rarity_emoji)
            await ctx.send(embed=message,view=view)
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name} you do not have a farm.")

    @commands.hybrid_command(name="tradechicken", aliases=["tc", "trade"], usage="tradeChicken <user>", description="Trade a chicken(s) with another user.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def trade_chicken(self, ctx, user: discord.Member):
        """Trade a chicken(s) with another user"""
        if GiftData.read(ctx.author.id) or GiftData.read(user.id):
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you or {user.display_name} can't trade a chicken while in a gift request")
            return
        elif SellData.read(ctx.author.id) or SellData.read(user.id):
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you or {user.display_name} can't trade a chicken while in a sell request.")
            return
        author_involved_in_trade = TradeData.read(ctx.author.id)
        target_involved_in_trade = TradeData.read(user.id)
        if author_involved_in_trade:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you already have a trade in progress.")
            return
        if target_involved_in_trade:
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} already has a trade request in progress.")
            return
        farm_author = Farm.read(ctx.author.id)
        farm_target = Farm.read(user.id)
        if farm_author and farm_target:
            if not farm_author['chickens'] or not farm_target['chickens']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, {user.display_name} doesn't have any chickens.")
                return
            if user.id == ctx.author.id:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't trade with yourself.")
                return
            t = TradeData()
            t.identifier = [ctx.author.id, user.id]
            msg = await create_embed_without_title(ctx, f":chicken: {ctx.author.display_name} has sent a trade request to {user.display_name}. You have 40 seconds to react with ✅ to accept or ❌ to decline.")
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            try:
                reaction, usr = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == user and reaction.message == msg, timeout=40)
                while True:
                    if reaction.emoji == "✅" and usr == user:
                            await self.trade_chickens(ctx, user, t, farm_author, farm_target)
                            return
                    elif reaction.emoji == "❌" and usr == user:
                        await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} has declined the trade request.")
                        TradeData.remove(t)
                        return
            except asyncio.TimeoutError:
                await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} has not responded to the trade request.")
                TradeData.remove(t)

    async def trade_chickens(self, ctx, User: discord.Member, t, author_data, user_data):
        """Trade the chickens"""
        authorEmbed = await get_usr_farm(ctx.author)
        userEmbed = await get_usr_farm(User)
        trade_data = [author_data['chickens'], user_data['chickens']]
        members_data = [ctx.author, User]
        embeds = [authorEmbed, userEmbed]
        view_author = ChickenSelectView(chickens=trade_data, author=members_data, action="T", message=embeds, chicken_emoji=get_rarity_emoji, role="author", trade_data=t)
        view_user = ChickenSelectView(chickens=trade_data, author=members_data, action="T", message=embeds, chicken_emoji=get_rarity_emoji, role="user", trade_data=t, instance_bot = self.bot)
        await ctx.send(embed=authorEmbed, view=view_author)
        await ctx.send(embed=userEmbed, view=view_user)

    @commands.hybrid_command(name="giftchicken", aliases=["gc"], usage="giftChicken <index> <user>", description="Gift a chicken to another user.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def gift_chicken(self, ctx, index: int, user: discord.Member):
        """Gift a chicken to another user"""
        if TradeData.read(ctx.author.id) or TradeData.read(user.id):
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you or {user.display_name} can't gift a chicken while in a trade.")
            return
        elif SellData.read(ctx.author.id) or SellData.read(user.id):
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you or {user.display_name} can't gift a chicken while in a sell request.")
            return
        author_involved_in_gift = GiftData.read(ctx.author.id)
        target_involved_in_gift = GiftData.read(user.id)
        if author_involved_in_gift:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you already have a gift in progress.")
            return
        if target_involved_in_gift:
            await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name}, you already have a gift in progress.")
            return
        author_data = Farm.read(ctx.author.id)
        user_data = Farm.read(user.id)
        if author_data and user_data:
            index -= 1
            g = GiftData()
            g.identifier = [ctx.author.id, user.id]
            if not author_data['chickens']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have any chickens.")
                GiftData.remove(g)
                return
            if index > len(author_data['chickens']) or index < 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
                GiftData.remove(g)
                return
            if user.id == ctx.author.id:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't gift a chicken to yourself.")
                GiftData.remove(g)
                return
            if len(user_data['chickens']) >= get_max_chicken_limit(user_data):
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, {user.display_name} already has the maximum amount of chickens.")
                GiftData.remove(g)
                return
            gifted_chicken = author_data['chickens'][index]
            msg = await create_embed_without_title(ctx, f":gift: {user.display_name}, {ctx.author.display_name} wants to gift you a {gifted_chicken['rarity']} {gifted_chicken['name']}. You have 20 seconds to react with ✅ to accept or ❌ to decline the gift request.")
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            try:
                reaction, jogador = await self.bot.wait_for("reaction_add", check=lambda reaction, jogador: jogador == user and reaction.message == msg, timeout=40)
                if reaction.emoji == "✅":
                    chicken = author_data['chickens'][index]
                    user_data['chickens'].append(chicken)
                    author_data['chickens'].remove(chicken)
                    Farm.update(ctx.author.id, chickens=author_data['chickens'])
                    Farm.update(user.id, chickens=user_data['chickens'])
                    await create_embed_without_title(ctx, f":gift: {ctx.author.display_name}, the chicken has been gifted to {user.display_name}.")
                    GiftData.remove(g)
                elif reaction.emoji == "❌":
                    await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} has declined the gift request.")
                    GiftData.remove(g)
                    return
            except asyncio.TimeoutError:
                await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} has not responded to the gift request.")
                GiftData.remove(g)
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you or {user.display_name} don't have a farm.")
    
    @commands.hybrid_command(name="evolvechicken", aliases=["ec", "fuse"], usage="evolveChicken <index> <index2>", description="Evolve a chicken if having 2 of the same rarity.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def evolve_chicken(self, ctx, index: int, index2: int):
        """Evolves a chicken if having 2 of the same rarity"""
        if TradeData.read(ctx.author.id) or GiftData.read(ctx.author.id):
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't evolve a chicken while in a trade or gift request.")
            return
        if SellData.read(ctx.author.id) or SellData.read(ctx.author.id):
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't evolve a chicken while in a sell request.")
            return
        if GiftData.read(ctx.author.id) or GiftData.read(ctx.author.id):
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't evolve a chicken while in a gift request.")
            return
        farm_data = Farm.read(ctx.author.id)
        if farm_data:
            if not farm_data['chickens']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have any chickens.")
                return
            if index > len(farm_data['chickens']) or index < 0 or index2 > len(farm_data['chickens']) or index2 < 0:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
                return
            if index == index2:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't evolve a chicken with itself.")
                return
            chicken_selected = farm_data['chickens'][index - 1]
            chicken_removed = farm_data['chickens'][index2 - 1]
            if chicken_selected['rarity'] != chicken_removed['rarity']:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, the chickens must be of the same rarity to evolve.")
                return
            if chicken_selected['rarity'] == "ASCENDED" or chicken_removed['rarity'] == "ASCENDED":
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you can't evolve an ascended chicken.")
                return
            rarity_list = list(ChickenRarity.__members__)
            chicken_selected['rarity'] = rarity_list[rarity_list.index(chicken_selected['rarity']) + 1]
            chicken_selected['upkeep_multiplier'] = determine_chicken_upkeep(chicken_selected)
            farm_data['chickens'].remove(chicken_removed)
            Farm.update(ctx.author.id, chickens=farm_data['chickens'])
            await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, the chicken has been evolved to {chicken_selected['rarity']} {chicken_selected['name']}.")

    @commands.hybrid_command(name="farmer", usage="farmer", description="The farmers helps increase the productivity of the chickens.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def farmer(self, ctx):
        """The farmer automatically feeds the chickens"""
        farmer_price = 3000
        description = [
            ":moneybag: Rich Farmer: Increase the egg value of the chickens by 10%.\n",
            ":shield: Guardian Farmer: Whenever you sell a chicken, sell it for the full price and reduces upkeep by 4%.\n",
            ":briefcase: Executive Farmer: Gives you 4 more daily rolls in the market and chickens generated in the market comes with 30% discount. \n",
            ":crossed_swords: Warrior Farmer: Gives 3 more farm slots.\n",
            ":leaves: Sustainable Farmer: Auto-feeds the chickens every 4 hours, the happiness generated is a number between 20-40%. The farmer uses the money from your bank account.\n",
            ":tickets: Generous Farmer: Increases the maximum chickens generated in the market by 3 slots.\n"
            f"\n\nAll the farmer roles have a cost of **{farmer_price}** eggbux and you can only buy one of them. **Buying a farmer when you already have one will override the existing one.**\nReact with the corresponding emoji to purchase the role."
        ]
        message = await create_embed_with_title(ctx, ":farmer: Farmer roles:\n", "\n".join(description))
        emojis = ["💰", "🛡️", "💼", "⚔️", "🍃", "🎟️"]
        for emoji in emojis:
            await message.add_reaction(emoji)
        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.message == message, timeout=40)
            user_data = User.read(user.id)
            farm_data = Farm.read(user.id)
            if user_data['points'] >= farmer_price:
                farm_size = get_max_chicken_limit(farm_data)
                if len(farm_data['chickens']) >= farm_size and farm_data > 8:
                    await create_embed_without_title(ctx, f":no_entry_sign: {user.display_name} you have a Warrior farmer, you need to sell the extra farm slots to buy another farmer.")
                    return
                if reaction.emoji == "💰":
                    await self.buy_farmer_upgrade(ctx, "Rich Farmer", farmer_price, user_data, farm_data)
                elif reaction.emoji == "🛡️":
                    await self.buy_farmer_upgrade(ctx, "Guardian Farmer", farmer_price, user_data, farm_data)
                elif reaction.emoji == "💼":
                    await self.buy_farmer_upgrade(ctx, "Executive Farmer", farmer_price, user_data, farm_data)
                elif reaction.emoji == "⚔️":
                    await self.buy_farmer_upgrade(ctx, "Warrior Farmer", farmer_price, user_data, farm_data)
                elif reaction.emoji == "🍃":
                    await self.buy_farmer_upgrade(ctx, "Sustainable Farmer", farmer_price, user_data, farm_data)
                elif reaction.emoji == "🎟️":
                    await self.buy_farmer_upgrade(ctx, "Generous Farmer", farmer_price, user_data, farm_data)
            else:
                await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have enough eggbux to purchase a farmer role.")
        except asyncio.TimeoutError:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you have not selected a farmer role.")

    async def buy_farmer_upgrade(self, ctx, name, farmer_price, user_data, farm_data):
        """Buy the farmer upgrade"""
        if user_data['points'] >= farmer_price:
            farm_data['farmer'] = name
            User.update_points(ctx.author.id, user_data['points'] - farmer_price)
            Farm.update(ctx.author.id, farmer=name)
            await create_embed_without_title(ctx, f":white_check_mark: {ctx.author.display_name}, you have purchased the {name} farmer role.")
        else:
            await create_embed_without_title(ctx, f":no_entry_sign: {ctx.author.display_name}, you don't have enough eggbux to purchase the {name} farmer role.")
            
async def setup(bot):
    await bot.add_cog(ChickenEvents(bot))