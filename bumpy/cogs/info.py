from discord.ext import commands
import discord
from discord import app_commands
import sys

from utils.functions import *

class info(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @app_commands.command(name="botinfo", description="Show stats for Bumpy")
    async def botinfo(self, interaction):
        add_command_stats("botinfo")
        mongo = db.command("dbstats")
        dataSize = mongo["dataSize"]
        storageSize = mongo["storageSize"]
        used = dataSize / storageSize
        procent = used * 100
        procent = round(procent)
        stats = db.stats.find_one({}, {"bumps": 1, "commands": 1})
        bumps = stats["bumps"]
        commands = stats["commands"]
        
        guilds = len(self.client.guilds)
        users = len(self.client.users)
        
        info1 = f"**Developer:** kevie#0011\n**Guild Count:** {guilds}\n**User Count:** {users}\n\n"
        info2 = f"**Python:** {sys.version[0]}.{sys.version[2]}\n**discord:** {discord.__version__}\n\n"
        info3 = f"**Memory Used:** {dataSize} MB | {procent}%\n\n"
        info4 = f"**Total Commands:** {commands}\n**Total Bumps:** {bumps}"
        
        em = discord.Embed(title="Bumpy Information", color=discord.Color.blue())
        em.description = f"{info1}{info2}{info3}{info4}"
        await interaction.response.send_message(embed=em)
        
    @app_commands.command(name="info", description="Show information about Bumpy")
    async def info(self, interaction):
        add_command_stats("info")
        view = discord.ui.View()
        
        invite_button = discord.ui.Button(label="Invite", style=discord.ButtonStyle.url, url="https://discord.com/api/oauth2/authorize?client_id=880766859534794764&permissions=137976179857&scope=bot%20applications.commands&redirect_uri=https%3A%2F%2Fdiscord.gg%2FKcH28tRtBu&response_type=code", row=1)
        view.add_item(invite_button)
        
        support_button = discord.ui.Button(label="Support", style=discord.ButtonStyle.url, url="https://discord.gg/KcH28tRtBu", row=1)
        view.add_item(support_button)
        
        rules_button = discord.ui.Button(label="Rules", style=discord.ButtonStyle.url, url="https://github.com/thekevie/bumpy/blob/main/RULES.md", row=1)
        view.add_item(rules_button)
        
        terms_button = discord.ui.Button(label="Terms Of Service", style=discord.ButtonStyle.url, url="https://github.com/thekevie/bumpy/blob/main/TERMS.md", row=2)
        view.add_item(terms_button)
        
        privacy_button = discord.ui.Button(label="Privacy Policy", style=discord.ButtonStyle.url, url="https://github.com/thekevie/bumpy/blob/main/PRIVACY.md", row=2)
        view.add_item(privacy_button)
        
        em = discord.Embed(title="Bumpy Information", color=discord.Color.blue())
        em.description = "Comming Soon"
        await interaction.response.send_message(embed=em, view=view)
        
    @app_commands.command(name="vote", description="Get websites where you can vote on Bumpy")
    async def vote(self, interaction):
        add_command_stats("vote")
        view = discord.ui.View()
        
        topgg_button = discord.ui.Button(label="TOP.GG", style=discord.ButtonStyle.url, url="https://top.gg/bot/880766859534794764/vote")
        view.add_item(topgg_button)
        
        dbl_button = discord.ui.Button(label="DBL", style=discord.ButtonStyle.url, url="https://discordbotlist.com/bots/bumpy-5009/upvote")
        view.add_item(dbl_button)
        
        em = discord.Embed(title="Vote on Bumpy", description="If you vote for Bumpy on both websites you will get 10 minutes \nless cooldown on the bump command in any server.", color=discord.Color.blue())
        await interaction.response.send_message(embed=em, view=view)
        
    @app_commands.command(name="invite", description="Get the invite link to Bumpy")
    async def invite(self, interaction):
        add_command_stats("invite")
        view = discord.ui.View()
        
        invite_button = discord.ui.Button(label="Invite Me", style=discord.ButtonStyle.url, url="https://discord.com/api/oauth2/authorize?client_id=880766859534794764&permissions=137976179857&scope=bot%20applications.commands&redirect_uri=https%3A%2F%2Fdiscord.gg%2FKcH28tRtBu&response_type=code")
        view.add_item(invite_button)
        
        support_button = discord.ui.Button(label="Support Server", style=discord.ButtonStyle.url, url="https://discord.gg/KcH28tRtBu")
        view.add_item(support_button)
        
        em = discord.Embed(title="Invite Bumpy to your server", color=discord.Color.blue())
        await interaction.response.send_message(embed=em, view=view)
 
    @app_commands.command(name="userinfo", description="Get information about a user")
    async def userinfo(self, interaction, user: discord.User=None):
        add_command_stats("userinfo")
        user = user or interaction.user
        username = f"**Name:** {user.display_name}#{user.discriminator}"
        userid = f"**User ID:** `{user.id}`"
        created = f"**Created:** <t:{round(datetime.datetime.timestamp(user.created_at))}:D>"
        joined = f"**Joined:** <t:{round(datetime.datetime.timestamp(user.joined_at))}:D>"
        premium = f"**Premium:** {get_premium_user(user.id)}"
        em = discord.Embed(color=discord.Color.blue())
        em.description = f"{username}\n{userid}\n{created}\n{joined}\n{premium}"
        await interaction.response.send_message(embed=em)
        
    @app_commands.command(name="serverinfo", description="Get information about the server")
    async def userinfo(self, interaction):
        add_command_stats("serverinfo")
        guild = interaction.guild
        guildname = f"**Name:** {guild.name}"
        guildid = f"**Guild ID:** `{guild.id}`"
        owner = f"**Owner:** {guild.owner.display_name}#{guild.owner.discriminator}"
        members = f"**Members:** {(guild.member_count)}"
        created = f"**Created:** <t:{round(datetime.datetime.timestamp(guild.created_at))}:D>"
        premium = f"**Premium:** {get_premium_server(guild.id)}"
        em = discord.Embed(color=discord.Color.blue())
        em.description = f"{guildname}\n{guildid}\n{owner}\n{created}\n{premium}"
        await interaction.response.send_message(embed=em)
         
async def setup(client):
    await client.add_cog(info(client))