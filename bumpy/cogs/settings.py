from discord.ext import commands
import discord
from discord import app_commands
from discord.app_commands import Choice, choices, Group, checks

from utils.functions import *

def get_bump_channel(settings):
    if settings["bump_channel"] is None:
        return "None"
    else:
        return f"<#{settings['bump_channel']}>"
    
def get_invite_channel(settings):
    if settings["invite_channel"] is None:
        return "None"
    else:
        return f"<#{settings['invite_channel']}>"
    
def get_description(settings):
    if settings["description"] is None:
        return "None"
    else:
        return settings['description']
        
class settings(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    slash_settings = Group(
        name="settings",
        guild_only=True,
        default_permissions=False,
        description="Manage the servers settings"
    )
    
    @slash_settings.command(name="view", description="Show current settings")
    async def _view(self, interaction):
        add_command_stats("settings_view")
        settings = check_guild(interaction.guild.id, "settings")
        em = discord.Embed(title="Server Settings", color=discord.Colour.blue())        
        em.add_field(name="Premium", value=get_premium_server(interaction.guild.id))
        em.add_field(name="Bump-channel", value=get_bump_channel(settings))
        em.add_field(name="Invite-channel", value=get_invite_channel(settings))
        em.add_field(name="Description", value=get_description(settings))
        await interaction.response.send_message(embed=em)
    
    @slash_settings.command(name="invite-channel", description="Set your invite-channel")
    @commands.has_permissions(manage_guild=True)
    async def _invite_channel(self, interaction, channel: discord.TextChannel):
        add_command_stats("settings_invite_channel")
        check_guild(interaction.guild.id, "settings")
        data = {"$set":{"invite_channel": channel.id}}
        db.settings.update_one({"guild_id": interaction.guild.id}, data)
        await interaction.response.send_message(f"*Invite Channel was set to <#{channel.id}>*")
    
    @slash_settings.command(name="bump-channel", description="Set your bump-channel")
    @commands.has_permissions(manage_guild=True)
    async def _bump_channel(self, interaction, channel: discord.TextChannel):
        add_command_stats("settings_bump_channel")
        check_guild(interaction.guild.id, "settings")
        data = {"$set":{"bump_channel": channel.id}}
        db.settings.update_one({"guild_id": interaction.guild.id}, data)
        await interaction.response.send_message(f"*Bump Channel was set to <#{channel.id}>*")
    
    @slash_settings.command(name="description", description="Set your server-description")
    @commands.has_permissions(manage_guild=True)
    async def _description(self, interaction, description:str):
        add_command_stats("settings_description")
        check_guild(interaction.guild.id, "settings")
        data = {"$set":{"description": description}}
        db.settings.update_one({"guild_id": interaction.guild.id}, data)
        await interaction.response.send_message(f"*Server Description was set to*\n\n{description}")
            
async def setup(client):
    await client.add_cog(settings(client))