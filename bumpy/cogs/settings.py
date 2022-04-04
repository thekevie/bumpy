from diskord.ext import commands
import diskord

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
        
    @diskord.application.slash_command()
    async def settings(self, ctx):
        pass
    
    @settings.sub_command(name="view", description="Show current settings")
    async def _view(self, ctx):
        add_command_stats("settings_view")
        settings = check_guild(ctx.guild.id, "settings")
        em = diskord.Embed(title="Server Settings", color=diskord.Colour.blue())        
        em.add_field(name="Premium", value=get_premium_server(ctx.guild.id))
        em.add_field(name="Bump-channel", value=get_bump_channel(settings))
        em.add_field(name="Invite-channel", value=get_invite_channel(settings))
        em.add_field(name="Description", value=get_description(settings))
        await ctx.respond(embed=em)
    
    @settings.sub_command(name="invite-channel", description="Set your invite-channel")
    @commands.has_permissions(manage_guild=True)
    @diskord.application.option("channel")
    async def _invite_channel(self, ctx, channel: diskord.TextChannel):
        add_command_stats("settings_invite_channel")
        check_guild(ctx.guild.id, "settings")
        data = {"$set":{"invite_channel": channel.id}}
        db.settings.update_one({"guild_id": ctx.guild.id}, data)
        await ctx.respond(f"*Invite Channel was set to <#{channel.id}>*")
    
    @settings.sub_command(name="bump-channel", description="Set your bump-channel")
    @commands.has_permissions(manage_guild=True)
    @diskord.application.option("channel")
    async def _bump_channel(self, ctx, channel: diskord.TextChannel):
        add_command_stats("settings_bump_channel")
        check_guild(ctx.guild.id, "settings")
        data = {"$set":{"bump_channel": channel.id}}
        db.settings.update_one({"guild_id": ctx.guild.id}, data)
        await ctx.respond(f"*Bump Channel was set to <#{channel.id}>*")
    
    @settings.sub_command(name="description", description="Set your server-description")
    @commands.has_permissions(manage_guild=True)
    @diskord.application.option("description")
    async def _description(self, ctx, description):
        add_command_stats("settings_description")
        check_guild(ctx.guild.id, "settings")
        data = {"$set":{"description": description}}
        db.settings.update_one({"guild_id": ctx.guild.id}, data)
        await ctx.respond(f"*Server Description was set to*\n\n{description}")
            
def setup(client):
    client.add_cog(settings(client))