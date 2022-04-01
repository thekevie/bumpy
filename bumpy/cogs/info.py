from diskord.ext import commands
import diskord
import sys

from utils.functions import *

class info(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @diskord.application.slash_command(name="botinfo", description="Show stats for Bumpy")
    async def botinfo(self, ctx):
        add_command_stats("botinfo")
        mongo = db.command("dbstats")
        dataSize = mongo["dataSize"]
        storageSize = mongo["storageSize"]
        used = dataSize / storageSize
        procent = used * 100
        procent = round(procent)
        stats = db.stats.find_one({}, {"bumps": 1, "commands": 1})
        bumps = stats["bumps"]
        commands = stats["commands"]
        
        guilds = len(self.client.guilds)
        users = len(self.client.users)
        
        info1 = f"**Developer:** kevie#9091\n**Guild Count:** {guilds}\n**User Count:** {users}\n\n"
        info2 = f"**Python:** {sys.version[0]}.{sys.version[2]}\n**Diskord:** {diskord.__version__}\n\n"
        info3 = f"**Memory Used:** {dataSize} MB | {procent}%\n\n"
        info4 = f"**Total Commands:** {commands}\n**Total Bumps:** {bumps}"
        
        em = diskord.Embed(title="Bumpy Information", color=diskord.Color.blue())
        em.description = f"{info1}{info2}{info3}{info4}"
        await ctx.respond(embed=em)
        
    @diskord.application.slash_command(name="info", description="Show information about Bumpy")
    async def info(self, ctx):
        add_command_stats("info")
        view = diskord.ui.View()
        
        invite_button = diskord.ui.Button(label="Invite", style=diskord.ButtonStyle.url, url="https://discord.com/api/oauth2/authorize?client_id=880766859534794764&permissions=137976179857&scope=bot%20applications.commands&redirect_uri=https%3A%2F%2Fdiscord.gg%2FKcH28tRtBu&response_type=code", row=1)
        view.add_item(invite_button)
        
        support_button = diskord.ui.Button(label="Support", style=diskord.ButtonStyle.url, url="https://discord.gg/KcH28tRtBu", row=1)
        view.add_item(support_button)
        
        rules_button = diskord.ui.Button(label="Rules", style=diskord.ButtonStyle.url, url="https://github.com/thekevie/bumpy/blob/main/RULES.md", row=1)
        view.add_item(rules_button)
        
        terms_button = diskord.ui.Button(label="Terms Of Service", style=diskord.ButtonStyle.url, url="https://github.com/thekevie/bumpy/blob/main/TERMS.md", row=2)
        view.add_item(terms_button)
        
        privacy_button = diskord.ui.Button(label="Privacy Policy", style=diskord.ButtonStyle.url, url="https://github.com/thekevie/bumpy/blob/main/PRIVACY.md", row=2)
        view.add_item(privacy_button)
        
        em = diskord.Embed(title="Bumpy Information", color=diskord.Color.blue())
        em.description = "Comming Soon"
        await ctx.respond(embed=em, view=view)
        
    @diskord.application.slash_command(name="vote", description="Get websites where you can vote on Bumpy")
    async def vote(self, ctx):
        add_command_stats("vote")
        view = diskord.ui.View()
        
        topgg_button = diskord.ui.Button(label="TOP.GG", style=diskord.ButtonStyle.url, url="https://top.gg/bot/880766859534794764/vote")
        view.add_item(topgg_button)
        
        dbl_button = diskord.ui.Button(label="DBL", style=diskord.ButtonStyle.url, url="https://discordbotlist.com/bots/bumpy-5009/upvote")
        view.add_item(dbl_button)
        
        em = diskord.Embed(title="Vote on Bumpy", description="If you vote for Bumpy on both websites you will get 10 minutes \nless cooldown on the bump command in any server.", color=diskord.Color.blue())
        await ctx.respond(embed=em, view=view)
        
    @diskord.application.slash_command(name="invite", description="Get the invite link to Bumpy")
    async def invite(self, ctx):
        add_command_stats("invite")
        view = diskord.ui.View()
        
        invite_button = diskord.ui.Button(label="Invite Me", style=diskord.ButtonStyle.url, url="https://discord.com/api/oauth2/authorize?client_id=880766859534794764&permissions=137976179857&scope=bot%20applications.commands&redirect_uri=https%3A%2F%2Fdiscord.gg%2FKcH28tRtBu&response_type=code")
        view.add_item(invite_button)
        
        support_button = diskord.ui.Button(label="Support Server", style=diskord.ButtonStyle.url, url="https://discord.gg/KcH28tRtBu")
        view.add_item(support_button)
        
        em = diskord.Embed(title="Invite Bumpy to your server", color=diskord.Color.blue())
        await ctx.respond(embed=em, view=view)
         
def setup(client):
    client.add_cog(info(client))