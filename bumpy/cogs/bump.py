from diskord.ext import commands
from diskord.ui import Button, View
import diskord
import datetime

from main import read_config, db, db_settings, db_blocked, db_ratelimit, db_stats, db_premium, db_codes

class bump(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    def get_ratelimit(self, guild):
        rate = db_ratelimit.find_one({"guild_id": guild.id}, {"_id": 0, "cooldown": 1})
        
        if rate is None:
          ago = datetime.datetime.now() - datetime.timedelta(minutes=40)
          data = {"guild_id": guild.id, "cooldown": ago}
          db_ratelimit.insert_one(data)
          return 0
          
        now = datetime.datetime.now()
        then = rate["cooldown"]
        while now <= then:    
          left = then - now
          return left.total_seconds()
        else:
          return 0

    @diskord.application.slash_command(description="Command to bumps your server")
    async def bump(self, ctx):
      blocked = db_blocked.find_one({"guild_id": ctx.guild.id}, {"_id": 0, "blocked": 1})
      if blocked is None:
        pass
      elif blocked["blocked"] is True:
        if not db_blocked.find_one({"guild_id": ctx.guild.id}, {"_id": 0, "reason": 1}):
          reason = "Not provided"
        else:
          reason = blocked["reason"]
        em = diskord.Embed(title='Your server has been blocked', description="If you want to appeal your ban join the [support server](https://discord.gg/KcH28tRtBu)", color=diskord.Color.blue())
        em.add_field(name="Reason", value=reason, inline=False)
        await ctx.respond(embed=em)
        return

      db = db_settings.find_one({"guild_id": ctx.guild.id}, {"_id": 0})
      if db is None:
        data = {"guild_id": ctx.guild.id, "status": "OFF", "bump_channel": None, "invite_channel": None, "description": None}
        db_settings.insert_one(data)
        db = db_settings.find_one({"guild_id": ctx.guild.id}, {"_id": 0})
        
      if not db["status"] == "ON":
        em = diskord.Embed(title='Command has been disabled', color=diskord.Color.blue())
        em.set_footer(text='Use /settings to turn it on again')
        await ctx.respond(embed=em)
        return
      
      if db["description"] is None:
        em = diskord.Embed(title='No server description found\n/settings to add one', color=diskord.Color.blue())
        em.set_footer(text='/support')
        await ctx.respond(embed=em)
        return

      if db["bump_channel"] is None:
        em = diskord.Embed(title='No bump channel found\n/settings to add one', color=diskord.Color.blue())
        em.set_footer(text='/support')
        await ctx.respond(embed=em)
        return
      
      vote = None
      top = None
      dbl = None
      
      guild = self.client.get_guild(832743824181952534)
      channel = guild.get_channel(951095386959929355)
      guild = None
      date = datetime.datetime.now() - datetime.timedelta(hours=12)
      messages = channel.history(after=date) 
      async for message in messages:
        if message.mentions:
          user = message.mentions[0]
          if ctx.user == user:
            if "top.gg" in message.content:
              top = True
            if "dbl" in message.content:
              dbl = True
            vote = True
             
      ratelimit = self.get_ratelimit(ctx.guild)
      if not ratelimit is None:
        minutes = ratelimit // 60

        if vote is True:
          if top is True:
            minutes = minutes - 10
          if dbl is True:
            minutes = minutes - 10
          if minutes < 0:
            minutes = 0
          
        if not minutes == 0:
          minutes = round(minutes)
          em = diskord.Embed(title=f"Server on cooldown", description=f"You can bump again in {minutes} minutes.", color=diskord.Color.red())
          em.add_field(name='Note', value='If you vote on [top.gg](https://top.gg/bot/880766859534794764/vote) and [dbl](https://discordbotlist.com/bots/bumpy-5009/upvote) you get 20 minutes less cooldown')
          em.set_footer(text=read_config["footer"])
          await ctx.respond(embed=em)
          return
        
        else: 
          then = datetime.datetime.now() + datetime.timedelta(minutes=30)
          data = {"$set":{"cooldown": then}}
          db_ratelimit.update_one({"guild_id": ctx.guild.id}, data)

      em = diskord.Embed(title='Bumping!', description='Your server is beening bumped', color=diskord.Color.blue())
      em.add_field(name='Note', value='If you vote on [top.gg](https://top.gg/bot/880766859534794764/vote) and [dbl](https://discordbotlist.com/bots/bumpy-5009/upvote) you get 20 minutes less cooldown')
      em.set_footer(text=read_config["footer"])
      await ctx.respond(embed=em)
      

      invite_channel = self.client.get_channel(db["invite_channel"])
      if not invite_channel:
        invite_channel = ctx.guild.text_channels[0]
      
      invite = await invite_channel.create_invite(unique=False, max_age = 0, max_uses = 0, temporary=False)
      
      channel_ids = db_settings.find({}, {"_id": 0, "status": 1, "bump_channel": 1})
      
      for item in channel_ids:
        if not item["bump_channel"] is None:
          channel = self.client.get_channel(item["bump_channel"])
          if not channel is None:

            status = item["status"]
            if status == "ON":
            
              description = db["description"]
              if description is None:
                em = diskord.Embed(title='Server Description Is None', color=diskord.Color.blue())
                em.set_footer(text='Use /settings and add an Server Description')
                await ctx.send(embed=em)
                return

              bump_em = diskord.Embed(color=diskord.Colour.blue())
              bump_em.add_field(name='**Description**', value=description, inline=False)
              bump_em.add_field(name='**Members**', value=str(len(ctx.guild.members)), inline=True)
              bump_em.add_field(name="**Channels**", value=str(len(ctx.guild.channels)), inline=True)
              bump_em.add_field(name="**Emojis**", value=str(len(ctx.guild.emojis)), inline=True)
              
              try:  
                bump_em.set_author(name=f"{ctx.guild.name} ({ctx.guild.id})", icon_url=ctx.guild.icon.url)
              except:
                bump_em.set_author(name=f"{ctx.guild.name} ({ctx.guild.id})")
                
              try:
                bump_em.set_footer(text=read_config["footer"], icon_url=ctx.guild.icon.url)
              except:
                bump_em.set_footer(text=read_config["footer"])
              
              button = Button(label="Join Server", style=diskord.ButtonStyle.url, url=f"{invite}")
              view = View()
              view.add_item(button)

              try:
                await channel.send(embed=bump_em, view=view)
              except Exception:
                pass
          
          
      em = diskord.Embed(title='Bumped!', description='Your server has been bumped', color=diskord.Color.green())
      em.add_field(name='Note', value='If you vote on [top.gg](https://top.gg/bot/880766859534794764/vote) and [dbl](https://discordbotlist.com/bots/bumpy-5009/upvote) you get 20 minutes less cooldown')
      em.set_footer(text=read_config["footer"])
      await ctx.channel.send(embed=em)
      
      stats = db_stats.find_one({}, {"_id": 1, "bumps": 1})
      if stats is None:
        data = {"bumps": 0}
        db_stats.insert_one(data)
        stats = db_stats.find_one({}, {"_id": 1, "bumps": 1})
        
      amount = stats["bumps"]     
      amount = amount + 1 
      
      data = {"$set":{f"bumps": amount}}
      db_stats.update_one({"_id": stats["_id"]}, data)
      
def setup(client):
    client.add_cog(bump(client))
