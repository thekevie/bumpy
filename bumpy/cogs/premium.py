from diskord.ext import commands
import diskord
import datetime

from utils.functions import *

class premium(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @diskord.application.slash_command(name="buy")
    async def buy(self, ctx):
        pass
        
    @buy.sub_command(name="premium", description="Buy Bumpy premium for a guild/user")
    async def buy_premium_(self, ctx):
        add_command_stats("buy_premium")
        em = diskord.Embed(title="Buy Bumpy Premium", color=diskord.Color.blue())
        em.description = f"If you want to buy Bumpy Premium join the [support server](https://discord.gg/KcH28tRtBu) and message `kevie#9091` to pay with paypal"
        await ctx.respond(embed=em)
        
    @diskord.application.slash_command(name="premium", guild_ids=[832743824181952534])
    @commands.is_owner()
    async def premium(self, ctx):
        pass
            
    @premium.sub_command(name="add", description="Add Bumpy premium to a guild/user")
    @commands.is_owner()
    @diskord.application.option("id")
    @diskord.application.option("type", choices=[
        diskord.OptionChoice(name="User", value="user"),
        diskord.OptionChoice(name="Guild", value="guild"),
    ])
    @diskord.application.option("months", required=False)
    @diskord.application.option("weeks", required=False)
    @diskord.application.option("days", required=False)
    async def premium_add(self, ctx, id, type, months=None, weeks=None, days=None):
        id = int(id)
        add_command_stats("premium_add")
        
        total = 0
        if not months is None:
            total = total + int(months)*30
        if not weeks is None:
            total = total + int(weeks)*7
        if not days is None:
            total = total + int(days)
        if not total:
            total = False
        
        if type == "user":   
            settings = check_user(id, "premium")
            expires = get_date(settings, total)
            db.settings.update_one({"user_id": id}, {"$set":{"premium.status": True, "premium.expires": expires}})
            if not expires is False:
                expires = round(datetime.datetime.timestamp(expires))
                expires = f"<t:{expires}:D>"
            await ctx.respond(f"User: `{id}` now has premium that expires on {expires}")
            
        elif type == "guild":
            settings = check_guild(id, "premium")
            expires = get_date(settings, total)   
            db.settings.update_one({"guild_id": id}, {"$set":{"premium.status": True, "premium.expires": expires}})
            if not expires is False:
                expires = round(datetime.datetime.timestamp(expires))
                expires = f"<t:{expires}:D>"
            await ctx.respond(f"Guild: `{id}` now has premium that expires on {expires}")
    
    @premium.sub_command(name="set", description="Set Bumpy premium for a guild/user")
    @commands.is_owner()
    @diskord.application.option("id")
    @diskord.application.option("type", choices=[
        diskord.OptionChoice(name="User", value="user"),
        diskord.OptionChoice(name="Guild", value="guild"),
    ])
    @diskord.application.option("expires", required=False)
    async def premium_set(self, ctx, id, type, expires=None):
        id = int(id)
        add_command_stats("premium_set")
        
        if expires is None or expires == "False":
            expires = False
        else:
            expires = datetime.datetime.strptime(expires, "%Y-%m-%d")
            if datetime.datetime.utcnow() > expires:
                return await ctx.respond("This time has already been")
            
        if type == "user":   
            check_user(id, "premium")                    
            db.settings.update_one({"user_id": id}, {"$set":{"premium.status": True, "premium.expires": expires}})
            if not expires is False:
                expires = round(datetime.datetime.timestamp(expires))
                expires = f"<t:{expires}:D>"
            await ctx.respond(f"User: `{id}` now has premium that expires on {expires}")
            
        elif type == "guild":   
            check_guild(id, "premium")                    
            db.settings.update_one({"guild_id": id}, {"$set":{"premium.status": True, "premium.expires": expires}})
            if not expires is False:
                expires = round(datetime.datetime.timestamp(expires))
                expires = f"<t:{expires}:D>"
            await ctx.respond(f"Guild: `{id}` now has premium that expires on {expires}")
        
    @premium.sub_command(name="remove", description="Remove Bumpy premium from a guild/user")
    @commands.is_owner()
    @diskord.application.option("id")
    @diskord.application.option("type", choices=[
        diskord.OptionChoice(name="User", value="user"),
        diskord.OptionChoice(name="Guild", value="guild"),
    ])
    async def premium_remove(self, ctx, id, type):
        add_command_stats("premium_remove")
        id = int(id)
        if type == "user":
            if not db.settings.find_one({"user_id": id, "premium.status": True}):
                return await ctx.respond(f"User: `{id}` do not have *premium*")
            db.settings.update_one({"user_id": id}, {"$set":{"premium.status": False, "premium.expires": None}})
            await ctx.respond(f"User: `{id}` no longer has *premium*")
        elif type == "guild":
            if not db.settings.find_one({"guild_id": id, "premium.status": True}):
                return await ctx.respond(f"Guild: `{id}` do not have *premium*")
            db.settings.update_one({"guild_id": id}, {"$set":{"premium.status": False, "premium.expires": None}})
            await ctx.respond(f"Guild: `{id}` no longer has *premium*")
        
def setup(client):
    client.add_cog(premium(client))