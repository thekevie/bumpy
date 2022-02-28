from diskord.ext import commands
from diskord.ui import Button, View
import diskord
import datetime

import pymongo
from main import read_config
MongoClient = pymongo.MongoClient(read_config['mongodb'])
db = MongoClient.db
blocked_db = db["blocked"]

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
            await channel.send(self.client.get_user(read_config["owners"][0]).mention, embed=em)
        else:
            return
        
    @diskord.application.slash_command(description="Block a server from bumpy", default_permission=False, guild_ids=[832743824181952534])
    @commands.is_owner()
    @diskord.application.option('id')
    async def block(self, ctx, id):
        id = int(id)
        r = blocked_db.find_one({"guild_id": ctx.guild.id})
        if r is None:
            data = {"guild_id": id, "blocked": False}
            blocked_db.insert_one(data)
            r = blocked_db.find_one({"guild_id": ctx.guild.id})
            
        res = r['blocked']
        if res is True: 
            data = {"$set":{"blocked": True}}
            blocked_db.update_one({"guild_id": ctx.guild.id}, data)
            await ctx.respond("**Server was blocked**", ephemeral=True)
            
        elif res is False:
            data = {"$set":{"blocked": False}}
            blocked_db.update_one({"guild_id": ctx.guild.id}, data)
            await ctx.respond("**Server was unblocked**", ephemeral=True)

        
      
def setup(client):
    client.add_cog(report(client))
