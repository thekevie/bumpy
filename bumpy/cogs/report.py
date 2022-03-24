from diskord.ext import commands
from diskord.ui import Button, View
import diskord
import datetime
import time

from main import read_config, db, db_settings, db_blocked, db_ratelimit, db_stats, db_premium, db_codes

class Confirm(diskord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @diskord.ui.button(label="Confirm", style=diskord.ButtonStyle.green)
    async def confirm(self, button, interaction):
        await interaction.response.edit_message(content="**Report was Posted**", embed=None, view=None)
        self.value = True
        self.stop()

    @diskord.ui.button(label="Cancel", style=diskord.ButtonStyle.red)
    async def cancel(self, button, interaction):
        await interaction.response.edit_message(content="**Report was Removed**", embed=None, view=None)
        self.value = False
        self.stop()

class report(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @diskord.application.slash_command(description="Report a server")
    @diskord.application.option('id', description="Send the Guild ID for the server you want to report")
    @diskord.application.option('reason', description="The reason for the report")
    async def report(self, ctx, id, reason):
        id = int(id)
        em = diskord.Embed(title="Report", description="By pushing the **Confirm** button you agree on being message by the bumpy support team. Here is the report check so everything is right.", color=diskord.Colour.blue())
        em.add_field(name="Guild Name", value=self.client.get_guild(id).name)
        em.add_field(name="Guild ID", value=id)
        em.add_field(name="Reason", value=reason, inline=False)
        view = Confirm()
        await ctx.respond(embed=em, view=view, ephemeral=True)
        await view.wait()
        if view.value is True:
            chn = self.client.get_guild(id).text_channels[0]
            invite = await chn.create_invite(unique=False, max_age = 0, max_uses = 0, temporary=False)
            channel = self.client.get_channel(932557305340391464)
            em = diskord.Embed(title="Report", color=diskord.Colour.blue())
            em.set_author(name=f"{ctx.author.display_name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar.url)
            em.add_field(name="Guild Name", value=self.client.get_guild(id).name, inline=False)
            em.add_field(name="Guild ID", value=id, inline=False)
            em.add_field(name="Invite", value=invite, inline=False)
            em.add_field(name="Reason", value=reason, inline=False)
            em.add_field(name="Date", value=datetime.datetime.now(), inline=False)
            em.set_footer(text=f"USER ID: {ctx.author.id}")
            await channel.send(self.client.get_user(self.config["owners"][0]).mention, embed=em)
        else:
            return
        
    @diskord.application.slash_command(description="Block a server from bumpy", default_permission=False, guild_ids=[832743824181952534])
    @commands.is_owner()
    @diskord.application.option('id')
    @diskord.application.option('reason', required=False)
    async def block(self, ctx, id, reason=None):
        id = int(id)
        if not db_blocked.find_one({"guild_id": id}):
            data = {"guild_id": id, "blocked": False}
            db_blocked.insert_one(data)
            
        b_db = db_blocked.find_one({"guild_id": id})
            
        if b_db['blocked'] is False: 
            data = {"$set":{"blocked": True, "reason": reason}}
            db_blocked.update_one({"guild_id": id}, data)
            await ctx.respond("**Server was blocked**", ephemeral=True)
            servers = db_settings.find({}, {"_id": 0, "status": 1, "bump_channel": 1})
            for server in servers:
                channel = self.client.get_channel(server["bump_channel"])
                async for message in channel.history():
                    for embed in message.embeds:
                        if str(id) in embed.author.name:
                            await message.delete()
                            time.sleep(3)
            
        elif b_db['blocked'] is True:
            db_blocked.delete_one({"guild_id": id})
            await ctx.respond("**Server was unblocked**", ephemeral=True) 

        
      
def setup(client):
    client.add_cog(report(client))
