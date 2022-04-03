import diskord
from diskord.ext import commands, tasks

from utils.functions import *

class events(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @tasks.loop(hours=3)
    async def premium_check(self):
        guilds = db.settings.find({"premium.status": True, "guild_id":{"$exists": True}})
        for guild in guilds:
            if guild["premium"]["expires"] < datetime.datetime.today():
                db.settings.update_one({"guild_id": guild["guild_id"]}, {"$set":{"premium.status": False, "premium.expires": None}})
        users = db.settings.find({"premium.status": True, "user_id":{"$exists": True}})
        for user in users:
            if user["premium"]["expires"] < datetime.datetime.today():
                db.settings.update_one({"user_id": user["user_id"]}, {"$set":{"premium.status": False, "premium.expires": None}})

    @commands.Cog.listener()
    async def on_ready(self):
        print(self.client.user.name, f"is online")
        print(f"{len(self.client.guilds)} Servers")
        print(f"{len(self.client.users)} Users")
        await self.client.change_presence(status=diskord.Status.online)
        
        self.premium_check.start()
      
        if not self.client.user.id == 880766859534794764:
            return
        
        for setting in db.settings.find({"guild_id":{"$exists": True}}):  
            guild_id = setting["guild_id"]
            guild = self.client.get_guild(guild_id)
            if not guild in self.client.guilds:
                if not setting["premium.status"] is True:
                    db.settings.delete_one({"guild_id": guild_id})
    
    @commands.Cog.listener()
    async def on_guild_leave(self, ctx):  
        db.settings.delete_one({"guild_id": ctx.guild.id})
      
def setup(client):
    client.add_cog(events(client))