from diskord.ext import commands
import diskord

from main import read_config, db, check, add_command_stats, db_settings

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
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx):
        add_command_stats("settings")
        pass
    
    @settings.sub_command(name="view", description="Show current settings")
    async def _view(self, ctx):
        add_command_stats("settings_view")
        settings = check(ctx)
        em = diskord.Embed(title="Server Settings", color=diskord.Colour.blue())
        em.add_field(name="Status", value=settings["status"])
        em.add_field(name="Bump-channel", value=get_bump_channel(settings))
        em.add_field(name="Invite-channel", value=get_invite_channel(settings))
        em.add_field(name="Description", value=get_description(settings))
        await ctx.respond(embed=em)
    
    @settings.sub_command(name="status", description="Turn on/off bumpy in your server")
    @diskord.application.option("action", choices=[
        diskord.OptionChoice(name="Enable", value="ON"),
        diskord.OptionChoice(name="Disable", value="OFF"),
    ])
    async def _status(self, ctx, action):
        add_command_stats("settings_status")
        check(ctx) 
        data = {"$set":{"status": action}}
        db_settings.update_one({"guild_id": ctx.guild.id}, data)
        if action == "ON":
            action = "Enabled"
        elif action == "OFF":
            action = "Disabled"
        await ctx.respond(f"*Bumpy is now {action}*")
    
    @settings.sub_command(name="invite-channel", description="Set your invite-channel")
    @diskord.application.option("channel")
    async def _invite_channel(self, ctx, channel: diskord.TextChannel):
        add_command_stats("settings_invite_channel")
        check(ctx)
        data = {"$set":{"invite_channel": channel.id}}
        db_settings.update_one({"guild_id": ctx.guild.id}, data)
        await ctx.respond(f"*Invite Channel was set to <#{channel.id}>*")
    
    @settings.sub_command(name="bump-channel", description="Set your bump-channel")
    @diskord.application.option("channel")
    async def _bump_channel(self, ctx, channel: diskord.TextChannel):
        add_command_stats("settings_bump_channel")
        check(ctx)
        data = {"$set":{"bump_channel": channel.id}}
        db_settings.update_one({"guild_id": ctx.guild.id}, data)
        await ctx.respond(f"*Bump Channel was set to <#{channel.id}>*")
    
    @settings.sub_command(name="description", description="Set your server-description")
    @diskord.application.option("description")
    async def _description(self, ctx, description):
        add_command_stats("settings_description")
        check(ctx)
        data = {"$set":{"description": description}}
        db_settings.update_one({"guild_id": ctx.guild.id}, data)
        await ctx.respond(f"*Server Description was set to*\n\n{description}")
            
def setup(client):
    client.add_cog(settings(client))