import discord
import json
import logging
import time
from datetime import datetime

from discord.ext import commands
from requests import get

logger = logging.getLogger(__name__)


class Alerts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="alerts", with_app_command=True, description="Data about current alerts."
    )
    async def alerts(self, ctx):
        """
        Usage: !alerts\n
        Data about current alerts
        """
        start = time.time()
        embed = discord.Embed(color=discord.Colour.random(), title=f"Alerts")

        res = get("https://api.warframestat.us/pc/alerts")
        data = json.loads(res.text)
        if len(data) == 0:
            err = discord.Embed(
                color=discord.Colour.random(),
                description="There are no alerts currently running.",
            )
            await ctx.send(embed=err)
            return

        for alert in data:
            x = alert.get("mission")
            expiry = alert.get("expiry")
            key = f"{x.get('nodeKey')} | {x.get('typeKey')} | {x.get('factionKey')} | ({x.get('minEnemyLevel')}-{x.get('maxEnemyLevel')})"
            # length = x.get("maxWaveNum")
            # length_text = f"Waves: {length}\n" if length else ''
            value = f"Rewards: {x.get('reward').get('asString')}\nEnds: <t:{int(datetime.strptime(expiry, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())}:R>"
            embed.add_field(name=key, value=value, inline=False)

        embed.set_footer(text=f"Latency: {round((time.time() - start) * 1000)}ms")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Alerts(bot))
