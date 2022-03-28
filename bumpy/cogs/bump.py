from http import server
from logging import exception
from webbrowser import get
from diskord.ext import commands
import diskord

import datetime

from main import read_config, db, check, bump_check, add_command_stats, db_settings, db_blocked

def check_blocked(guild_id):
    if not db_blocked.find_one({"guild_id": guild_id}, {"_id": 0, "blocked": 1}):
        return False, None
    blocked = db_blocked.find_one({"guild_id": guild_id}, {"blocked": 1})
    if blocked["reason"]:
        reason = blocked["reason"]
    else:
        reason = "Not Provided"
    return True, reason

def check_for_server(ctx):
    settings = db_settings.find_one({"guild_id": ctx.guild.id})
    
    if settings["status"] == "OFF":
        return False, "Command has been disabled"
    if settings["bump_channel"] is None:
        return False, "Bump Channel was not found"
    if settings["description"] is None:
        return False, "Server Description was not found"
    if not ctx.guild.get_channel(settings["bump_channel"]):
        return False, "Bump Channel was not found"
    return True, None
    
async def check_ratelimit(ctx, client):        
    channel = client.get_channel(951095386959929355)
    date = datetime.datetime.now() - datetime.timedelta(hours=12)
    top = None
    dbl = None
    async for message in channel.history(after=date):
        user = message.mentions[0]
        if ctx.user == user:
            if "top.gg" in message.content:
                top = True
            if "dbl" in message.content:
                dbl = True
    
    rate = db_settings.find_one({"guild_id": ctx.guild.id}, {"_id": 0, "cooldown": 1})
    if rate["cooldown"] is None:
        then = datetime.datetime.now() + datetime.timedelta(minutes=read_config["cooldown"])
        data = {"$set":{"cooldown": then}}
        db_settings.update_one({"guild_id": ctx.guild.id}, data)
        return True, None 
                
    if datetime.datetime.now() <= rate["cooldown"]:
        left = rate["cooldown"] - datetime.datetime.now()
        seconds = left.total_seconds()
        minutes = seconds // 60
        
        if top is True:
            minutes = minutes - read_config["top"]
        if dbl is True:
            minutes = minutes - read_config["dbl"]            
            
        em = diskord.Embed(title="Server on Cooldown", description=f"You can bump again in {round(minutes)} minutes.", color=diskord.Colour.red())
        em.add_field(name="Note", value=read_config["note"], inline=False)
        em.set_footer(text=read_config["footer"])
        return False, em
    else:
        then = datetime.datetime.now() + datetime.timedelta(minutes=read_config["cooldown"])
        data = {"$set":{"cooldown": then}}
        db_settings.update_one({"guild_id": ctx.guild.id}, data)
        return True, None        
            
async def get_server(ctx):
    settings = db_settings.find_one({"guild_id": ctx.guild.id})
    invite_channel = ctx.guild.get_channel(settings["invite_channel"])
    if not invite_channel:
        invite_channel = ctx.guild.text_channels[0]   
    invite = await invite_channel.create_invite(unique=False, max_age=0, max_uses=0, temporary=False)
    
    em = diskord.Embed(color=diskord.Colour.blue())
    em.set_author(name=f"{ctx.guild.name} ({ctx.guild.id})", icon_url=ctx.guild.icon.url)
    em.add_field(name="Description", value=settings["description"], inline=False)
    em.add_field(name="Members", value=len(ctx.guild.members), inline=True)
    em.add_field(name="Channels", value=len(ctx.guild.channels), inline=True)
    em.add_field(name="Categories", value=len(ctx.guild.categories), inline=True)
    em.add_field(name="Emojis", value=len(ctx.guild.emojis), inline=False) #[emoji for emoji in ctx.guild.id]
    em.set_footer(text=read_config["footer"])
    
    button = diskord.ui.Button(label="Join Server", style=diskord.ButtonStyle.url, url=f"{invite}")
    view = diskord.ui.View()
    view.add_item(button)
    return em, view
                
class bump(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @diskord.application.slash_command(name="bump")
    async def bump(self, ctx):
        check(ctx)
        cb, reason = check_blocked(ctx.guild.id)
        if cb is True:
            em = diskord.Embed(title="Your server has been banned", description="If you want to appeal your ban [click here](https://discord.gg/KcH28tRtBu)", color=diskord.Colour.red())
            em.add_field(name="Reason", value=reason, inline=False)
            await ctx.respond(embed=em)
            return
        cfs, response = check_for_server(ctx)
        if cfs is False:
            em = diskord.Embed(title=response, color=diskord.Colour.red())
            await ctx.respond(embed=em)
            return
        
        status, res = await check_ratelimit(ctx, self.client)
        if status is False:
            await ctx.respond(embed=res)
            return
        
        status, res = await bump_check(ctx)
        if status is False:
            em = diskord.Embed(title=response, color=diskord.Colour.red())
            await ctx.respond(embed=em)
            return
        
        em = diskord.Embed(title="Bumping!", description="The server is beening bumped", color=diskord.Colour.blue())
        em.add_field(name="Note", value=read_config["note"], inline=False)
        em.set_footer(text=read_config["footer"])
        await ctx.respond(embed=em)
        
        server_embed, server_button = await get_server(ctx)
        
        channel_ids = db_settings.find({}, {"_id": 0, "status": 1, "bump_channel": 1})
        for item in channel_ids:
            channel = self.client.get_channel(item["bump_channel"])
            if channel:
                if item["status"] == "ON":
                    try:
                        await channel.send(embed=server_embed, view=server_button)
                    except Exception:
                        pass
        
        em = diskord.Embed(title="Bumped!", description="The server had been bumped.", color=diskord.Colour.green())
        em.add_field(name="Note", value=read_config["note"], inline=False)
        em.set_footer(text=read_config["footer"])
        await ctx.channel.send(embed=em)
        add_command_stats("bump")
        
def setup(client):
    client.add_cog(bump(client))