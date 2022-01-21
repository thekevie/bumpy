from discord.commands import slash_command, Option, permissions
from discord.ext import commands
from discord.ui import Button, View
import discord
import datetime

from main import read_config

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button, interaction):
        await interaction.response.edit_message(content="**Report was Posted**", embed=None, view=None)
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button, interaction):
        await interaction.response.edit_message(content="**Report was Removed**", embed=None, view=None)
        self.value = False
        self.stop()

class report(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash_command(description="Report a server")
    async def report(self, ctx, 
        id: discord.Option(str, "Send the Guild ID for the server you want to report"),
        reason: discord.Option(str, "Why is this server breaking the rules")
    ):
        id = int(id)
        em = discord.Embed(title="Report", description="By pushing the **Confirm** button you agree on being message by the bumpy support team. Here is the report check so everything is right.", color=discord.Colour.blue())
        em.add_field(name="Guild Name", value=self.client.get_guild(id).name)
        em.add_field(name="Guild ID", value=id)
        em.add_field(name="Reason", value=reason, inline=False)
        view = Confirm()
        await ctx.respond(embed=em, view=view, ephemeral=True)
        await view.wait()
        if view.value is True:
            chn = self.client.get_guild(id).text_channels[0]
            invite = await chn.create_invite(unique=False, max_age = 0, max_uses = 0, temporary=False)
            channel = self.client.get_channel(933680144781037598)
            em = discord.Embed(title="Report", color=discord.Colour.blue())
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
        
      
def setup(client):
    client.add_cog(report(client))