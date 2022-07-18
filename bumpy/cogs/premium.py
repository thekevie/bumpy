from discord.ext import commands
from discord import app_commands
import discord
import datetime

from utils.functions import *

class premium(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @app_commands.command(name="premium", description="Buy Bumpy premium for a guild/user")
    async def premium(self, interaction):
        add_command_stats("buy_premium")
        em = discord.Embed(title="Buy Bumpy Premium", color=discord.Color.blue())
        em.description = f"Premium is currently not avalible. The only current way to get permium is to win it in the [support server](https://discord.gg/KcH28tRtBu)"
        await interaction.response.send_message(embed=em)
        
    @commands.group("premium")
    @commands.is_owner()
    async def admin_premium(self, ctx):
        pass
            
    @admin_premium.command(name="add", description="Add Bumpy premium to a guild/user")
    @commands.is_owner()
    async def premium_add(self, ctx, type=None, id=None, *, time=None):
        await ctx.message.delete()
        if id is None:
            await ctx.send("ID was not found")
            return
        if not type in ["guild", "user"] or type is None:
            await ctx.send("Type is not valid\n[guild/user]")
            return
        id = int(id)
        add_command_stats("premium_add")
        
        try:
            time_list = time.split(" ")            
        except Exception as e:
            time_list = [time]
            
            
        if not time is None:
            total = 0
            for x in time_list:
                x = x.lower()
                if x.endswith("m"):
                    x = x.replace('m', '')
                    total = int(x)*30 + total
                elif x.endswith("w"):
                    x = x.replace('w', '')
                    total = int(x)*7 + total
                elif x.endswith("d"):
                    x = x.replace('d', '')
                    total = int(x) + total
        else:
            total=False
               
        if type == "user":   
            settings = check_user(id, "premium")
            expires = get_date(settings, total)
            db.settings.update_one({"user_id": id}, {"$set":{"premium": {"status": True, "expires": expires}}})
            if not expires is False:
                expires = round(datetime.datetime.timestamp(expires))
                expires = f"<t:{expires}:D>"
            await ctx.send(f"User: `{id}` now has *premium* that expires on {expires}")
            
        elif type == "guild":
            settings = check_guild(id, "premium")
            expires = get_date(settings, total)   
            db.settings.update_one({"guild_id": id}, {"$set":{"premium": {"status": True, "expires": expires}}})
            if not expires is False:
                expires = round(datetime.datetime.timestamp(expires))
                expires = f"<t:{expires}:D>"
            await ctx.send(f"Guild: `{id}` now has *premium* that expires on {expires}")
    
    @admin_premium.command(name="set", description="Set Bumpy premium for a guild/user")
    @commands.is_owner()
    async def premium_set(self, ctx, type=None, id=None, expires=None):
        await ctx.message.delete()
        if id is None:
            await ctx.send("ID was not found")
            return
        if not type in ["guild", "user"] or type is None:
            await ctx.send("Type is not valid\n[guild/user]")
            return
        id = int(id)
        add_command_stats("premium_set")
        
        if expires is None or expires == "False":
            expires = False
        else:
            expires = datetime.datetime.strptime(expires, "%Y-%m-%d")
            if datetime.datetime.utcnow() > expires:
                return await ctx.send("This time has already been")
            
        if type == "user":   
            check_user(id, "premium")                    
            db.settings.update_one({"user_id": id}, {"$set":{"premium": {"status": True, "expires": expires}}})
            if not expires is False:
                expires = round(datetime.datetime.timestamp(expires))
                expires = f"<t:{expires}:D>"
            await ctx.send(f"User: `{id}` now has *premium* that expires on {expires}")
            
        elif type == "guild":   
            check_guild(id, "premium")                    
            db.settings.update_one({"guild_id": id}, {"$set":{"premium": {"status": True, "expires": expires}}})
            if not expires is False:
                expires = round(datetime.datetime.timestamp(expires))
                expires = f"<t:{expires}:D>"
            await ctx.send(f"Guild: `{id}` now has *premium* that expires on {expires}")
        
    @admin_premium.command(name="remove", description="Remove Bumpy premium from a guild/user")
    @commands.is_owner()
    async def premium_remove(self, ctx, type=None, id=None):
        await ctx.message.delete()
        if id is None:
            await ctx.send("ID was not found")
            return
        if not type in ["guild", "user"] or type is None:
            await ctx.send("Type is not valid\n[guild/user]")
            return
        add_command_stats("premium_remove")
        id = int(id)
        if type == "user":
            if not db.settings.find_one({"user_id": id, "premium.status": True}):
                return await ctx.send(f"User: `{id}` do not have *premium*")
            db.settings.update_one({"user_id": id}, {"$unset":{"premium": ""}})
            await ctx.send(f"User: `{id}` no longer has *premium*")
        elif type == "guild":
            if not db.settings.find_one({"guild_id": id, "premium.status": True}):
                return await ctx.send(f"Guild: `{id}` do not have *premium*")
            db.settings.update_one({"guild_id": id}, {"$unset":{"premium": ""}})
            await ctx.send(f"Guild: `{id}` no longer has *premium*")
        
async def setup(client):
    await client.add_cog(premium(client))