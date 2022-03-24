from diskord.ext import commands
import diskord
import asyncio

from main import read_config, db, db_settings, db_blocked, db_ratelimit, db_stats, db_premium, db_codes

async def get_data(self, interaction):
  
  db = self.settings.find_one({"guild_id": interaction.guild.id}, {"_id": 0})
  
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
    
  em = diskord.Embed(title="Bumpy Settings", description="Here you can change all settings for the bump command.", color=diskord.Colour.blue())
  em.add_field(name="Status", value=db["status"], inline=True)
  em.add_field(name="Bump Channel", value=bump_channel, inline=True)
  em.add_field(name="Invite Channel", value=invite_channel, inline=True)
  em.add_field(name="Description", value=db["description"], inline=False)
  return em

class menu(diskord.ui.View):
    def __init__(self, client):
        self.client = client        
    
    @diskord.ui.button(label="Enabled",style=diskord.ButtonStyle.green, custom_id="enabled", row=0)
    async def on_button_callback(self, button, interaction):      
        data = {"$set":{"status": "ON"}}
        db_settings.update_one({"guild_id": interaction.guild.id}, data)  

        em = await get_data(self, interaction)
        view = menu(self.client)
        await interaction.response.edit_message(embed=em, view=view)

    @diskord.ui.button(label="Disabled",style=diskord.ButtonStyle.red, custom_id="disabled", row=0)
    async def off_button_callback(self, button, interaction):
        data = {"$set":{"status": "OFF"}}
        db_settings.update_one({"guild_id": interaction.guild.id}, data)

        em = await get_data(self, interaction)
        view = menu(self.client)
        await interaction.response.edit_message(embed=em, view=view)
        

    @diskord.ui.button(label="Bump Channel", style=diskord.ButtonStyle.blurple, custom_id="bump_channel", row=1)  
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
        db_settings.update_one({"guild_id": interaction.guild.id}, data)
      
        em = await get_data(self, interaction)
        view = menu(self.client)
        await interaction.followup.edit_message(message_id=message_id, content=None, embed=em, view=view)        
        
    @diskord.ui.button(label="Invite Channel", style=diskord.ButtonStyle.blurple, custom_id="invite_channel", row=1)  
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
        db_settings.update_one({"guild_id": interaction.guild.id}, data)
      
        em = await get_data(self, interaction)
        view = menu(self.client)
        await interaction.followup.edit_message(message_id=message_id, content=None, embed=em, view=view)  
        
    @diskord.ui.button(label="Description", style=diskord.ButtonStyle.blurple, custom_id="set_description", row=1)  
    async def description_button_callback(self, button, interaction):
        message_id = interaction.message.id        
        await interaction.response.edit_message(content="**Send your server description in the channel below!**", embed=None, view=None)
        
        def check(msg):
          return msg.author == interaction.user and msg.channel == interaction.channel
        
        try:
          answer = await self.client.wait_for("message", check=check, timeout=180)
        except asyncio.TimeoutError:
          await interaction.followup.edit_message(message_id=message_id, content="**Timeout**", embed=None, view=None)     
          return    
        await answer.delete()
        description = answer.content
        
        if len(description) > 1000:
          await interaction.followup.send_message(content="Your description has more than 1000 characters")
        else: 
          data = {"$set":{f"description": description}}
          db_settings.update_one({"guild_id": interaction.guild.id}, data)
        
        em = await get_data(self, interaction)
        view = menu(self.client)
        await interaction.followup.edit_message(message_id=message_id, content=None, embed=em, view=view)
      
    @diskord.ui.button(label="Exit", style=diskord.ButtonStyle.gray, row=2)  
    async def exit_button_callback(self, button, interaction):
      await interaction.response.edit_message(content="Settings Was Saved", embed=None, view=None)      

class settings(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @diskord.application.slash_command(description="A command to change the settings")
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx):
      r = db_settings.find_one({"guild_id": ctx.guild.id})
      if r is None:
        data = {"guild_id": ctx.guild.id, "status": "OFF", "bump_channel": None, "invite_channel": None, "description": None}
        db_settings.insert_one(data)
        
      em = await get_data(self, ctx)
      client = self.client
      view = menu(client)
      await ctx.respond(embed=em, view=view, ephemeral=True)
      
def setup(client):
    client.add_cog(settings(client))
