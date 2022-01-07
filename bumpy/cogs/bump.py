from discord.commands import slash_command, permissions
from discord.ext import commands
from discord.ui import Button, View
import discord
import datetime
import os

import pymongo
from main import read_config

MongoClient = pymongo.MongoClient(read_config['mongodb'])
sett = MongoClient.settings
servers_db = sett["servers"]
cooldown = MongoClient.cooldown
bump_db = cooldown["bump"]

class bump(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    def get_ratelimit(self, user: discord.User):
        user_db = bump_db.find_one({"user_id": user.id}, {"_id": 0, "cooldown": 1})
        
        if user_db is None:
          ago = datetime.datetime.now() - datetime.timedelta(minutes=30)
          data = {"user_id": user.id, "cooldown": ago}
          bump_db.insert_one(data)
          return 0
          
        now = datetime.datetime.now()
        then = user_db["cooldown"]
        while now <= then:    
          left = then - now
          return left.total_seconds()
        else:
          return 0

    @slash_command(description="Command to bumps your server")
    async def bump(self, ctx):

      db = servers_db.find_one({"guild_id": ctx.guild.id}, {"_id": 0})
      if db is None:
        data = {"guild_id": ctx.guild.id, "ad": None, "channel_id": None, "invite_channel": None, "on_off": "OFF"}
        servers_db.insert_one(data)
        db = servers_db.find_one({"guild_id": ctx.guild.id}, {"_id": 0})
        
      if not db["on_off"] == "ON":
        em = discord.Embed(title='Command has been disabled', color=discord.Color.blue())
        em.set_footer(text='Use /settings to turn it on again')
        await ctx.respond(embed=em)
        return
      
      if db["ad"] is None:
        em = discord.Embed(title='No server description found\nUse /settings and add one', color=discord.Color.blue())
        em.set_footer(text='/support')
        await ctx.respond(embed=em)
        return

      if db["channel_id"] is None:
        em = discord.Embed(title='No bump channel found\nUse /settings and add one', color=discord.Color.blue())
        em.set_footer(text='/support')
        await ctx.respond(embed=em)
        return
      
      #dbl = dbl.DBLClient(self.client, os.environ["top"], autopost = True, autopost_interval=900)
      #vote = await dbl.get_user_vote(ctx.author.id)
      vote = True

      ratelimit = self.get_ratelimit(ctx.user)
      if not ratelimit is None:
        minutes = ratelimit // 60

        if vote is True:
          minutes = minutes - 10
          
        #for partner in read_config["partner"]:
          #server = self.client.get_guild(partner)
          #if ctx.author in server.members:
            #minutes = minutes - 1

        if not minutes < 0:
          em = discord.Embed(title=f"Server on cooldown",description=f"You can bump again in {minutes} minutes.", color=discord.Color.red())
          em.add_field(name='Tip', value='For [voters](https://top.gg/bot/880766859534794764/vote) cooldown is 20 minutes')
          em.set_footer(text=read_config["footer"], icon_url=ctx.guild.icon.url)
          await ctx.respond(embed=em)
          return
        
        else: 
          then = datetime.datetime.now() + datetime.timedelta(minutes=30)
          data = {"$set":{"cooldown": then}}
          bump_db.update_one({"user_id": ctx.user.id}, data)
          

      em = discord.Embed(title='Bumping!', description='Your server is beening bumped', color=discord.Color.blue())
      em.add_field(name='Tip', value='For [voters](https://top.gg/bot/880766859534794764/vote) cooldown is 20 minutes')
      em.set_footer(text=read_config["footer"], icon_url=ctx.guild.icon.url)
      await ctx.respond(embed=em)
      

      invite_channel = self.client.get_channel(db["invite_channel"])
      if not invite_channel:
        invite_channel = ctx.guild.text_channels[0]
      
      invite = await invite_channel.create_invite(unique=False, max_age = 0, max_uses = 0, temporary=False)
      
      channel_ids = servers_db.find({}, {"_id": 0, "channel_id": 1, "on_off": 1})
      
      for item in channel_ids:
        print(item["channel_id"])
        if not item["channel_id"] is None:
          channel = self.client.get_channel(item["channel_id"])
          if not channel is None:

            on_off = item["on_off"]
            if on_off == "ON":
            
              ad = db["ad"]
              if ad is None:
                em = discord.Embed(title='Server Description Is None', color=discord.Color.blue())
                em.set_footer(text='Use /settings and add an Server Description')
                await ctx.send(embed=em)
                return

              bump_em = discord.Embed(color=discord.Colour.blue())
              bump_em.add_field(name='**Invite**', value=invite, inline=True)
              bump_em.add_field(name='**Members**', value=str(len(ctx.guild.members)), inline=True)
              bump_em.add_field(name='**Description**', value=ad, inline=False)
              bump_em.add_field(name='**Region**', value=ctx.guild.region, inline=True)
              bump_em.add_field(name='**Server ID**', value=ctx.guild.id, inline=True)
              bump_em.add_field(name="**Emojis**", value=str(len(ctx.guild.emojis)), inline=True)
              bump_em.add_field(name="**Boosts**", value=ctx.guild.premium_subscription_count, inline=True)
              bump_em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
              bump_em.set_footer(text=read_config["footer"], icon_url=ctx.guild.icon.url)

              try:
                await channel.send(embed=bump_em)
              except Exception:
                pass
          
          
      em = discord.Embed(title='Bumped!', description='Your server has been bumped', color=discord.Color.green())
      em.add_field(name='Tip', value='For [voters](https://top.gg/bot/880766859534794764/vote) cooldown is 20 minutes')
      em.set_footer(text=read_config["footer"], icon_url=ctx.guild.icon.url)
      await ctx.send(embed=em)
      
def setup(client):
    client.add_cog(bump(client))