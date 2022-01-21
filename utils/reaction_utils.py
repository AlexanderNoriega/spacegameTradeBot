import discord


def number_to_word(number):
    if number == 0:
        return "zero"
    if number == 1:
        return "one"
    elif number == 2:
        return "two"
    elif number == 3:
        return "three"
    elif number == 4:
        return "four"
    elif number == 5:
        return "five"
    elif number == 6:
        return "six"
    elif number == 7:
        return "seven"
    elif number == 8:
        return "eight"
    elif number == 9:
        return "nine"
    elif number == 10:
        return "keycap_ten"
    else:
        return "robot"


emoji_map = {
    "zero": "0️⃣",
    "one": "1️⃣",
    "two": "2️⃣",
    "three": "3️⃣",
    "four": "4️⃣",
    "five": "5️⃣",
    "six": "6️⃣",
    "seven": "7️⃣",
    "eight": "8️⃣",
    "nine": "9️⃣",
    "keycap_ten": "🔟",
    "repeat": "🔁",
}


async def add_wait_for_response(message, options: dict, channel):
    if len(list(options.keys())) > 0:
        if isinstance(message, dict):
            message_id = message["id"]
            message = await channel.fetch_message(id=message_id)
        elif isinstance(message, discord.Message):
            message_id = message.id
        else:
            raise Exception(f"Unknown type for message: {message.__class__}")
        message_id = str(message_id)
        print(
            f"adding add_wait_for_response to message id {message_id} with options {options}"
        )

        waiting_for[message_id] = options
        for option in options:
            emoji = emoji_map.get(option, None)
            if emoji:
                # don't add reactions to a message that is already taken care of
                if message_id in waiting_for.keys():
                    try:
                        await message.add_reaction(emoji)
                    except discord.errors.NotFound as ex:
                        # ignore errors when trying to react to a message that was deleted
                        print("message already deleted", ex)


waiting_for = {}
