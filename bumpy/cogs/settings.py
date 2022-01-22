from discord.commands import slash_command, permissions
from discord.ext import commands
from discord.ui import Button, View
import discord
import asyncio
import os

import pymongo

from main import read_config

MongoClient = pymongo.MongoClient(read_config['mongodb'])
db = MongoClient.settings
s = db["servers"]

class menu(discord.ui.View):
    def __init__(self, ctx, client):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.client = client
        self.bump = None
        self.invite = None
        self.descriotion = None
    
    @discord.ui.button(label="Enabled",style=discord.ButtonStyle.green, custom_id="enabled", row=0)
    async def on_button_callback(self, button, interaction):      
        data = {"$set":{"on_off": "ON"}}
        s.update_one({"guild_id": self.ctx.guild.id}, data)  

        db = s.find_one({"guild_id": self.ctx.guild.id}, {"_id": 0})
        if db['channel_id'] is None:
          bump_channel = None
        else:
          bump_channel = self.client.get_channel(db['channel_id']).mention

        if db['invite_channel'] is None:
          invite_channel = None
        else:
          invite_channel = self.client.get_channel(db['invite_channel']).mention
        
        em = discord.Embed(title="Bumpy Settings", description="Here you can change all settings for the bump command.", color=discord.Colour.blue())
        em.add_field(name="Status", value="ON", inline=True)
        em.add_field(name="Bump Channel", value=bump_channel, inline=True)
        em.add_field(name="Invite Channel", value=invite_channel, inline=True)
        em.add_field(name="Description", value=db['ad'], inline=False)
      
        await interaction.response.edit_message(embed=em, view=self)
        await self.ctx.respond(f"**Bumpy was Enabled**", ephemeral=True)

    @discord.ui.button(label="Disabled",style=discord.ButtonStyle.red, custom_id="disabled", row=0)
    async def off_button_callback(self, button, interaction):
        data = {"$set":{"on_off": "OFF"}}
        s.update_one({"guild_id": self.ctx.guild.id}, data)

        db = s.find_one({"guild_id": self.ctx.guild.id}, {"_id": 0})
        if db['channel_id'] is None:
          bump_channel = "None"
        else:
          bump_channel = self.client.get_channel(db['channel_id']).mention

        if db['invite_channel'] is None:
          invite_channel = None
        else:
          invite_channel = self.client.get_channel(db['invite_channel']).mention
        
        em = discord.Embed(title="Bumpy Settings", description="Here you can change all settings for the bump command.", color=discord.Colour.blue())
        em.add_field(name="Status", value="OFF", inline=True)
        em.add_field(name="Bump Channel", value=bump_channel, inline=True)
        em.add_field(name="Invite Channel", value=invite_channel, inline=True)
        em.add_field(name="Description", value=db['ad'], inline=False)
        
        await interaction.response.edit_message(embed=em, view=self)
        await self.ctx.respond(f"**Bumpy was Disabled**", ephemeral=True)
        

    @discord.ui.button(label="Bump Channel", style=discord.ButtonStyle.blurple, custom_id="bump_channel", row=1)  
    async def bump_channel_button_callback(self, button, interaction):
        button.disabled = True
        await interaction.response.edit_message(view=self)
        
        i = await self.ctx.respond("**Mention the channel you want the bumps to be sent in!**", ephemeral=True)
        
        def check(msg):
          return msg.author == self.ctx.author and msg.channel == self.ctx.channel
        
        try:
          answer = await self.client.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
          await i.delete()
          return
        await answer.delete()
        channel_id = answer.channel_mentions[0].id
        
        data = {"$set":{f"channel_id": channel_id}}
        self.bump = data
      
        await i.edit(f"**Bump Channel was set to <#{channel_id}>**")
        
    @discord.ui.button(label="Invite Channel", style=discord.ButtonStyle.blurple, custom_id="invite_channel", row=1)  
    async def invite_channel_button_callback(self, button, interaction):
        button.disabled = True
        await interaction.response.edit_message(view=self)
        
        i = await self.ctx.respond("**Mention the channel you want the invite to be created in!**", ephemeral=True)
        
        def check(msg):
          return msg.author == self.ctx.author and msg.channel == self.ctx.channel
        
        try:
          answer = await self.client.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
          await i.delete()
          return
        await answer.delete()
        channel_id = answer.channel_mentions[0].id
        
        data = {"$set":{f"invite_channel": channel_id}}
        self.invite = data
      
        await i.edit(f"**Invite Channel was set to <#{channel_id}>**")
        
    @discord.ui.button(label="Description", style=discord.ButtonStyle.blurple, custom_id="set_description", row=1)  
    async def descriotion_button_callback(self, button, interaction):
        button.disabled = True
        await interaction.response.edit_message(view=self)
        
        i = await self.ctx.respond("**Send your server description in the channel below!**", ephemeral=True)
        
        def check(msg):
          return msg.author == self.ctx.author and msg.channel == self.ctx.channel
        
        try:
          answer = await self.client.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
          await i.delete()
          return
        await answer.delete()
        ad = answer.content
        
        data = {"$set":{f"ad": ad}}
        self.descriotion = data
        
        await i.edit(f"**Server Description Was Changed**")
        
        
    @discord.ui.button(label="Save", style=discord.ButtonStyle.gray, custom_id="update", row=2)  
    async def update_button_callback(self, button, interaction):
      if self.bump is not None:
        s.update_one({"guild_id": self.ctx.guild.id}, self.bump)
        
      if self.invite is not None:
        s.update_one({"guild_id": self.ctx.guild.id}, self.invite)
      
      if self.descriotion is not None:
        s.update_one({"guild_id": self.ctx.guild.id}, self.descriotion)

      db = s.find_one({"guild_id": self.ctx.guild.id}, {"_id": 0})

      if db['channel_id'] is None:
        bump_channel = "None"
      else:
        bump_channel = self.client.get_channel(db['channel_id']).mention

      if db['invite_channel'] is None:
        invite_channel = None
      else:
        invite_channel = self.client.get_channel(db['invite_channel']).mention
      
      em = discord.Embed(title="Bumpy Settings", description="Here you can change all settings for the bump command.", color=discord.Colour.blue())
      em.add_field(name="Status", value=db['on_off'], inline=True)
      em.add_field(name="Bump Channel", value=bump_channel, inline=True)
      em.add_field(name="Invite Channel", value=invite_channel, inline=True)
      em.add_field(name="Description", value=db['ad'], inline=False)
      button.disabled = True
      await interaction.response.edit_message(embed=em, view=self)
      await self.ctx.respond("**Saved Changes**", ephemeral=True)
      
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray, custom_id="cancel", row=2)  
    async def cancel_button_callback(self, button, interaction):   
      button.disabled = True  
      await interaction.respons.edit_message(view=self)
      await self.ctx.respond("**Cancelled Changes**")

    async def on_error(self, error, item, interaction):
        await self.ctx.respond(f"{str(error)}", ephemeral=True)

class settings(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @slash_command(description="A command to change the settings")
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx: discord.ApplicationContext):
      r = s.find_one({"guild_id": ctx.guild.id})
      if r is None:
        data = {"guild_id": ctx.guild.id, "ad": None, "channel_id": None, "invite_channel": None, "on_off": "OFF"}
        s.insert_one(data)
        
      client = self.client
      view = menu(ctx, client)
      
      db = s.find_one({"guild_id": ctx.guild.id}, {"_id": 0})

      if db['channel_id'] is None:
        bump_channel = "None"
      else:
        bump_channel = self.client.get_channel(db['channel_id']).mention

      if db['invite_channel'] is None:
        invite_channel = None
      else:
        invite_channel = self.client.get_channel(db['invite_channel']).mention

        
      em = discord.Embed(title="Bumpy Settings", description="Here you can change all settings for the bump command.", color=discord.Colour.blue())
      em.add_field(name="Status", value=db['on_off'], inline=True)
      em.add_field(name="Bump Channel", value=bump_channel, inline=True)
      em.add_field(name="Invite Channel", value=invite_channel, inline=True)
      em.add_field(name="Description", value=db['ad'], inline=False)
     
      await ctx.respond(embed=em, view=view, ephemeral=True)

    @slash_command(description="Get help with the bot")
    async def help(self, ctx: discord.ApplicationContext):
      em = discord.Embed(description = "If you need help join the support server and contact us", colour=discord.Colour.blue())
      em.add_field(name='**Links**', value=f'**[Invite Me](https://discord.com/api/oauth2/authorize?client_id=880766859534794764&permissions=137976212545&scope=bot%20applications.commands) | [Support Server](https://discord.gg/KcH28tRtBu)**')
      await ctx.respond(embed=em, ephemeral=True)

    @slash_command(description="The bots support server")
    async def support(self, ctx):
      em = discord.Embed(colour=discord.Colour.blue())
      em.add_field(name='**Links**', value=f'**[Invite Me](https://discord.com/api/oauth2/authorize?client_id=880766859534794764&permissions=137976212545&scope=bot%20applications.commands) | [Support Server](https://discord.gg/KcH28tRtBu)**')
      await ctx.respond(embed=em, ephemeral=True)

    @slash_command(description="The bots invite link")
    async def invite(self, ctx):
      em = discord.Embed(colour=discord.Colour.blue())
      em.add_field(name='**Links**', value=f'**[Invite Me](https://discord.com/api/oauth2/authorize?client_id=880766859534794764&permissions=137976212545&scope=bot%20applications.commands) | [Support Server](https://discord.gg/KcH28tRtBu)**')
      await ctx.respond(embed=em, ephemeral=True)

    @slash_command(description="A list of all parters")
    async def partners(self, ctx):
      value = ""

      for i in read_config["partner"]:

        guild = self.client.get_guild(i)
        invite = await guild.text_channels[0].create_invite(unique=False, max_age = 0, max_uses = 0, temporary=False)
        if ctx.author in guild.members:
          io = "**(Joined)**"
        else:
          io = "**(Not Joined)**"

        value += f'**[{guild.name}]({invite})** {io}\n'

      em = discord.Embed(title='Partners', description=value, color=discord.Color.blue())
      await ctx.respond(embed=em, ephemeral=True)

    @slash_command(description="Some info about the bot")
    async def info(self, ctx):
      em = discord.Embed(colour=discord.Colour.blue())
      em.add_field(name='**Links**', value=f'**[Invite Me](https://discord.com/api/oauth2/authorize?client_id=880766859534794764&permissions=137976212545&scope=bot%20applications.commands) | [Support Server](https://discord.gg/KcH28tRtBu)**')
      await ctx.respond(embed=em, ephemeral=True)

    @slash_command(description="Vote for the bot to get perks")
    async def vote(self, ctx):
      em = discord.Embed(colour=discord.Colour.green())
      em.add_field(name='**TOP.GG**', value='[Vote Here](https://top.gg/bot/880766859534794764/vote)', inline=False)
      await ctx.respond(embed=em, ephemeral=True)
      
def setup(client):
    client.add_cog(settings(client))