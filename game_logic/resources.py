import csv
import os

import discord

from utils.data_utils import get_price, update_price

resources = {}


class Resource:
    def __init__(
        self,
        resource_name: str,
        resource_group: str,
        price_I: str,
        price_II: str,
        price_III: str,
        price_IV: str,
        price_V: str,
    ):
        global resources
        self.name = resource_name
        self.resource_group = resource_group
        resources[resource_name.lower()] = self
        self.price_I_default = price_I
        self.price_II_default = price_II
        self.price_III_default = price_III
        self.price_IV_default = price_IV
        self.price_V_default = price_V

    def get_default_price(self, quality: str):
        if quality == "I":
            return self.price_I_default
        elif quality == "II":
            return self.price_II_default
        elif quality == "III":
            return self.price_III_default
        elif quality == "IV":
            return self.price_IV_default
        elif quality == "V":
            return self.price_V_default
        else:
            return 0

    def price(self, quality: str, guild: discord.Guild) -> int:
        resource_dict = get_price(self.name, guild)
        return resource_dict.get(f"price_{quality}", self.get_default_price(quality))

    def set_price(self, quality: str, new_price: int, guild: discord.Guild) -> None:
        resource_dict = get_price(self.name, guild)
        resource_dict[f"price_{quality}"] = new_price
        update_price(resource=resource_dict, guild=guild)


def load_resources():
    if not resources.keys():
        with open(os.path.join("content", "prices.csv"), "r") as f:
            csvreader = csv.DictReader(f)
            for row in csvreader:
                Resource(**row)
