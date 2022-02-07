from discord.commands import slash_command, permissions
from discord.ext import commands
from discord.ui import Button, View
import discord
import datetime
import os

import pymongo
from main import read_config
import topgg

MongoClient = pymongo.MongoClient(read_config['mongodb'])
db = MongoClient.db
settings_db = db["settings"]
blocked_db = db["blocked"]
ratelimit_db = db["cooldown"]
stats_db = db["stats"]

class bump(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.top = topgg.DBLClient(read_config["top"], autopost=True).set_data(client)
    
    def get_ratelimit(self, guild):
        rate = ratelimit_db.find_one({"guild_id": guild.id}, {"_id": 0, "cooldown": 1})
        
        if rate is None:
          ago = datetime.datetime.now() - datetime.timedelta(minutes=30)
          data = {"guild_id": guild.id, "cooldown": ago}
          ratelimit_db.insert_one(data)
          return 0
          
        now = datetime.datetime.now()
        then = rate["cooldown"]
        while now <= then:    
          left = then - now
          return left.total_seconds()
        else:
          return 0

    @slash_command(description="Command to bumps your server")
    async def bump(self, ctx):
      blocked = blocked_db.find_one({"guild_id": ctx.guild.id}, {"_id": 0, "blocked": 1})
      if blocked is None:
        pass
      elif blocked["blocked"] is True:
        em = discord.Embed(title='Your server has been blocked', color=discord.Color.blue())
        await ctx.respond(embed=em)
        return

      db = settings_db.find_one({"guild_id": ctx.guild.id}, {"_id": 0})
      if db is None:
        data = {"guild_id": ctx.guild.id, "status": "OFF", "bump_channel": None, "invite_channel": None, "description": None}
        settings_db.insert_one(data)
        db = settings_db.find_one({"guild_id": ctx.guild.id}, {"_id": 0})
        
      if not db["status"] == "ON":
        em = discord.Embed(title='Command has been disabled', color=discord.Color.blue())
        em.set_footer(text='Use /settings to turn it on again')
        await ctx.respond(embed=em)
        return
      
      if db["description"] is None:
        em = discord.Embed(title='No server description found\n/settings to add one', color=discord.Color.blue())
        em.set_footer(text='/support')
        await ctx.respond(embed=em)
        return

      if db["bump_channel"] is None:
        em = discord.Embed(title='No bump channel found\n/settings to add one', color=discord.Color.blue())
        em.set_footer(text='/support')
        await ctx.respond(embed=em)
        return
      
      self.top.default_bot_id = self.client.user.id
      vote = await self.top.get_user_vote(ctx.author.id)

      ratelimit = self.get_ratelimit(ctx.guild)
      if not ratelimit is None:
        minutes = ratelimit // 60

        if vote is True:
          minutes = minutes - 10

        if not minutes < 0:
          em = discord.Embed(title=f"Server on cooldown",description=f"You can bump again in {minutes} minutes.", color=discord.Color.red())
          em.add_field(name='Note', value='Please [vote](https://top.gg/bot/880766859534794764/vote) for us so we can grow!')
          em.set_footer(text=read_config["footer"], icon_url=ctx.guild.icon.url)
          await ctx.respond(embed=em)
          return
        
        else: 
          then = datetime.datetime.now() + datetime.timedelta(minutes=30)
          data = {"$set":{"cooldown": then}}
          ratelimit_db.update_one({"guild_id": ctx.guild.id}, data)
          

      em = discord.Embed(title='Bumping!', description='Your server is beening bumped', color=discord.Color.blue())
      em.add_field(name='Note', value='Please [vote](https://top.gg/bot/880766859534794764/vote) for us so we can grow!')
      em.set_footer(text=read_config["footer"], icon_url=ctx.guild.icon.url)
      await ctx.respond(embed=em)
      

      invite_channel = self.client.get_channel(db["invite_channel"])
      if not invite_channel:
        invite_channel = ctx.guild.text_channels[0]
      
      invite = await invite_channel.create_invite(unique=False, max_age = 0, max_uses = 0, temporary=False)
      
      channel_ids = settings_db.find({}, {"_id": 0, "status": 1, "bump_channel": 1})
      
      for item in channel_ids:
        if not item["bump_channel"] is None:
          channel = self.client.get_channel(item["bump_channel"])
          if not channel is None:

            status = item["status"]
            if status == "ON":
            
              description = db["description"]
              if description is None:
                em = discord.Embed(title='Server Description Is None', color=discord.Color.blue())
                em.set_footer(text='Use /settings and add an Server Description')
                await ctx.send(embed=em)
                return

              bump_em = discord.Embed(color=discord.Colour.blue())
              bump_em.add_field(name='**Description**', value=description, inline=False)
              bump_em.add_field(name='**Members**', value=str(len(ctx.guild.members)), inline=True)
              bump_em.add_field(name="**Channels**", value=str(len(ctx.guild.channels)), inline=True)
              bump_em.add_field(name="**Emojis**", value=str(len(ctx.guild.emojis)), inline=True)
              bump_em.add_field(name="**Boosts**", value=ctx.guild.premium_subscription_count, inline=True)
              bump_em.set_author(name=f"{ctx.guild.name} ({ctx.guild.id})", icon_url=ctx.guild.icon.url)
              bump_em.set_footer(text=read_config["footer"], icon_url=ctx.guild.icon.url)
              
              button = Button(label="Join Server", style=discord.ButtonStyle.url, url=f"{invite}")
              view = View()
              view.add_item(button)

              try:
                await channel.send(embed=bump_em, view=view)
              except Exception:
                pass
          
          
      em = discord.Embed(title='Bumped!', description='Your server has been bumped', color=discord.Color.green())
      em.add_field(name='Note', value='Please [vote](https://top.gg/bot/880766859534794764/vote) for us so we can grow!')
      em.set_footer(text=read_config["footer"], icon_url=ctx.guild.icon.url)
      await ctx.send(embed=em)
      
      stats = stats_db.find_one({}, {"_id": 1, "bumps": 1})
      if stats is None:
        data = {"bumps": 0}
        stats_db.insert_one(data)
        stats = stats_db.find_one({}, {"_id": 1, "bumps": 1})
        
      amount = stats["bumps"]     
      amount = amount + 1 
      
      data = {"$set":{f"bumps": amount}}
      stats_db.update_one({"_id": stats["_id"]}, data)
      
def setup(client):
    client.add_cog(bump(client))