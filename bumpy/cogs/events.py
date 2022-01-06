import discord
from discord.ext import commands, tasks
import asyncio

from main import read_config

class events(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.status.start()
        
    @tasks.loop()
    async def status(self):
      for status in read_config["status"]:
        await self.client.change_presence(activity=discord.Game(name=(status)))
        await asyncio.sleep(8)
        
        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.client.guilds)} Servers"))
        await asyncio.sleep(8)

        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.client.users)} Users"))
        await asyncio.sleep(8)

    @status.before_loop
    async def before_status(self):
        await self.client.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
      print(self.client.user.name, f"is online")
      print(f"{len(self.client.guilds)} Servers")
      await self.client.change_presence(status=discord.Status.online)
      
    @commands.Cog.listener()
    async def on_message(self, message):
      if message.content == ".bump":
        await message.channel.send("Bumpy has been moved to slash commmands if you can use them in the server your in try to reinvite the bot using this link https://dsc.gg/bumpy")
      
def setup(client):
    client.add_cog(events(client))