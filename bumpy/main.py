import os 
import discord

import json

import topgg

def read_config():
    with open("config.json") as file:
        return json.load(file)

read_config = read_config()

intents = discord.Intents.default()
intents.members = True

client=discord.Bot(owner_ids = read_config["owners"], intents = intents)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f"cogs.{filename[:-3]}")

client.run(read_config["token"])