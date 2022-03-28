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
db_stats = db["stats"]
db_premium = db["premium"]
db_codes = db["codes"]

def check(ctx):
    if not db_settings.find_one({"guild_id": ctx.guild.id}):
        data = {"guild_id": ctx.guild.id, "status": "OFF", "bump_channel": None, "invite_channel": None, "description": None, "cooldown": None}
        db_settings.insert_one(data) 
    
    if not db_settings.find_one({"guild_id": ctx.guild.id}, {"_id": 0, "status": 1}):
        db_settings.update_one({"guild_id": ctx.guild.id}, {"$set":{"status": "OFF"}})
        
    if not db_settings.find_one({"guild_id": ctx.guild.id}, {"_id": 0, "bump_channel": 1}):
        db_settings.update_one({"guild_id": ctx.guild.id}, {"$set":{"bump_channel": None}})
        
    if not db_settings.find_one({"guild_id": ctx.guild.id}, {"_id": 0, "invite_channel": 1}):
        db_settings.update_one({"guild_id": ctx.guild.id}, {"$set":{"invite_channel": None}})
        
    if not db_settings.find_one({"guild_id": ctx.guild.id}, {"_id": 0, "description": 1}):
        db_settings.update_one({"guild_id": ctx.guild.id}, {"$set":{"description": None}})
    
    if not db_settings.find_one({"guild_id": ctx.guild.id}, {"_id": 0, "cooldown": 1}):
        db_settings.update_one({"guild_id": ctx.guild.id}, {"$set":{"cooldown": None}})
        
    return db_settings.find_one({"guild_id": ctx.guild.id})

async def bump_check(ctx):
    settings = db_settings.find_one({"guild_id": ctx.guild.id})
    try:
        bump_channel = client.get_channel(settings["bump_channel"])
        await bump_channel.send("Checking for Bump Channel", delete_after=2)
    except diskord.HTTPException:
        return False, "I dont have Permission or the channel do not exist"
    return True, None

def add_command_stats(command):
    if not db_stats.find_one({}, {"_id": 0, "bumps": 1, "commands": 1}):
        data = {"bumps": 0, "commands": 0}
        db_stats.insert_one(data)
    stats = db_stats.find_one({}, {"bumps": 1, "commands": 1})    
    data = {"$set":{"commands": stats["commands"] + 1}}
    db_stats.update_one({"_id": stats["_id"]}, data)
    if command == "bump":
        data = {"$set":{"bumps": stats["bumps"] + 1}}
        db_stats.update_one({"_id": stats["_id"]}, data)
        

intents = diskord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=read_config["prefix"], owner_ids = read_config["owners"], intents = intents)
  
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f"cogs.{filename[:-3]}")

client.run(read_config["token"])