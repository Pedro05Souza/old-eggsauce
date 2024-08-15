from discord.ext import commands
from db.farmDB import Farm
from db.userDB import User
from tools.chickens.selection.chickenselection import ChickenSelectView
from tools.chickens.chickeninfo import ChickenRarity
from tools.chickens.chickenhandlers import EventData
from tools.chickens.chickenshared import *
from tools.pointscore import pricing
from tools.shared import send_bot_embed, confirmation_embed, regular_command_cooldown, user_cache_retriever
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
    async def sell_chicken(self, ctx) -> None:
        """Deletes a chicken from the farm"""
        if await verify_events(ctx, ctx.author):
            return
        farm_data = ctx.data["farm_data"]
        if farm_data:
            if not farm_data['chickens']:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} You don't have any chickens.")
                return
            message = await get_usr_farm(ctx, ctx.author)
            view = ChickenSelectView(message=message, chickens=farm_data['chickens'], author=ctx.author, action="D")
            await ctx.send(embed=message,view=view)
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} you do not have a farm.")

    @commands.hybrid_command(name="tradechicken", aliases=["tc", "trade"], usage="tradeChicken <user>", description="Trade a chicken(s) with another user.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def trade_chicken(self, ctx, user: discord.Member) -> None:
        """Trade a chicken(s) with another user"""
        if await verify_events(ctx, ctx.author) or await verify_events(ctx, user):
            return
        farm_author = ctx.data["farm_data"]
        farm_target = await user_cache_retriever(user.id)
        farm_target = farm_target["farm_data"]
        if farm_author and farm_target:
            if not farm_author['chickens'] or not farm_target['chickens']:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, {user.display_name} doesn't have any chickens.")
                return
            if user.id == ctx.author.id:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't trade with yourself.")
                return
            if len(farm_author['chickens']) == 1 and farm_author['chickens'][0]['rarity'] == "ETHEREAL":
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't trade an ethereal chicken.")
                return
            t = EventData(user=ctx.author)
            t2 = EventData(user=user)
            msg = await send_bot_embed(ctx, description=f":chicken: {ctx.author.display_name} has sent a trade request to {user.display_name}. You have 40 seconds to react with ✅ to accept or ❌ to decline.")
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            try:
                reaction, _ = await self.bot.wait_for("reaction_add", check=lambda reaction, usr: usr == user and reaction.message == msg, timeout=40)
                if reaction.emoji == "✅":
                        await self.trade_chickens(ctx, user, t, farm_author, farm_target)
                        return
                elif reaction.emoji == "❌":
                    await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} has declined the trade request.")
                    EventData.remove(t)
                    EventData.remove(t2)
                    return
            except asyncio.TimeoutError:
                await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} has not responded to the trade request.")
                EventData.remove(t)
                EventData.remove(t2)

    async def trade_chickens(self, ctx, User: discord.Member, t, author_data, user_data) -> None:
        """Trade the chickens"""
        authorEmbed = await get_usr_farm(ctx, ctx.author)
        userEmbed = await get_usr_farm(ctx, User)
        trade_data = [author_data['chickens'], user_data['chickens']]
        trade_data[0] = [chicken for chicken in trade_data[0] if chicken['rarity'] != "DEAD" and chicken['rarity'] != "ETHEREAL"]
        trade_data[1] = [chicken for chicken in trade_data[1] if chicken['rarity'] != "DEAD" and chicken['rarity'] != "ETHEREAL"]
        members_data = [ctx.author, User]
        embeds = [authorEmbed, userEmbed]
        if len(user_data['chickens']) == 1 and user_data['chickens'][0]['rarity'] == "ETHEREAL":
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't trade an ethereal chicken.")
            return
        view_author = ChickenSelectView(chickens=trade_data, author=members_data, action="T", message=embeds, role="author", trade_data=t)
        view_user = ChickenSelectView(chickens=trade_data, author=members_data, action="T", message=embeds, role="user", trade_data=t, instance_bot = self.bot)
        await ctx.send(embed=authorEmbed, view=view_author)
        await ctx.send(embed=userEmbed, view=view_user)

    @commands.hybrid_command(name="giftchicken", aliases=["gc"], usage="giftChicken <index> <user>", description="Gift a chicken to another user.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def gift_chicken(self, ctx, index: int, user: discord.Member) -> None:
        """Gift a chicken to another user"""
        if await verify_events(ctx, ctx.author) or await verify_events(ctx, user):
            return
        author_data = ctx.data["farm_data"]
        user_data = await user_cache_retriever(user.id)
        user_data = user_data["farm_data"]
        if author_data and user_data:
            index -= 1
            g = EventData(ctx.author)
            g2 = EventData(user)
            if not author_data['chickens']:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have any chickens.")
                EventData.remove(g)
                EventData.remove(g2)
                return
            if index > len(author_data['chickens']) or index < 0:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
                EventData.remove(g)
                EventData.remove(g2)
                return
            if user.id == ctx.author.id:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't gift a chicken to yourself.")
                EventData.remove(g)
                EventData.remove(g2)
                return
            if len(user_data['chickens']) >= get_max_chicken_limit(user_data):
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, {user.display_name} already has the maximum amount of chickens.")
                EventData.remove(g)
                EventData.remove(g2)
                return
            gifted_chicken = author_data['chickens'][index]
            if gifted_chicken['rarity'] == "ETHEREAL":
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't gift an ethereal chicken.")
                EventData.remove(g)
                EventData.remove(g2)
                return
            confirmation = await confirmation_embed(ctx, ctx.author, f":question: {ctx.author.display_name}, are you sure you want to gift **{get_rarity_emoji(gifted_chicken['rarity'])}{gifted_chicken['rarity']}** {gifted_chicken['name']} to {user.display_name}?")
            if confirmation:
                msg = await send_bot_embed(ctx, description=f":gift: {user.display_name}, {ctx.author.display_name} wants to gift you a {gifted_chicken['rarity']} {gifted_chicken['name']}. You have 20 seconds to react with ✅ to accept or ❌ to decline the gift request.")
                await msg.add_reaction("✅")
                await msg.add_reaction("❌")
                try:
                    reaction, _ = await self.bot.wait_for("reaction_add", check=lambda reaction, jogador: jogador == user and reaction.message == msg, timeout=40)
                    if reaction.emoji == "✅":
                        chicken = author_data['chickens'][index]
                        user_data['chickens'].append(chicken)
                        author_data['chickens'].remove(chicken)
                        Farm.update(ctx.author.id, chickens=author_data['chickens'])
                        Farm.update(user.id, chickens=user_data['chickens'])
                        await send_bot_embed(ctx, description=f":gift: {ctx.author.display_name}, the chicken has been gifted to {user.display_name}.")
                        EventData.remove(g)
                        EventData.remove(g2)
                    elif reaction.emoji == "❌":
                        await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} has declined the gift request.")
                        EventData.remove(g)
                        EventData.remove(g2)
                        return
                except asyncio.TimeoutError:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} has not responded to the gift request.")
                    EventData.remove(g)
                    EventData.remove(g2)
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you have cancelled the gift request.")
                EventData.remove(g)
                EventData.remove(g2)
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you or {user.display_name} don't have a farm.")
    
    @commands.hybrid_command(name="evolvechicken", aliases=["ec", "fuse"], usage="evolveChicken <index> <index2>", description="Evolve a chicken if having 2 of the same rarity.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def evolve_chicken(self, ctx, index: int, index2: int) -> None:
        """Evolves a chicken if having 2 of the same rarity"""
        if await verify_events(ctx, ctx.author):
            return
        farm_data = ctx.data["farm_data"]
        if farm_data:
            e = EventData(ctx.author)
            if not farm_data['chickens']:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have any chickens.")
                EventData.remove(e)
                return
            if index > len(farm_data['chickens']) or index < 0 or index2 > len(farm_data['chickens']) or index2 < 0:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
                EventData.remove(e)
                return
            if index == index2:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't evolve a chicken with itself.")
                EventData.remove(e)
                return
            chicken_selected = farm_data['chickens'][index - 1]
            chicken_removed = farm_data['chickens'][index2 - 1]
            if chicken_selected['rarity'] != chicken_removed['rarity']:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, the chickens must be of the same rarity to evolve.")
                EventData.remove(e)
                return
            if chicken_selected['rarity'] == "ASCENDED" or chicken_removed['rarity'] == "ASCENDED" or chicken_selected['rarity'] == "ETHEREAL" or chicken_removed['rarity'] == "ETHEREAL":
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't evolve an ascended or ethereal chicken.")
                EventData.remove(e)
                return
            if chicken_selected['rarity'] == "DEAD" or chicken_removed['rarity'] == "DEAD":
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't evolve a dead chicken.")
                EventData.remove(e)
                return
            confirmation = await confirmation_embed(ctx, ctx.author, f"{ctx.author.display_name}, are you sure you want to evolve your **{get_rarity_emoji(chicken_selected['rarity'])}{chicken_selected['rarity']} {chicken_selected['name']}** to a higher rarity?")
            if confirmation:
                rarity_list = list(ChickenRarity.__members__)
                chicken_selected['rarity'] = rarity_list[rarity_list.index(chicken_selected['rarity']) + 1]
                chicken_selected['upkeep_multiplier'] = determine_chicken_upkeep(chicken_selected)
                farm_data['chickens'].remove(chicken_removed)
                Farm.update(ctx.author.id, chickens=farm_data['chickens'])
                await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, the chicken has been evolved to {chicken_selected['rarity']} {chicken_selected['name']}.")
                EventData.remove(e)
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you have cancelled the evolution.")
                EventData.remove(e)

    @commands.hybrid_command(name="farmer", aliases =["farmers"], usage="farmer", description="The farmers helps increase the productivity of the chickens.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def farmer(self, ctx) -> None:
        """The farmer automatically feeds the chickens"""
        farmer_price = 5000
        eggs_needed = 10000
        description = [
            f":moneybag: Rich Farmer: Increase the egg value of the chickens by **{load_farmer_upgrades('Rich Farmer')[0]}%** and increases the hourly corn production by **{load_farmer_upgrades('Rich Farmer')[1]}%**\n",
            f":shield: Guardian Farmer: Whenever you sell a chicken, sell it for the full price and reduces farm taxes by **{load_farmer_upgrades('Guardian Farmer')}%**.\n",
            f":briefcase: Executive Farmer: Gives you **{load_farmer_upgrades('Executive Farmer')[0]}** more daily rolls in the market and chickens generated in the market comes with **{load_farmer_upgrades('Executive Farmer')[1]}%** discount. \n",
            f":crossed_swords: Warrior Farmer: Gives **{load_farmer_upgrades('Warrior Farmer')}** more farm slots.\n",
            f":leaves: Sustainable Farmer: Auto-feeds the chickens every **{load_farmer_upgrades('Sustainable Farmer')[0] // 3600}** hours, the happiness generated is a number between **{load_farmer_upgrades('Sustainable Farmer')[1][0]}-{load_farmer_upgrades('Sustainable Farmer')[1][1]}%**. The farmer uses the money from your bank account.\n",
            f":tickets: Generous Farmer: Increases the maximum chickens generated in the market by **{load_farmer_upgrades('Generous Farmer')[0]}** slots.\n"
            f"\n\nAll the farmer roles have a cost of **{farmer_price}** eggbux and you can only buy one of them. Buying a farmer when you already have one will override the existing one. You need at least **{eggs_needed}** total eggs produced by your farm in order to buy them.\nReact with the corresponding emoji to purchase the role."
        ]
        message = await send_bot_embed(ctx, title=":farmer: Farmer roles:\n", description="\n".join(description))
        emojis = ["💰", "🛡️", "💼", "⚔️", "🍃", "🎟️"]
        for emoji in emojis:
            await message.add_reaction(emoji)
        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.message == message, timeout=40)
            user_data = ctx.data["user_data"]
            farm_data = ctx.data["farm_data"]
            if user_data['points'] >= farmer_price:
                if farm_data['total_eggs'] < eggs_needed:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you need to produce at least {eggs_needed} eggs in order to purchase a farmer role.")
                    return
                farm_size = get_max_chicken_limit(farm_data)
                if len(farm_data['chickens']) >= farm_size and len(farm_data['chickens']) > 8:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} you have a Warrior farmer, you need to sell the extra farm slots to buy another farmer.")
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
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have enough eggbux to purchase a farmer role.")
        except asyncio.TimeoutError:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you have not selected a farmer role.")

    async def buy_farmer_upgrade(self, ctx, name, farmer_price, user_data, farm_data) -> None:
        """Buy the farmer upgrade"""
        if user_data['points'] >= farmer_price:
            farm_data['farmer'] = name
            User.update_points(ctx.author.id, user_data['points'] - farmer_price)
            Farm.update(ctx.author.id, farmer=name)
            await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, you have purchased the {name} farmer role.")
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have enough eggbux to purchase the {name} farmer role.")
    
    @commands.hybrid_command(name="transcend", usage="transcend", description="Only available when having 8 ascended chickens.")
    @commands.cooldown(1, regular_command_cooldown, commands.BucketType.user)
    @pricing()
    async def transcend(self, ctx) -> None:
        """Transcend chicken"""
        farm_data = ctx.data["farm_data"]
        if all(chicken for chicken in farm_data['chickens'] if chicken['rarity'] == 'ASCENDED'):
            if len(farm_data['chickens']) < 8:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you need to have 8 ascended chickens to transcend.")
                return
            transcended_chicken = await create_chicken("ETHEREAL", "transced")
            farm_data['chickens'] = [transcended_chicken]
            Farm.update(ctx.author.id, chickens=farm_data['chickens'])
            await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, you have transcended your chickens to an **{get_rarity_emoji('ETHEREAL')} ETHEREAL Chicken.**")
            return
            
async def setup(bot):
    await bot.add_cog(ChickenEvents(bot))