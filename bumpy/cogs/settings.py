from discord.commands import slash_command, permissions
from discord.ext import commands
from discord.ui import Button, View
import discord
import asyncio
import sys

import pymongo

from main import read_config

MongoClient = pymongo.MongoClient(read_config['mongodb'])
db = MongoClient.db
settings_db = db["settings"]
stats_db = db["stats"]

async def get_data(self, interaction):
  
  db = settings_db.find_one({"guild_id": interaction.guild.id}, {"_id": 0})
  
  if db['bump_channel'] is None:
      bump_channel = None
  else:
      bump_channel = self.client.get_channel(db['bump_channel'])
      if bump_channel:
          bump_channel = bump_channel.mention
      else:
          bump_channel = None

  if db['invite_channel'] is None:
      invite_channel = None
  else:
      invite_channel = self.client.get_channel(db['invite_channel'])
      if invite_channel:
          invite_channel = invite_channel.mention
      else:
          invite_channel = None
    
  em = discord.Embed(title="Bumpy Settings", description="Here you can change all settings for the bump command.", color=discord.Colour.blue())
  em.add_field(name="Status", value=db["status"], inline=True)
  em.add_field(name="Bump Channel", value=bump_channel, inline=True)
  em.add_field(name="Invite Channel", value=invite_channel, inline=True)
  em.add_field(name="Description", value=db["description"], inline=False)
  return em

class menu(discord.ui.View):
    def __init__(self, client):
        super().__init__(timeout=120)
        self.client = client
    
    @discord.ui.button(label="Enabled",style=discord.ButtonStyle.green, custom_id="enabled", row=0)
    async def on_button_callback(self, button, interaction):      
        data = {"$set":{"status": "ON"}}
        settings_db.update_one({"guild_id": interaction.guild.id}, data)  

        em = await get_data(self, interaction)
        view = menu(self.client)
        await interaction.response.edit_message(embed=em, view=view)

    @discord.ui.button(label="Disabled",style=discord.ButtonStyle.red, custom_id="disabled", row=0)
    async def off_button_callback(self, button, interaction):
        data = {"$set":{"status": "OFF"}}
        settings_db.update_one({"guild_id": interaction.guild.id}, data)

        em = await get_data(self, interaction)
        view = menu(self.client)
        await interaction.response.edit_message(embed=em, view=view)
        

    @discord.ui.button(label="Bump Channel", style=discord.ButtonStyle.blurple, custom_id="bump_channel", row=1)  
    async def bump_channel_button_callback(self, button, interaction):
        message_id = interaction.message.id
        await interaction.response.edit_message(content="**Mention the channel you want the bumps to be sent in!**", embed=None, view=None)
        
        def check(msg):
          return msg.author == interaction.user and msg.channel == interaction.channel
        
        try:
          answer = await self.client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
          await interaction.followup.edit_message(message_id=message_id, content="**Timeout**", embed=None, view=None)     
          return
        await answer.delete()
        channel_id = answer.channel_mentions[0].id
        
        data = {"$set":{f"bump_channel": channel_id}}
        settings_db.update_one({"guild_id": interaction.guild.id}, data)
      
        em = await get_data(self, interaction)
        view = menu(self.client)
        await interaction.followup.edit_message(message_id=message_id, content=None, embed=em, view=view)        
        
    @discord.ui.button(label="Invite Channel", style=discord.ButtonStyle.blurple, custom_id="invite_channel", row=1)  
    async def invite_channel_button_callback(self, button, interaction):
        message_id = interaction.message.id
        await interaction.response.edit_message(content="**Mention the channel you want the invite to be created in!**", embed=None, view=None)
        
        def check(msg):
          return msg.author == interaction.user and msg.channel == interaction.channel
        
        try:
          answer = await self.client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
          await interaction.followup.edit_message(message_id=message_id, content="**Timeout**", embed=None, view=None)     
          return  
        await answer.delete()
        channel_id = answer.channel_mentions[0].id
        
        data = {"$set":{f"invite_channel": channel_id}}
        settings_db.update_one({"guild_id": interaction.guild.id}, data)
      
        em = await get_data(self, interaction)
        view = menu(self.client)
        await interaction.followup.edit_message(message_id=message_id, content=None, embed=em, view=view)  
        
    @discord.ui.button(label="Description", style=discord.ButtonStyle.blurple, custom_id="set_description", row=1)  
    async def description_button_callback(self, button, interaction):
        message_id = interaction.message.id        
        await interaction.response.edit_message(content="**Send your server description in the channel below!**", embed=None, view=None)
        
        def check(msg):
          return msg.author == interaction.user and msg.channel == interaction.channel
        
        try:
          answer = await self.client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
          await interaction.followup.edit_message(message_id=message_id, content="**Timeout**", embed=None, view=None)     
          return    
        await answer.delete()
        description = answer.content
        
        data = {"$set":{f"description": description}}
        settings_db.update_one({"guild_id": interaction.guild.id}, data)
        
        em = await get_data(self, interaction)
        view = menu(self.client)
        await interaction.followup.edit_message(message_id=message_id, content=None, embed=em, view=view)
      
    @discord.ui.button(label="Exit", style=discord.ButtonStyle.gray, row=2)  
    async def exit_button_callback(self, button, interaction):
      await interaction.response.edit_message(content="Settings Was Saved", embed=None, view=None)      

class settings(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @slash_command(description="A command to change the settings")
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx: discord.ApplicationContext):
      r = settings_db.find_one({"guild_id": ctx.guild.id})
      if r is None:
        data = {"guild_id": ctx.guild.id, "status": "OFF", "bump_channel": None, "invite_channel": None, "description": None}
        settings_db.insert_one(data)
        
      em = await get_data(self, ctx)
      client = self.client
      view = menu(client)
      await ctx.respond(embed=em, view=view, ephemeral=True)

    @slash_command(description="Some info about the bot")
    async def info(self, ctx):
      em = discord.Embed(title="Bumpy Information", description="Bumpy is a discord bot that list server. You can use the command `/bump` to push your server so more users see it. If you need help with bumpy or have questions join our [support server](https://discord.gg/KcH28tRtBu)", colour=discord.Colour.blue())
      await ctx.respond(embed=em, ephemeral=True)
      
    @slash_command(description="The stats for bumpy")
    async def stats(self, ctx):
      mongo = db.command("dbstats")
      dataSize = mongo["dataSize"]
      storageSize = mongo["storageSize"]
      
      used = dataSize / storageSize
      procent = used * 100
      procent = round(procent)
      
      stats = stats_db.find_one({}, {"_id": 0, "bumps": 1})
      bumps = stats["bumps"]
      
      em = discord.Embed(title="Bumpy Statistics", color=discord.Colour.blue())
      em.add_field(name="Servers", value=len(self.client.guilds))
      em.add_field(name="Language", value=f"Python {sys.version[0]}")
      em.add_field(name="Pycord", value=discord.__version__)
      em.add_field(name="Memory Used", value=f"{dataSize} MB | {procent}%")
      em.add_field(name="Total Bumps", value=bumps)
      await ctx.respond(embed=em)

    @slash_command(description="Vote for the bot to get perks")
    async def vote(self, ctx):
      em = discord.Embed(colour=discord.Colour.green())
      em.add_field(name='**TOP.GG**', value='[Vote Here](https://top.gg/bot/880766859534794764/vote)', inline=False)
      await ctx.respond(embed=em, ephemeral=True)
      
def setup(client):
    client.add_cog(settings(client))
