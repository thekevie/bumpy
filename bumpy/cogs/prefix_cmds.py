from diskord.ext import commands
import diskord

from main import read_config, db, db_settings, db_blocked, db_ratelimit, db_stats, db_premium, db_codes

class prefix_cmds(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command(aliases=["bump"], description="Command to bumps your server")
    async def _bump(self, ctx):
        #await ctx.invoke(self.client.get_application_command("bump"))
        await ctx.reply("Bumpy is now using slash commands. If you cant use them reinvite Bumpy to your server using this link\n https://dsc.gg/bumpy")
        
def setup(client):
    client.add_cog(prefix_cmds(client))