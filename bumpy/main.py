import os 
import diskord
from diskord.ext import commands

import json
import pymongo

def read_config():
    with open("config.json") as file:
        return json.load(file)

read_config = read_config()

MongoClient = pymongo.MongoClient(read_config['mongodb'])
db = MongoClient.db

db_settings = db["settings"]
db_blocked = db["blocked"]
db_ratelimit = db["cooldown"]
db_stats = db["stats"]
db_premium = db["premium"]
db_codes = db["codes"]

intents = diskord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=read_config["prefix"], owner_ids = read_config["owners"], intents = intents)
  
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f"cogs.{filename[:-3]}")

client.run(read_config["token"])