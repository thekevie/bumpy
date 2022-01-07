import os 
import discord

import json

def read_config():
    with open("config.json") as file:
        return json.load(file)

read_config = read_config()

client=discord.Bot(intents = discord.Intents.all())

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f"cogs.{filename[:-3]}")

client.run(read_config["token"])