import os 
import diskord
from diskord.ext import commands

import json

import topgg

def read_config():
    with open("config.json") as file:
        return json.load(file)

read_config = read_config()

intents = diskord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=read_config["prefix"], owner_ids = read_config["owners"], intents = intents)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f"cogs.{filename[:-3]}")

client.run(read_config["token"])