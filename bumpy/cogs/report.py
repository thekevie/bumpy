from discord.ext import commands
from discord import app_commands
import discord
import datetime
import time
from discord.app_commands import Choice, choices, Group, checks

from utils.functions import *

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction , button):
        await interaction.response.edit_message(content="Report was Posted", embed=None, view=None)
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction, button):
        await interaction.response.edit_message(content="Report was Removed", embed=None, view=None)
        self.value = False
        self.stop()

class report(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @app_commands.command(description="Report a server")
    async def report(self, interaction, id:str, reason:str):
        add_command_stats("report")
        id = int(id)
        em = discord.Embed(title="Report", description="By pushing the **Confirm** button you agree on being message by the bumpy support team. Here is the report check so everything is right.", color=discord.Colour.blue())
        em.add_field(name="Guild Name", value=self.client.get_guild(id).name)
        em.add_field(name="Guild ID", value=id)
        em.add_field(name="Reason", value=reason, inline=False)
        view = Confirm()
        await interaction.response.send_message(embed=em, view=view, ephemeral=True)
        await view.wait()
        if view.value is True:
            chn = self.client.get_guild(id).text_channels[0]
            invite = await chn.create_invite(unique=False, max_age = 0, max_uses = 0, temporary=False)
            channel = self.client.get_channel(932557305340391464)
            em = discord.Embed(title="Report", color=discord.Colour.blue())
            em.set_author(name=f"{interaction.user.display_name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
            em.add_field(name="Guild Name", value=self.client.get_guild(id).name, inline=False)
            em.add_field(name="Guild ID", value=id, inline=False)
            em.add_field(name="Invite", value=invite, inline=False)
            em.add_field(name="Reason", value=reason, inline=False)
            em.add_field(name="Date", value=datetime.datetime.now(), inline=False)
            em.set_footer(text=f"USER ID: {interaction.user.id}")
            await channel.send(self.client.get_user(read_config["owners"][0]).mention, embed=em)
        else:
            return
        
    @commands.command(description="Block a server from bumpy")
    @commands.is_owner()
    async def block(self, ctx, id:str, type:str, reason:str=None):
        if not type in ["user","guild"]:
            await ctx.send("b!block <guild_id> <user/guild> [reason]")
        id = int(id)
        if type == "user":
            settings = check_user(id, "block")                
            if settings["blocked"] is False:
                db.settings.update_one({"user_id": id}, {"$set":{"blocked": {"status": True, "reason": reason}}})
                await ctx.send(f"User: `{id}` has been *blocked*", ephemeral=True)
            elif settings["blocked"]["status"] is True:
                db.settings.update_one({"user_id": id}, {"$unset":{"blocked": ""}})
                await ctx.send(f"User: `{id}` has been *unblocked*", ephemeral=True)
                
        elif type == "guild":
            settings = check_guild(id, "block")
            if settings["blocked"] is False:
                db.settings.update_one({"guild_id": id}, {"$set":{"blocked": {"status": True, "reason": reason}}})
                await ctx.send(f"Guild: `{id}` has been *blocked*", ephemeral=True)
                guilds = db.settings.find({"bump_channel":{"$exists":True}})
                for guild in guilds:
                    channel = self.client.get_channel(guild["bump_channel"])
                    try:
                        async for message in channel.history():
                            for embed in message.embeds:
                                if str(id) in embed.author.name:
                                    await message.delete()
                                    time.sleep(2)
                    except Exception:
                        pass
            elif settings["blocked"]["status"] is True:
                db.settings.update_one({"guild_id": id}, {"$unset":{"blocked": ""}})
                await ctx.send(f"Guild: `{id}` has been *unblocked*", ephemeral=True)
      
async def setup(client):
    await client.add_cog(report(client))
