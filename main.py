import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
from game_logic import resources
from utils.discord_utils import handle_message
from utils.reaction_utils import number_to_word, waiting_for

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# start the client
intents = discord.Intents().all()
client = commands.Bot(command_prefix="=", intents=intents)


@client.event
async def on_ready() -> None:
    await client.wait_until_ready()
    resources.load_resources()
    print("I'm ready.")


async def handle_response(
    user: discord.User,
    channel: discord.TextChannel,
    message: discord.Message,
    guild: discord.guild,
) -> None:
    await client.wait_until_ready()
    try:
        if user != client.user:
            await handle_message(
                user=user, channel=channel, message=message, client=client, guild=guild
            )
    except Exception as ex:
        await channel.send(":fire::robot::fire: I ran into an issue.. :sweat:")
        raise ex


@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User) -> None:
    print(f"reaction: {reaction}")
    await client.wait_until_ready()
    channel = reaction.message.channel
    message_id = str(reaction.message.id)
    if user == client.user:
        return
    try:
        print(f"{user.name} reacts to {message_id} with {reaction.emoji}")
        if message_id in waiting_for.keys():
            options = waiting_for[message_id]
            print(f"I have the following options for that ID: {options}")

            # figure out which emoji they used to react
            emoji = reaction.emoji
            if len(str(emoji)) > 1:
                emoji_number = int(str(emoji).split("️")[0])
                emoji_word = number_to_word(emoji_number)
            elif str(emoji) == "🔁":
                emoji_word = "repeat"
            else:
                emoji_word = emoji

            print(f"reaction emoji = {emoji} -> {emoji_word}")

            # determine if that emoji was an option
            if emoji_word in options.keys():

                # if so, clear all reactions and do what was chosen
                del waiting_for[message_id]
                await reaction.message.clear_reactions()
                await reaction.message.delete()
                (func, kwargs) = options[emoji_word]
                if func:
                    await func(**kwargs)
        else:
            print("I have no options for that message ID")
    except Exception as ex:
        await channel.send(":fire::robot::fire: I ran into an issue.. :sweat:")
        raise ex


@client.event
async def on_message(message: discord.Message) -> None:
    await client.wait_until_ready()

    # if this message was sent by me, another bot, or a webhook, ignore it.
    if message.author == client.user or message.webhook_id or message.author.bot:
        return

    await handle_response(message.author, message.channel, message, message.guild)


if __name__ == "__main__":
    client.run(TOKEN)
