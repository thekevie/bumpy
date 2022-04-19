from diskord.ext import commands
import diskord
import datetime
import time

from utils.functions import *

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
        add_command_stats("report")
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
        
    @diskord.application.slash_command(description="Block a server from bumpy", guild_ids=[832743824181952534])
    @commands.is_owner()
    @diskord.application.option('id')
    @diskord.application.option("type", choices=[
        diskord.OptionChoice(name="User", value="user"),
        diskord.OptionChoice(name="Guild", value="guild"),
    ])
    @diskord.application.option('reason', required=False)
    async def block(self, ctx, id, type, reason=None):
        id = int(id)
        if type == "user":
            settings = check_user(id, "block")                
            if settings["banned"]["status"] is True:
                db.settings.update_one({"user_id": id}, {"$set":{"banned": False}})
                await ctx.respond(f"User: `{id}` has been *unbanned*", ephemeral=True)
            if settings["banned"] is False:
                db.settings.update_one({"user_id": id}, {"$set":{"banned.status": True, "banned.reason": reason}})
                await ctx.respond(f"User: `{id}` has been *banned*", ephemeral=True)
                
        elif type == "guild":
            settings = check_guild(id, "block")
            if settings["banned"]["status"] is True:
                db.settings.update_one({"guild_id": id}, {"$set":{"banned": False}})
                await ctx.respond(f"Guild: `{id}` has been *unbanned*", ephemeral=True)    
            elif settings["banned"] is False:
                db.settings.update_one({"guild_id": id}, {"$set":{"banned.status": True, "banned.reason": reason}})
                await ctx.respond(f"Guild: `{id}` has been *banned*", ephemeral=True)
                guilds = db.settings.find({}, {"_id": 0, "bump_channel": 1})
                for guild in guilds:
                    channel = self.client.get_channel(guild["bump_channel"])
                    async for message in channel.history():
                        for embed in message.embeds:
                            if int(id) in embed.author.name:
                                await message.delete()
                                time.sleep(2)        
      
def setup(client):
    client.add_cog(report(client))
