import discord
from discord.ext import commands, tasks
import datetime

from utils.functions import *

class events(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @tasks.loop(hours=3)
    async def check(self):
        guilds = db.settings.find({"premium.status": True, "guild_id":{"$exists": True}})
        if guilds:
            for guild in guilds:
                if not guild["premium"]["expires"] is False:
                    if guild["premium"]["expires"] < datetime.datetime.today():
                        db.settings.update_one({"guild_id": guild["guild_id"]}, {"$unset":{"premium": ""}})
        users = db.settings.find({"premium.status": True, "user_id":{"$exists": True}})
        if users:
            for user in users:
                if not user["premium"]["expires"] is False:
                    if user["premium"]["expires"] < datetime.datetime.today():
                        db.settings.update_one({"user_id": user["user_id"]}, {"$unset":{"premium": ""}})
        db.settings.delete_many({"user_id":{"$exists": True}, "premium":{"$exists": False}, "blocked":{"$exists": False}})
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(self.client.user.name, f"is online")
        print(f"{len(self.client.guilds)} Servers")
        
        self.check.start()
      
        if not self.client.user.id == 880766859534794764:
            return
        
        for setting in db.settings.find({"guild_id":{"$exists": True}}):  
            guild_id = setting["guild_id"]
            guild = self.client.get_guild(guild_id)
            if not guild in self.client.guilds:
                if db.settings.find({"guild_id": guild_id, "premium.status": True}):
                    pass
                else:
                    db.settings.delete_one({"guild_id": guild_id})
      
async def setup(client):
    await client.add_cog(events(client))