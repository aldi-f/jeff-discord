import discord
import json
import logging
import requests
from datetime import datetime

from discord.ext import commands

logger = logging.getLogger(__name__)


MAPPINGS = {
    "Ostrons": ("plains", "poe", "cetus", "ostron", "earth"),
    "Solaris United": ("venus", "fortuna", "4tuna", "solaris", "vallis"),
    "Entrati": ("deimos", "necralisk", "cambion", "entrati"),
    "The Holdfasts": ("zariman", "holdfast", "holdfasts", "zariman"),
    "Cavia": ("cavia", "loid", "sanctum"),
}


class bounty(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="bounty", with_app_command=True, description="Data about currently running bounties")
    async def bounty(self, ctx: commands.Context, place=None):
        if not place:
            err_embed = discord.Embed(
                description="Specify the bounty place (e.g. -bounty cetus)"
            )
            await ctx.send(embed=err_embed)
            return
        syndicate = list(filter(lambda x: f"{place}" in MAPPINGS[x], MAPPINGS))
        if not syndicate:
            err_embed = discord.Embed(
                description="Be sure to type the correct planet/syndicate/node"
            )
            await ctx.send(embed=err_embed)
            return

        response = requests.get(
            "https://api.warframestat.us/PC/syndicateMissions/?language=en")
        data = json.loads(response.text)

        # filter the bounty data
        bounties = list(filter(lambda x: x["syndicate"] == syndicate[0], data))
        if not bounties:
            print(f"{bounties=}")

            err_embed = discord.Embed(
                description="Something went wrong. Try again later."
            )
            await ctx.send(embed=err_embed)
            return
        embed = discord.Embed(
            title=f"{bounties[0]['syndicate']} Bounties"
        )
        for job in bounties[0]['jobs']:
            embed.add_field(
                name=f"[{'-'.join([f'{x}' for x in job['enemyLevels']])}]{job['type']}",
                value="- "+"\n- ".join(job["rewardPool"]))

        expiration = int(datetime.strptime(bounties[0]['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
        embed.set_footer(
            text=f"Rotation ends: <t:{expiration}:R>"
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(bounty(bot))
