import discord
from discord.ext import commands
import datetime
import asyncio
import json
import os

from dotenv import load_dotenv
load_dotenv()

def read_config():
    with open("config.json") as file:
        return json.load(file)

intents = discord.Intents.default()
intents.message_content = True
#intents.members = True

class Bumpy(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix = commands.when_mentioned_or("b!", "!b", "B!", "!B"),
            owner_ids = read_config()["owners"],
            intents = intents,
            shard_count=2,
            case_insensitive=True,
            strip_after_prefix=True,
            status=discord.Status.online,
            activity = discord.Game(name="/bump")
        )
        self.color = discord.Color.blurple()
        self.success = discord.Color.green()
        self.fail = discord.Color.red()
        self.config = read_config()
        asyncio.run(self.load_cogs())

    async def load_cogs(self):
        for file in [file for file in os.listdir(f"cogs") if file.endswith(".py")]:
            await self.load_extension(f"cogs.{file[:-3]}")    
        return

print(os.getenv("token"))
client = Bumpy()
client.run(os.getenv("token"))