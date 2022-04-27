import diskord
import json
import pymongo
import datetime

def read_config():
    with open("config.json") as file:
        return json.load(file)

read_config = read_config()

MongoClient = pymongo.MongoClient(read_config['mongodb'])
db = MongoClient.db

def check_guild(guild_id, type):
    if not db.settings.find_one({"guild_id": guild_id}):
        db.settings.insert_one({"guild_id": guild_id}) 
        
    if type in ["all", "settings", "bump"]:            
        if not db.settings.find_one({"guild_id": guild_id}, {"_id": 0, "bump_channel": 1}):
            db.settings.update_one({"guild_id": guild_id}, {"$set":{"bump_channel": None}})
        
        if not db.settings.find_one({"guild_id": guild_id}, {"_id": 0, "invite_channel": 1}):
            db.settings.update_one({"guild_id": guild_id}, {"$set":{"invite_channel": None}})
        
        if not db.settings.find_one({"guild_id": guild_id}, {"_id": 0, "description": 1}):
            db.settings.update_one({"guild_id": guild_id}, {"$set":{"description": None}})
    
        if not db.settings.find_one({"guild_id": guild_id}, {"_id": 0, "cooldown": 1}):
            db.settings.update_one({"guild_id": guild_id}, {"$set":{"cooldown": None}})
            
    if type in ["all", "premium"]:
        if not db.settings.find_one({"guild_id": guild_id}, {"_id": 0, "premium": 1}):
            db.settings.update_one({"guild_id": guild_id}, {"$set":{"premium.status": False, "premium.expires": None}})
            
    if type in ["all", "block"]:
        if not db.settings.find_one({"guild_id": guild_id}, {"_id": 0, "banned": 1}):
            db.settings.update_one({"guild_id": guild_id}, {"$set":{"banned": False}})
        
    return db.settings.find_one({"guild_id": guild_id})

def check_user(user_id, type):
    if not db.settings.find_one({"user_id": user_id}):
        db.settings.insert_one({"user_id": user_id})
        
    if type in ["all", "premium"]:
        if not db.settings.find_one({"user_id": user_id}, {"_id": 0, "premium": 1}):
            db.settings.update_one({"user_id": user_id}, {"$set":{"premium": False}})
    if type in ["all", "block"]:
        if not db.settings.find_one({"user_id": user_id}, {"_id": 0, "banned": 1}):
            db.settings.update_one({"user_id": user_id}, {"$set":{"banned": False}})
                
    return db.settings.find_one({"user_id": user_id})

def get_date(settings, total):
    if settings["premium"]["status"] is True:
        expires = settings["premium"]["expires"]
        if expires is None:
            expires = datetime.datetime.utcnow()
    else:
        expires = datetime.datetime.utcnow()
        
    if total is False:
        return False
    
    total = int(total)       
    if not expires is False:
        expires = expires + datetime.timedelta(days=total)
    return expires

async def bump_check(ctx, client):
    settings = db.settings.find_one({"guild_id": ctx.guild.id})
    try:
        bump_channel = client.get_channel(settings["bump_channel"])
    except diskord.NotFound:
        return False, "That channel do not exist"

    try:
        await bump_channel.send("Checking for Bump Channel", delete_after=1)
    except diskord.Forbidden:
        return False, "I dont have Permission to use that channel"
    return True, None

def add_command_stats(command):
    if not db.stats.find_one({}, {"_id": 0, "bumps": 1, "commands": 1}):
        data = {"bumps": 0, "commands": 0}
        db.stats.insert_one(data)
    stats = db.stats.find_one({}, {"bumps": 1, "commands": 1})    
    data = {"$set":{"commands": stats["commands"] + 1}}
    db.stats.update_one({"_id": stats["_id"]}, data)
    if command == "bump":
        data = {"$set":{"bumps": stats["bumps"] + 1}}
        db.stats.update_one({"_id": stats["_id"]}, data)

def check_blocked(guild_id, user_id):
    if db.settings.find_one({"user_id": user_id, "banned":{"exists": True}}):
        user = db.settings.find_one({"user_id": user_id})
        if user["banned"]["status"] is True:
            if not user["banned"]["reason"] is None:
                reason = user["banned"]["reason"]
            else:
                reason = "Not Provided"
            return True, reason
    elif db.settings.find_one({"guild_id": guild_id, "banned":{"exists": True}}):   
        guild = db.settings.find_one({"guild_id": guild_id})
        if guild["banned"]["status"] is True:
            if not guild["banned"]["reason"] is None:
                reason = guild["banned"]["reason"]
            else:
                reason = "Not Provided"
            return True, reason     
    return False, None

def check_for_server(ctx):
    settings = db.settings.find_one({"guild_id": ctx.guild.id})
    
    if settings["bump_channel"] is None:
        return False, "Bump Channel was not found"
    if settings["description"] is None:
        return False, "Server Description was not found"
    return True, None

async def get_delay(ctx, client):    
    settings = db.settings.find_one({"guild_id": ctx.guild.id}, {"_id": 0})
    user = db.settings.find_one({"user_id": ctx.user.id}, {"_id": 0})
    if settings["cooldown"] is None:
        return 0 
                
    if datetime.datetime.now() <= settings["cooldown"]:
        left = settings["cooldown"] - datetime.datetime.utcnow()
        seconds = left.total_seconds()
        minutes = seconds // 60
        
        if db.settings.find_one({"guild_id": ctx.guild.id, "premium":{"exists": True}}):
            if settings["premium"]["status"] is True:
                minutes = minutes - read_config["premium"]
        elif db.settings.find_one({"user_id": ctx.user.id, "premium":{"exists": True}}):
            if user["premium"]["stats"] is True:
                minutes = minutes - read_config["premium"]
                
        channel = client.get_channel(951095386959929355)
        date = datetime.datetime.utcnow() - datetime.timedelta(hours=12)                
        async for message in channel.history(after=date):
            if str(ctx.user.id) in message.content:
                if "top.gg" in message.content:
                    minutes = minutes - read_config["top"]
                if "dbl" in message.content:
                    minutes = minutes - read_config["dbl"]
        return minutes
    return 0
    
async def check_ratelimit(ctx, client):
    left = await get_delay(ctx, client)

    if 0 < left:      
        em = diskord.Embed(title="Server on Cooldown", description=f"You can bump again in {round(left)} minutes.", color=diskord.Colour.red())
        em.add_field(name="Note", value=read_config["note"], inline=False)
        return False, em
    else:
        then = datetime.datetime.utcnow() + datetime.timedelta(minutes=read_config["cooldown"])
        data = {"$set":{"cooldown": then}}
        db.settings.update_one({"guild_id": ctx.guild.id}, data)
        return True, None        
            
async def get_server(ctx):
    settings = db.settings.find_one({"guild_id": ctx.guild.id})
    invite_channel = ctx.guild.get_channel(settings["invite_channel"])
    if not invite_channel:
        invite_channel = ctx.guild.text_channels[0]   
    invite = await invite_channel.create_invite(unique=False, max_age=0, max_uses=0, temporary=False)
    
    em = diskord.Embed(color=diskord.Colour.blue())
    em.set_author(name=f"{ctx.guild.name} ({ctx.guild.id})", icon_url=ctx.guild.icon.url)
    em.add_field(name="Description", value=settings["description"], inline=False)
    em.add_field(name="Members", value=len(ctx.guild.members), inline=True)
    em.add_field(name="Channels", value=len(ctx.guild.channels), inline=True)
    em.add_field(name="Categories", value=len(ctx.guild.categories), inline=True)
    em.add_field(name="Emojis", value=len(ctx.guild.emojis), inline=False) #[emoji for emoji in ctx.guild.id]
    em.set_footer(text="Bumpy | Use /report to report a server")
    
    button = diskord.ui.Button(label="Join Server", style=diskord.ButtonStyle.url, url=f"{invite}")
    view = diskord.ui.View()
    view.add_item(button)
    return em, view

def get_premium_user(user_id):
    if db.settings.find_one({"user_id": user_id, "premium.status": True}):
        settings = db.settings.find_one({"guild_id": user_id})
        if settings["premium"]["expires"] is False:
            return "True"
        expires = datetime.datetime.timestamp(settings["premium"]["expires"])
        return f"True <t:{round(expires)}:D>"
    else:
        return "False"
    
def get_premium_server(guild_id):
    if db.settings.find_one({"guild_id": guild_id, "premium.status": True}):
        settings = db.settings.find_one({"guild_id": guild_id})
        if settings["premium"]["expires"] is False:
            return "True"
        expires = datetime.datetime.timestamp(settings["premium"]["expires"])
        return f"True <t:{round(expires)}:D>"
    else:
        return "False"
