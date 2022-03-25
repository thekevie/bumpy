from diskord.ext import commands
import diskord

from main import read_config, db, check, add_command_stats, db_stats

class info(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @diskord.application.slash_command(name="info")
    async def info(self, ctx):
        add_command_stats("info")
        mongo = db.command("dbstats")
        dataSize = mongo["dataSize"]
        storageSize = mongo["storageSize"]
        used = dataSize / storageSize
        procent = used * 100
        procent = round(procent)
        stats = db_stats.find_one({}, {"bumps": 1, "commands": 1})
        bumps = stats["bumps"]
        cmds = stats["commands"]
        
        em = diskord.Embed(title="Bumpy Information", color=diskord.Colour.blue())
        em.description = "Comming Soon"
        await ctx.respond(embed=em)

def setup(client):
    client.add_cog(info(client))