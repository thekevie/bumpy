from diskord.ext import commands
import diskord

from utils.functions import *

class prefix_cmds(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command(aliases=["bump"], description="Command to bumps your server")
    async def _bump(self, ctx):
        #add_command_stats("bump")
        #await ctx.invoke(self.client.get_application_command("bump"))
        await ctx.reply("Bumpy is now using slash commands. If you cant use them reinvite Bumpy to your server using this link\n https://dsc.gg/bumpy")
        
def setup(client):
    client.add_cog(prefix_cmds(client))