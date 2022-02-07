import discord
from discord.ext import commands, tasks
import asyncio
import random

from main import read_config

import pymongo
import topgg

MongoClient = pymongo.MongoClient(read_config['mongodb'])
db = MongoClient.db["settings"]
ratelimit_db = db["cooldown"]

class events(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.status.start()
        
    @tasks.loop()
    async def status(self):
      for status in random.sample(read_config["status"], 1):
          
        if status[0] == "Watching":
            if status[1] == "Users":
                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.client.users)} Users"))
            elif status[1] == "Servers":
                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.client.guilds)} Servers"))
            else:  
                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status[1]))
        elif status[0] == "Playing":
            await self.client.change_presence(activity=discord.Game(name=status[1]))   
        elif status[0] == "Listening":
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status[1]))
        elif status[0] == "Streaming":
            await self.client.change_presence(activity=discord.Streaming(name=status[1], url=status[2]))
        await asyncio.sleep(10)

    @status.before_loop
    async def before_status(self):
        await self.client.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        print(self.client.user.name, f"is online")
        print(f"{len(self.client.guilds)} Servers")
        await self.client.change_presence(status=discord.Status.online)
      
        if not self.client.user.id == 880766859534794764:
            return
      
        for x in db.find({},{"_id": 0, "guild_id": 1}):
            id = int(x["guild_id"])
            guild = self.client.get_guild(id)
            if not guild in self.client.guilds:
                db.delete_one({"guild_id": id})
                ratelimit_db.delete_one({"guild_id": id})
            else:
                pass
    
    @commands.Cog.listener()
    async def on_guild_leave(self, ctx):  
        db.delete_one({"guild_id": ctx.guild.id})
        ratelimit_db.delete_one({"guild_id": id})
          
      
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == ".bump":
            await message.channel.send("Bumpy is now using slash commands. If you cant use them reinvite Bumpy to your server using this link https://dsc.gg/bumpy")
      
def setup(client):
    client.add_cog(events(client))