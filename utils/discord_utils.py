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
    options["one"] = (
        look_up_price_menu,
        {"user": user, "channel": channel, "guild": guild},
    )
    # 3. They can use the bot to sell or buy those goods
    #       a. They input the good name, the quantity, and the quality
    #       b. The bot confirms the order and adjusts the Ym total
    text += [":two: Buy or sell products"]
    options["two"] = (buy_sell_menu, {"user": user, "channel": channel, "guild": guild})
    # 4. A way to save a 'shopping list' to the save so they can quickly sell repeated goods without issue
    #      a. an ability to load and then edit existing shopping lists
    text += [":three: Manage shopping list"]
    options["three"] = (
        shopping_list_menu,
        {"user": user, "channel": channel, "guild": guild},
    )
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
    group: str = None,
    page: int = 0,
):
    all_resources = list(resources.resources.keys())

    if group:
        all_resources = [
            resource
            for resource in resources.resources.values()
            if resource.resource_group == group
        ]
        max_displayed = 15
        n_pages = math.ceil(len(all_resources) / max_displayed)
        page = page % n_pages
        start = page * max_displayed
        end = start + max_displayed
        list_resources = all_resources[start:end]
        text = []
        for resource in list_resources:
            name = resource.name
            line = f"**{name}**:"
            for quality in ["I", "II", "III", "IV", "V"]:
                price = resource.price(quality, guild)
                line += f" | {quality}={price} Ym |"
            text += [line]

        options = {}
        text += [":one: Previous page"]
        options["one"] = (
            look_up_price_menu,
            {
                "user": user,
                "channel": channel,
                "guild": guild,
                "page": page - 1,
                "group": group,
            },
        )
        text += [":two: Next page"]
        options["two"] = (
            look_up_price_menu,
            {
                "user": user,
                "channel": channel,
                "guild": guild,
                "page": page + 1,
                "group": group,
            },
        )

        message = await channel.send("\n".join(text))
        await add_wait_for_response(message=message, options=options, channel=channel)
    else:
        all_groups = list(
            set([resource.resource_group for resource in resources.resources.values()])
        )
        text = []
        options = {}
        numbers = ["one", "two", "three", "four", "five", "six", "seven", "eight"]
        for group, num in zip(all_groups[: len(numbers)], numbers[: len(all_groups)]):
            text += [f":{num}: {group}"]
            options[num] = (
                look_up_price_menu,
                {
                    "user": user,
                    "channel": channel,
                    "guild": guild,
                    "page": page,
                    "group": group,
                },
            )
        message = await channel.send("\n".join(text))
        await add_wait_for_response(message=message, options=options, channel=channel)


def lehvenstein_distance(str1: str, str2: str):
    """
    Honestly, not sure if this is a proper implementation.
    But it's what I came up with in 10 minutes, hehe.
    """

    mapping_1 = {}
    mapping_2 = {}

    for c in str1:
        mapping_1[c] = str1.count(c)
    for c in str2:
        mapping_2[c] = str2.count(c)

    add = 0
    remove = 0

    for key in set(mapping_1.keys()).union(set(mapping_2.keys())):
        n1 = mapping_1.get(key, 0)
        n2 = mapping_2.get(key, 0)
        if n1 > n2:
            add += n1 - n2
        elif n2 > n1:
            remove += n2 - n1

    return max(add, remove)


async def show_item_price(
    resource_name: str,
    user: discord.User,
    channel: discord.TextChannel,
    guild: discord.Guild,
):
    resource = resources.resources.get(resource_name, None)
    if resource:
        text = []
        name = resource.name
        for quality in ["I", "II", "III", "IV", "V"]:
            price = resource.price(quality, guild)
            text += [f"**Quality {quality} {name}**: {price} Ym"]
        await channel.send("\n".join(text))
    else:

        def lambdafunc(r):
            return lehvenstein_distance(r, resource_name)

        likely = min(list(resources.resources.keys()), key=lambdafunc)
        await channel.send(
            f"I couldn't find {resource_name}, but I assume you mean {likely}"
        )
        await show_item_price(likely, user, channel, guild)


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
    elif str(message.content.lower()).startswith("$lookup "):
        async with channel.typing():
            resource = message.content.lower()[len("$lookup ") :]
            await show_item_price(resource, user, channel, guild)
