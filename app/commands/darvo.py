import discord
import json
import logging
import requests
from datetime import datetime

from discord.ext import commands

logger = logging.getLogger(__name__)

url = "https://api.warframestat.us/PC/dailyDeals?language=en"


class darvo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="darvo", with_app_command=True, description="Daily Darvo deal")
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def darvo(self, ctx: commands.Context):
        response = requests.get(url)
        data = json.loads(response.text)[0]
        expiration = int(datetime.strptime(data['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
        set_embed = discord.Embed(
            description=f"## {data['item']}\n### {data['total']-data['sold']}/{data['total']} left\nPrice: ~~{data['originalPrice']}~~ {data['salePrice']}<:Platinum:992917150358589550> ({data['discount']}% off)\n\nEnds: <t:{expiration}:R>",
            title="Darvo's Daily Deal"
        )

        await ctx.send(embed=set_embed)


async def setup(bot):
    await bot.add_cog(darvo(bot))
