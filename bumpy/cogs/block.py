from discord.commands import slash_command, Option, permissions
from discord.ext import commands
import discord
import pymongo

from main import read_config

MongoClient = pymongo.MongoClient(read_config['mongodb'])
sett = MongoClient.settings
blocked_db = sett["blocked"]

class block(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash_command(description="DEV ONLY: Block a server from bumpy", default_permission=False)
    @permissions.is_owner()
    async def block(self, ctx, id: discord.Option(str, "The guild id of the server you want to block")):
        id = int(id)
        r = blocked_db.find_one({"guild_id": ctx.guild.id})
        if r is None:
            data = {"guild_id": id, "blocked": True}
            blocked_db.insert_one(data)
        else:
            data = {"$set":{"blocked": True}}
            blocked_db.update_one({"guild_id": ctx.guild.id}, data)
        await ctx.respond("**Server was blocked**", ephemeral=True)
        
    @slash_command(description="DEV ONLY: Unblock a server from bumpy", default_permission=False)
    @permissions.is_owner()
    async def unblock(self, ctx, id: discord.Option(str, "The guild id of the server you want to block")):
        id = int(id)
        r = blocked_db.find_one({"guild_id": ctx.guild.id})
        if r is None:
            data = {"guild_id": id, "blocked": False}
            blocked_db.insert_one(data)
        else:
            data = {"$set":{"blocked": False}}
            blocked_db.update_one({"guild_id": ctx.guild.id}, data)
        await ctx.respond("**Server was unblocked**", ephemeral=True)
        
def setup(client):
    client.add_cog(block(client))