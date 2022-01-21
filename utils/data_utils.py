import os
import time
from functools import lru_cache

import certifi
import discord
from dotenv import load_dotenv
from pymongo import MongoClient
from typing import Optional

load_dotenv()
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")
DATABASE = "game_data_space_game_trader_bot"


@lru_cache(1)
def _get_client():
    print(f"Connecting to database using environment variables")
    url = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}/{DATABASE}?retryWrites=true&w=majority"
    return MongoClient(url, tlsCAFile=certifi.where())


@lru_cache(1)
def _get_database():
    client = _get_client()
    return client.get_database(DATABASE)


def _get_collection(name):
    db = _get_database()
    return db.get_collection(name=name)


def _get_list(owner_username: str, collection_name: str) -> list:
    collection = _get_collection(collection_name)
    return [x for x in collection.find({"owner": owner_username})]


def _add_to_list(collection_name: str, item: dict) -> None:
    collection = _get_collection(collection_name)
    collection.insert_one(item)


def get_account(user: discord.User, guild: discord.Guild) -> Optional[dict]:
    collection = _get_collection("accounts")
    accounts = [x for x in collection.find({"user": user.id, "guild": guild.id})]

    if len(accounts) > 1:
        print(f"User has more than 1 accounts! Defaulting to first.")
    elif len(accounts) == 0:
        return None
    else:
        return accounts[0]


def new_account(user: discord.User, guild: discord.Guild) -> dict:
    collection = _get_collection("accounts")
    if get_account(user, guild) is None:
        character = {"user": user.id, "guild": guild.id}
        collection.insert_one(character)
    time.sleep(1)
    return get_account(user, guild)


def update_account(account, user: discord.User, guild: discord.Guild) -> None:
    collection = _get_collection("accounts")
    collection.replace_one({"user": user.id, "guild": guild.id}, account)


def get_price(resource: str, guild: discord.Guild) -> Optional[dict]:
    collection = _get_collection("prices")
    prices = [x for x in collection.find({"resource": resource, "guild": guild.id})]

    if len(prices) > 1:
        print(f"More than one price found! Defaulting to first.")
    elif len(prices) == 0:
        return {"resource": resource, "guild": guild.id}
    else:
        return prices[0]


def update_price(resource: dict, guild: discord.Guild) -> None:
    collection = _get_collection("prices")
    collection.replace_one(
        {"resource": resource["resource"], "guild": guild.id}, resource
    )
