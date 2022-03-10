from diskord.ext import commands
import diskord
import sys
import os
import pymongo

from main import read_config

MongoClient = pymongo.MongoClient(read_config['mongodb'], tls=True, tlsCertificateKeyFile="./X509-cert.pem")
db = MongoClient.db
stats_db = db["stats"]

class info(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @diskord.application.slash_command(description="Some info about the bot")
    async def info(self, ctx):
      em = diskord.Embed(title="Bumpy Information", description="Bumpy is a discord bot that list server. You can use the command `/bump` to push your server so more users see it. If you need help with bumpy or have questions join our [support server](https://discord.gg/KcH28tRtBu)", colour=diskord.Colour.blue())
      em.add_field(name="⠀", value="[Terms Of Service](https://github.com/thekevie/bumpy/blob/main/TERMS.md)\n[Privacy Policy](https://github.com/thekevie/bumpy/blob/main/PRIVACY.md)\n[Rules](https://github.com/thekevie/bumpy/blob/main/RULES.md)\n")
      await ctx.respond(embed=em, ephemeral=True)
      
    @diskord.application.slash_command(description="Invite me to your server")
    async def invite(self, ctx):
      em = diskord.Embed(description=f"[Invite](https://dsc.gg/bumpy)", colour=diskord.Colour.blue())
      await ctx.respond(embed=em, ephemeral=True)
      
    @diskord.application.slash_command(description="The stats for bumpy")
    async def stats(self, ctx):
      mongo = db.command("dbstats")
      dataSize = mongo["dataSize"]
      storageSize = mongo["storageSize"]
      
      used = dataSize / storageSize
      procent = used * 100
      procent = round(procent)
      
      stats = stats_db.find_one({}, {"_id": 0, "bumps": 1})
      bumps = stats["bumps"]
      
      em = diskord.Embed(title="Bumpy Statistics", color=diskord.Colour.blue())
      em.add_field(name="Servers", value=len(self.client.guilds), inline=False)
      em.add_field(name="Language", value=f"Python {sys.version[0]}", inline=False)
      em.add_field(name="diskord", value=diskord.__version__, inline=False)
      em.add_field(name="Memory Used", value=f"{dataSize} MB | {procent}%", inline=False)
      em.add_field(name="Total Bumps", value=bumps, inline=False)
      await ctx.respond(embed=em, ephemeral=True)

    @diskord.application.slash_command(description="Vote for the bot to get perks")
    async def vote(self, ctx):
      em = diskord.Embed(colour=diskord.Colour.green())
      em.add_field(name='**TOP.GG**', value='[Vote Here](https://top.gg/bot/880766859534794764/vote)', inline=False)
      em.add_field(name='**dbl**', value='[Vote Here](https://discordbotlist.com/bots/bumpy-5009/upvote)', inline=False)
      await ctx.respond(embed=em, ephemeral=True)
      
def setup(client):
    client.add_cog(info(client))
