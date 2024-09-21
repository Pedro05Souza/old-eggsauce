"""
This module handles events between users and their chickens.
"""
from discord.ext import commands
from db.farmdb import Farm
from db.userdb import User
from tools.chickens.selection.chickenselection import ChickenSelectView
from tools.chickens.chickeninfo import ChickenRarity
from tools.chickens.chickenhandlers import EventData
from tools.chickens.chickenshared import *
from tools.listeners import on_user_transaction
from tools.decorators import pricing
from tools.shared import send_bot_embed, confirmation_embed, user_cache_retriever
from tools.settings import REGULAR_COOLDOWN, FARMER_PRICE
from discord.ext.commands import Context
import asyncio
import logging
import discord
logger = logging.getLogger('botcore')

class ChickenEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="sellchicken", aliases=["sc"], usage="sellChicken", description="Deletes a chicken from the farm.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def sell_chicken(self, ctx: Context) -> None:
        """
        Deletes a chicken from the farm.
        
        Args:
            ctx (Context): The context of the command.
        
        Returns:
            None
        """
        if await verify_events(ctx, ctx.author):
            return
        
        farm_data = ctx.data["farm_data"]

        if not farm_data['chickens']:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name} You don't have any chickens.")
            return
        
        message = await get_usr_farm(ctx, ctx.author, ctx.data)
        view = ChickenSelectView(message=message, chickens=farm_data['chickens'], author=ctx.author, action="D")
        await ctx.send(embed=message,view=view)

    @commands.hybrid_command(name="tradechicken", aliases=["tc", "trade"], usage="tradeChicken <user>", description="Trade a chicken(s) with another user.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def trade_chicken(self, ctx: Context, user: discord.Member) -> None:
        """
        Trade a chicken(s) with another user.

        Args:
            ctx (Context): The context of the command.
            user (discord.Member): The user to trade the chicken(s) with.
        
        Returns:
            None
        """
        
        farm_author = ctx.data["farm_data"]
        user_cache_data = await user_cache_retriever(user.id)
        farm_target = user_cache_data["farm_data"]

        if farm_target:

            if not farm_author['chickens'] or not farm_target['chickens']:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, {user.display_name} doesn't have any chickens.")
                return
            
            if user.id == ctx.author.id:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't trade with yourself.")
                return
            
            if len(farm_author['chickens']) == 1 and farm_author['chickens'][0]['rarity'] == "ETHEREAL":
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't trade an ethereal chicken.")
                return
            
            if await verify_events(ctx, ctx.author) or await verify_events(ctx, user):
                return
                        
            msg = await send_bot_embed(ctx, description=f":chicken: **{ctx.author.display_name}** has sent a trade request to **{user.display_name}**. **{user.display_name}** has 40 seconds to react with ✅ to accept or ❌ to decline.")
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            try:
                reaction, _ = await self.bot.wait_for("reaction_add", check=lambda reaction, usr: usr == user and reaction.message == msg, timeout=40)
                if reaction.emoji == "✅":
                        await self.trade_chickens(ctx, user, farm_author, farm_target, user_cache_data)
                        return
                elif reaction.emoji == "❌":
                    await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} has declined the trade request.")
                    return
            except asyncio.TimeoutError:
                await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} has not responded to the trade request.")
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} doesn't have a farm.")

    async def trade_chickens(self, ctx: Context, user: discord.Member, farm_author: dict, farm_target: dict, user_cache_data: dict) -> None:
        """
        Trade the chickens.

        Args:
            ctx (Context): The context of the command.
            User (discord.Member): The user to trade the chicken(s) with.
            t (EventData): The event data.
            farm_author (dict): The farm data of the author.
            farm_target (dict): The farm data of the target.
            user_cache_data (dict): The user cache data.

        Returns:
            None
        """
        if await verify_events(ctx, ctx.author) or await verify_events(ctx, user):
            return
        
        t = EventData(ctx.author)
        t2 = EventData(user)

        authorEmbed = await get_usr_farm(ctx, ctx.author, ctx.data)
        userEmbed = await get_usr_farm(ctx, user, user_cache_data)
        trade_data = [farm_author['chickens'], farm_target['chickens']]
        trade_data[0] = [chicken for chicken in trade_data[0] if chicken['rarity'] != "DEAD" and chicken['rarity'] != "ETHEREAL"]
        trade_data[1] = [chicken for chicken in trade_data[1] if chicken['rarity'] != "DEAD" and chicken['rarity'] != "ETHEREAL"]
        members_data = [ctx.author, user]
        embeds = [authorEmbed, userEmbed]

        if len(farm_target['chickens']) == 1 and farm_target['chickens'][0]['rarity'] == "ETHEREAL":
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't trade an ethereal chicken.")
            return
        
        view_author = ChickenSelectView(chickens=trade_data, author=members_data, action="T", message=embeds, role="author", trade_data=t)
        view_user = ChickenSelectView(chickens=trade_data, author=members_data, action="T", message=embeds, role="user", trade_data=t2, instance_bot = self.bot)
        await ctx.send(embed=authorEmbed, view=view_author)
        await ctx.send(embed=userEmbed, view=view_user)

    @commands.hybrid_command(name="giftchicken", aliases=["gc"], usage="giftChicken <index> <user>", description="Gift a chicken to another user.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def gift_chicken(self, ctx: Context, index: int, user: discord.Member) -> None:
        """
        Gift a chicken to another user.

        Args:
            ctx (Context): The context of the command.
            index (int): The index of the chicken to gift.
            user (discord.Member): The user to gift the chicken to.
        
        Returns:
            None
        """
        
        author_data = ctx.data["farm_data"]
        user_data = await user_cache_retriever(user.id)
        user_data = user_data["farm_data"]
        index -= 1

        if not author_data['chickens']:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have any chickens.")
            return
        
        if index > len(author_data['chickens']) or index < 0:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
            return
        
        if user.id == ctx.author.id:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't gift a chicken to yourself.")
            return
        
        if len(user_data['chickens']) >= get_max_chicken_limit(user_data):
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, {user.display_name} already has the maximum amount of chickens.")
            return
        
        gifted_chicken = author_data['chickens'][index]

        if gifted_chicken['rarity'] == "ETHEREAL":
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't gift an ethereal chicken.")
            return
        
        confirmation = await confirmation_embed(ctx, ctx.author, f":question: {ctx.author.display_name}, are you sure you want to gift **{get_rarity_emoji(gifted_chicken['rarity'])}{gifted_chicken['rarity']}** {gifted_chicken['name']} to {user.display_name}?")

        if confirmation:
            await self.gift_request(ctx, user, gifted_chicken, author_data, user_data, index)
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you have cancelled the gift request.")


    async def gift_request(self, ctx: Context, user: discord.Member, gifted_chicken: dict, author_data: dict, user_data: dict, index: int) -> None:
        """
        Gift request to the user.

        Args:
            ctx (Context): The context of the command.
            user (discord.Member): The user to gift the chicken to.
            gifted_chicken (dict): The gifted chicken.
            author_data (dict): The author data.
            user_data (dict): The user data.

        Returns:
            None
        """
        if await verify_events(ctx, ctx.author) or await verify_events(ctx, user):
            return
        
        g = EventData(ctx.author)
        g2 = EventData(user)

        msg = await send_bot_embed(ctx, description=f":gift: {user.display_name}, {ctx.author.display_name} wants to gift you a {gifted_chicken['rarity']} {gifted_chicken['name']}. You have 20 seconds to react with ✅ to accept or ❌ to decline the gift request.")
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        try:
            reaction, _ = await self.bot.wait_for("reaction_add", check=lambda reaction, jogador: jogador == user and reaction.message == msg, timeout=40)
            if reaction.emoji == "✅":
                chicken = author_data['chickens'][index]
                user_data['chickens'].append(chicken)
                author_data['chickens'].remove(chicken)
                await Farm.update(ctx.author.id, chickens=author_data['chickens'])
                await Farm.update(user.id, chickens=user_data['chickens'])
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
            
    @commands.hybrid_command(name="evolvechicken", aliases=["ec", "fuse"], usage="evolveChicken <index> <index2>", description="Evolve a chicken if having 2 of the same rarity.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def evolve_chicken(self, ctx: Context, index: int, index2: int) -> None:
        """
        Evolves a chicken if having 2 of the same rarity.

        Args:
            ctx (Context): The context of the command.
            index (int): The index of the chicken to evolve.
            index2 (int): The index of the chicken to evolve.
        
        Returns:
            None
        """
        
        farm_data = ctx.data["farm_data"]

        if not farm_data['chickens']:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have any chickens.")
            return
        
        if index > len(farm_data['chickens']) or index < 0 or index2 > len(farm_data['chickens']) or index2 < 0:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, the chicken index is invalid.")
            return
        
        if index == index2:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't evolve a chicken with itself.")
            return
        
        chicken_selected = farm_data['chickens'][index - 1]
        chicken_removed = farm_data['chickens'][index2 - 1]

        if chicken_selected['rarity'] != chicken_removed['rarity']:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, the chickens must be of the same rarity to evolve.")
            return
        
        if chicken_selected['rarity'] == "ASCENDED" or chicken_removed['rarity'] == "ASCENDED" or chicken_selected['rarity'] == "ETHEREAL" or chicken_removed['rarity'] == "ETHEREAL":
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't evolve an ascended or ethereal chicken.")
            return
        
        if chicken_selected['rarity'] == "DEAD" or chicken_removed['rarity'] == "DEAD":
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you can't evolve a dead chicken.")
            return
        
        confirmation = await confirmation_embed(ctx, ctx.author, f"{ctx.author.display_name}, are you sure you want to evolve your **{get_rarity_emoji(chicken_selected['rarity'])}{chicken_selected['rarity']} {chicken_selected['name']}** to a higher rarity?")

        if confirmation:
            if await verify_events(ctx, ctx.author):
                return
            
            e = EventData(ctx.author)
            rarity_list = list(ChickenRarity.__members__)
            chicken_selected['rarity'] = rarity_list[rarity_list.index(chicken_selected['rarity']) + 1]
            chicken_selected['upkeep_multiplier'] = determine_chicken_upkeep(chicken_selected)
            farm_data['chickens'].remove(chicken_removed)
            await Farm.update(ctx.author.id, chickens=farm_data['chickens'])
            await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, the chicken has been evolved to {chicken_selected['rarity']} {chicken_selected['name']}.")
            EventData.remove(e)
        else:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you have cancelled the evolution.")
            EventData.remove(e)

    @commands.hybrid_command(name="farmer", aliases =["farmers"], usage="farmer", description="The farmers helps increase the productivity of the chickens.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def purchase_farmer(self, ctx: Context) -> None:
        """
        The farmers helps increase the productivity of the chickens in different ways.

        Args:
            ctx (Context): The context of the command.
        
        Returns:
            None
        """
        eggs_needed = FARMER_PRICE * 2
        message = await send_bot_embed(ctx, title=":farmer: Farmer roles:\n", description="\n".join(await self.farmers_descriptions(eggs_needed)))
        emojis = ["💰", "🛡️", "💼", "⚔️", "🍃", "🎟️"]
        for emoji in emojis:
            await message.add_reaction(emoji)
        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.message == message, timeout=40)
            user_data = ctx.data["user_data"]
            farm_data = ctx.data["farm_data"]
            if user_data['points'] >= FARMER_PRICE:
                if farm_data['eggs_generated'] < eggs_needed:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you need to produce at least {eggs_needed} eggs in order to purchase a farmer role.")
                    return
                farm_size = get_max_chicken_limit(farm_data)
                if len(farm_data['chickens']) >= farm_size and len(farm_data['chickens']) > 8:
                    await send_bot_embed(ctx, description=f":no_entry_sign: {user.display_name} you have a Warrior farmer, you need to sell the extra farm slots to buy another farmer.")
                    return
                farmer_dict = await self.retrieve_farmer_dict()
                await self.buy_farmer_upgrade(ctx, farmer_dict[reaction.emoji], FARMER_PRICE, user_data, farm_data)
            else:
                await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you don't have enough eggbux to purchase a farmer role.")
        except asyncio.TimeoutError:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you have not selected a farmer role.")

    async def farmers_descriptions(self, eggs_needed: int) -> str:
        """
        Gets all the farmer roles descriptions.

        Args:
            eggs_needed (int): The amount of eggs needed to buy a farmer role.

        Returns:
            str
        """
        description = [
            f":moneybag: Rich Farmer: Increase the egg value of the chickens by **{load_farmer_upgrades('Rich Farmer')[0]}%** and increases the hourly corn production by **{load_farmer_upgrades('Rich Farmer')[1]}%**\n",
            f":shield: Guardian Farmer: Whenever you sell a chicken, sell it for the full price and reduces farm taxes by **{load_farmer_upgrades('Guardian Farmer')}%**.\n",
            f":briefcase: Executive Farmer: Gives you **{load_farmer_upgrades('Executive Farmer')[0]}** more daily rolls in the market and chickens generated in the market comes with **{load_farmer_upgrades('Executive Farmer')[1]}%** discount. \n",
            f":crossed_swords: Warrior Farmer: Gives **{load_farmer_upgrades('Warrior Farmer')}** more farm slots.\n",
            f":leaves: Sustainable Farmer: Auto-feeds the chickens every **{load_farmer_upgrades('Sustainable Farmer')[0] // 3600}** hours, the happiness generated is a number between **{load_farmer_upgrades('Sustainable Farmer')[1][0]}-{load_farmer_upgrades('Sustainable Farmer')[1][1]}%**. The farmer uses the money from your bank account.\n",
            f":tickets: Generous Farmer: Increases the maximum chickens generated in the market by **{load_farmer_upgrades('Generous Farmer')[0]}** slots.\n"
            f"\n\nAll the farmer roles have a cost of **{FARMER_PRICE}** eggbux and you can only buy one of them. Buying a farmer when you already have one will override the existing one. You need at least **{eggs_needed}** total eggs produced by your farm in order to buy them.\nReact with the corresponding emoji to purchase the role."
        ]
        return description

    async def retrieve_farmer_dict(self) -> dict:
        """
        Retrieves a dictionary of the farmer roles.

        Returns:
            dict
        """
        farmer_dict = {
            "💰": "Rich Farmer",
            "🛡️": "Guardian Farmer",
            "💼": "Executive Farmer",
            "⚔️": "Warrior Farmer",
            "🍃": "Sustainable Farmer",
            "🎟️": "Generous Farmer"
        }
        return farmer_dict

    async def buy_farmer_upgrade(self, ctx: Context, name: str, farmer_price: int, user_data: dict, farm_data: dict) -> None:
        """
        Buy the farmer upgrade

        Args:
            ctx (Context): The context of the command.
            name (str): The name of the farmer.
            farmer_price (int): The price of the farmer.
            user_data (dict): The user data.
            farm_data (dict): The farm data.

        Returns:
            None
        """
        if farm_data['farmer'] == name:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you already have the {name} farmer role.")
            return
        
        if name == "Sustainable Farmer":
            Farm.add_last_farm_drop_attribute(ctx.author.id)

        if await self.verify_player_has_sustainable(farm_data) and not name == "Sustainable Farmer":
            Farm.remove_last_farm_drop_attribute(ctx.author.id)

        farm_data['farmer'] = name
        await User.update_points(ctx.author.id, user_data['points'] - farmer_price)
        await Farm.update(ctx.author.id, farmer=name)
        await on_user_transaction(ctx, farmer_price, 1)
        await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, you have purchased the {name} farmer role.")
        return
    
    @commands.hybrid_command(name="transcend", usage="transcend", description="Only available when having 8 ascended chickens.")
    @commands.cooldown(1, REGULAR_COOLDOWN, commands.BucketType.user)
    @pricing()
    async def transcend(self, ctx: Context) -> None:
        """
        Transcend 8 ascended chickens to an ethereal chicken.

        Args:
            ctx (Context): The context of the command.
        
        Returns:
            None
        """
        farm_data = ctx.data["farm_data"]
        ascended_chickens = [chicken for chicken in farm_data['chickens'] if chicken['rarity'] == 'ASCENDED']
        extra_ascended_chickens = []

        if len(ascended_chickens) < 8:
            await send_bot_embed(ctx, description=f":no_entry_sign: {ctx.author.display_name}, you need to have ** {8 - len(ascended_chickens)} more {get_rarity_emoji('ASCENDED')} ASCENDED chickens** in order to transcend them.")
            return
        
        elif len(ascended_chickens) > 8:
            extra_ascended_chickens = [chicken for chicken in ascended_chickens[8:]]

        if await confirmation_embed(ctx, ctx.author, f"{ctx.author.display_name}, are you sure you want to transcend your 8 ascended chickens to an ETHEREAL Chicken?"):

            transcended_chicken = await create_chicken("ETHEREAL", "transcend")
            farm_data['chickens'] = [for_chicken for for_chicken in farm_data['chickens'] if for_chicken['rarity'] != "ASCENDED"]
            farm_data['chickens'].extend(extra_ascended_chickens)
            farm_data['chickens'].append(transcended_chicken)
            await Farm.update(ctx.author.id, chickens=farm_data['chickens'])
            await send_bot_embed(ctx, description=f":white_check_mark: {ctx.author.display_name}, you have transcended your chickens to an **{get_rarity_emoji('ETHEREAL')} ETHEREAL Chicken.**")
        return
        
    async def verify_player_has_sustainable(self, farm_data: dict) -> bool:
        """
        Verify if the player has the sustainable farmer role.

        Args:
            farm_data (dict): The farm data.

        Returns:
            bool
        """
        return farm_data['farmer'] == "Sustainable Farmer"
            
async def setup(bot):
    await bot.add_cog(ChickenEvents(bot))