from diskord.ext import commands
import diskord

from utils.functions import *
class bump(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @diskord.application.slash_command(name="bump", description="Push the server to more users server")
    async def bump(self, ctx):
        check_guild(ctx.guild.id, "bump")
        cb, reason = check_blocked(ctx.guild.id, ctx.user.id)
        if cb is True:
            em = diskord.Embed(title="Your server has been banned", description="If you want to appeal your ban [click here](https://discord.gg/KcH28tRtBu)", color=diskord.Colour.red())
            em.add_field(name="Reason", value=reason, inline=False)
            await ctx.respond(embed=em)
            return

        cfs, response = check_for_server(ctx)
        if cfs is False:
            em = diskord.Embed(title=response, color=diskord.Colour.red())
            await ctx.respond(embed=em)
            return

        status, response = await bump_check(ctx, self.client)
        if status is False:
            em = diskord.Embed(title=response, color=diskord.Colour.red())
            await ctx.respond(embed=em)
            return
        
        status, response = await check_ratelimit(ctx, self.client)
        if status is False:
            await ctx.respond(embed=response)
            return
        
        em = diskord.Embed(title="Bumping!", description="The server is being bumped", color=diskord.Colour.blue())
        em.add_field(name="Note", value=read_config["note"], inline=False)
        await ctx.respond(embed=em)
        add_command_stats("bump")
        
        server_embed, server_button = await get_server(ctx)
        
        channel_ids = db.settings.find({}, {"_id": 0, "status": 1, "bump_channel": 1})
        for item in channel_ids:
            try:
                channel = self.client.get_channel(item["bump_channel"])
            except Exception:
                pass
            if channel:
                if not item["status"] is None:
                    pass
                else:
                    try:
                        await channel.send(embed=server_embed, view=server_button)
                    except Exception:
                        pass
        
        em = diskord.Embed(title="Bumped!", description="The server has been bumped.", color=diskord.Colour.green())
        em.add_field(name="Note", value=read_config["note"], inline=False)
        await ctx.channel.send(embed=em)
        
def setup(client):
    client.add_cog(bump(client))
