import discord
import json
import logging
import time
from datetime import datetime

from discord.ext import commands
from requests import get

logger = logging.getLogger(__name__)


class baro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='baro', with_app_command=True, description="Show current baro status and his inventory")
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def baro(self, ctx):
        """
        Usage: !baro\n
        Show current baro status and his inventory
        """
        start = time.time()
        response = get(f"https://api.warframestat.us/pc/voidTrader")
        data = json.loads(response.text)

        if not data['inventory']:
            noBaro = discord.Embed(title="Baro Ki'Teer")
            activation = int(datetime.strptime(data['activation'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
            noBaro.add_field(
                name=f"Incoming: <t:{activation}:R>",
                value=f"Location: {data['location']}"
            )

            await ctx.send(embed=noBaro)
            return
        else:
            text = ''

            for x in data['inventory']:
                text += f"{x['item']}: \u3000 {x['ducats']}<:Ducat:967433339868950638>| {x['credits']}<:Credits:967435392427106348>\n"

            embed = discord.Embed(
                title="Baro Ki'Teer Inventory",
                description=f"{data['location']}\n\n{text}"
            )
            expiration = int(datetime.strptime(data['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
            embed.set_footer(
                text=f"Leaving: <t:{expiration}:R>\nLatency: {round((time.time() - start)*1000)}ms"
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(baro(bot))
