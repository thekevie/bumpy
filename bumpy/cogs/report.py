from discord.commands import slash_command, Option, permissions
from discord.ext import commands
from discord.ui import Button, View
import discord
import asyncio

from main import read_config

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await interaction.response.send_message("**Report was sent**", ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("**Report was canceled**", ephemeral=True)
        self.value = False
        self.stop()

class report(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash_command(description="Report a server", guild_id=[875451993462825000])
    async def report(self, ctx, server: discord.Option(str, "Send the Guild ID for the server you want to report")):
        em = discord.Embed(title="Report", description="By pushing the **Confirm** button you agree on being message by the bumpy support team. Here is the report check so everything is right.", color=discord.Colour.blue())
        em.add_field(name="Guild ID", value=server)
        em.add_field(name="Guild Name", value=self.client.get_guild(id).name)
        view = Confirm()
        await ctx.respond(embed=em, view=view, ephemeral=True)
        await view.wait()
        if view.value:
            channel = self.client.get_channel(932557305340391464)
            em = discord.Embed(title="Report", color=discord.Colour.blue())
            em.add_field(name="Guild Name", value=self.client.get_guild(id).name)
            em.add_field(name="Guild ID", value=server)
            em.add_field(name="Reporter", value=ctx.author.name + ctx.author.discriminator)
            channel.send(embed=em)
        else:
            return
        
      
def setup(client):
    client.add_cog(report(client))