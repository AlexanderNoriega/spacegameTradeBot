import math

import discord

from game_logic import resources
from utils.data_utils import get_account, new_account
from utils.reaction_utils import add_wait_for_response


async def help_menu(
    user: discord.User,
    channel: discord.TextChannel,
    guild: discord.guild,
):
    await channel.send(
        "This bot helps with keeping track of your money and trade."
        "\n Possible actions:"
        "\n`$Help`"
        "\n`$Trade`"
    )


async def trade_menu(
    user: discord.User,
    channel: discord.TextChannel,
    guild: discord.guild,
):
    text = []
    options = {}
    # 1. User can create a profile that keeps track of their finances (Ym in total)
    account = get_account(user=user, guild=guild)
    if not account:
        account = new_account(user=user, guild=guild)
    text += [f"Account balance: {account.get('balance', 0)}"]
    # 2. They can look up the existing price of goods for sale and purchase from the merchantmen
    #    a. There is some controlled way I can edit those prices while others cannot
    text += [":one: Look up a price"]
    options["one"] = (look_up_price_menu, {"user": user, "channel": channel, "guild": guild})
    # 3. They can use the bot to sell or buy those goods
    #       a. They input the good name, the quantity, and the quality
    #       b. The bot confirms the order and adjusts the Ym total
    text += [":two: Buy or sell products"]
    options["two"] = (buy_sell_menu, {"user": user, "channel": channel, "guild": guild})
    # 4. A way to save a 'shopping list' to the save so they can quickly sell repeated goods without issue
    #      a. an ability to load and then edit existing shopping lists
    text += [":three: Manage shopping list"]
    options["three"] = (shopping_list_menu, {"user": user, "channel": channel, "guild": guild})
    text += [":four: Never mind"]
    options["four"] = (None, {})

    message = await channel.send("\n".join(text))
    await add_wait_for_response(message=message, options=options, channel=channel)


async def shopping_list_menu(
        user: discord.User,
        channel: discord.TextChannel,
        guild: discord.guild,
):
    await channel.send("TODO: shopping list menu")


async def buy_sell_menu(
        user: discord.User,
        channel: discord.TextChannel,
        guild: discord.guild,
):
    await channel.send("TODO: buy/sell menu")


async def look_up_price_menu(
        user: discord.User,
        channel: discord.TextChannel,
        guild: discord.guild,
        page:int = 0
):
    all_resources = list(resources.resources.keys())
    max_displayed = 20
    n_pages = math.ceil(len(all_resources) / max_displayed)
    page = page % n_pages
    start = page * max_displayed
    end = start + max_displayed
    list_resources = all_resources[start:end]
    text = []
    for resource_key in list_resources:
        resource = resources.resources[resource_key]
        name = resource.name
        price = resource.price(guild)
        text += [f"{name}: {price} Ym per unit"]

    options = {}
    text += [":one: Previous page"]
    options["one"] = (look_up_price_menu, {"user": user, "channel": channel, "guild": guild, "page": page-1})
    text += [":two: Next page"]
    options["two"] = (look_up_price_menu, {"user": user, "channel": channel, "guild": guild, "page": page+1})

    message = await channel.send("\n".join(text))
    await add_wait_for_response(message=message, options=options, channel=channel)


async def handle_message(
    user: discord.User,
    channel: discord.TextChannel,
    message: discord.Message,
    client: discord.Client,
    guild: discord.guild,
) -> None:
    commands = {
        "$help": (help_menu, {"user": user, "channel": channel, "guild": guild}),
        "$trade": (trade_menu, {"user": user, "channel": channel, "guild": guild}),
    }
    if message.content.lower() in commands:
        async with channel.typing():
            func, kwargs = commands[message.content.lower()]
            try:
                await message.delete()
            except Exception as e:
                print("failed to delete message:", e)
            await func(**kwargs)
