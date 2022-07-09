from discord.ext import commands
import discord
from discord import app_commands

from utils.functions import *
class bump(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @app_commands.command(name="bump", description="Push the server to more users server")
    async def bump(self, interaction):
        check_guild(interaction.guild.id, "bump")
        cb, reason, title = check_blocked(interaction.guild.id, interaction.user.id)
        if cb is True:
            em = discord.Embed(title=title, description="If you want to appeal your block [click here](https://discord.gg/KcH28tRtBu)", color=discord.Colour.red())
            em.add_field(name="Reason", value=reason, inline=False)
            await interaction.response.send_message(embed=em)
            return

        cfs, response = check_for_server(interaction)
        if cfs is False:
            em = discord.Embed(title=response, color=discord.Colour.red())
            await interaction.response.send_message(embed=em)
            return

        status, response = await bump_check(interaction, self.client)
        if status is False:
            em = discord.Embed(title=response, color=discord.Colour.red())
            await interaction.response.send_message(embed=em)
            return
        
        status, response = await check_ratelimit(interaction, self.client)
        if status is False:
            await interaction.response.send_message(embed=response)
            return
        
        em = discord.Embed(title="Bumping!", description="The server is being bumped", color=discord.Colour.blue())
        em.add_field(name="Note", value=read_config["note"], inline=False)
        await interaction.response.send_message(embed=em)
        add_command_stats("bump")
        
        server_embed, server_button = await get_server(interaction)
        
        channel_ids = db.settings.find({"bump_channel": {"$exists":True}})
        for item in channel_ids:
            try:
                channel = self.client.get_channel(item["bump_channel"])
            except Exception:
                pass
            if channel:
                try:
                    await channel.send(embed=server_embed, view=server_button)
                except Exception:
                    pass
        
        em = discord.Embed(title="Bumped!", description="The server has been bumped.", color=discord.Colour.green())
        em.add_field(name="Note", value=read_config["note"], inline=False)
        await interaction.channel.send(embed=em)
        
async def setup(client):
    await client.add_cog(bump(client))
