import diskord
from diskord.ext import commands

from main import read_config, db, check, db_settings

class events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(self.client.user.name, f"is online")
        print(f"{len(self.client.guilds)} Servers")
        await self.client.change_presence(status=diskord.Status.online)
      
        if not self.client.user.id == 880766859534794764:
            return      
        
        for x in db_settings.find({},{"_id": 0, "guild_id": 1}):
            id = int(x["guild_id"])
            guild = self.client.get_guild(id)
            if not guild in self.client.guilds:
                db_settings.delete_one({"guild_id": id})
            else:
                pass
    
    @commands.Cog.listener()
    async def on_guild_leave(self, ctx):  
        db_settings.delete_one({"guild_id": ctx.guild.id})
      
def setup(client):
    client.add_cog(events(client))