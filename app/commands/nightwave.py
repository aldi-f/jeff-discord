import discord
import json
import logging
import time

from discord.ext import commands
from requests import get

logger = logging.getLogger(__name__)


class nightwave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='nw', description="Show the current Nightwave Rotation", aliases=['nightwave', 'night'])
    async def nw(self, ctx, lang: str = None):
        """
        Usage: !nightwave <language>\n
        Defualt language is en (english)\n
        Show the current Nightwave Rotation
        """
        start = time.time()
        if lang is None:
            lang = 'en'

        download_start = time.time()
        response = get(
            f"https://api.warframestat.us/PC/nightwave?language={lang}")
        download_timer = time.time() - download_start
        data = json.loads(response.text)

        embed = discord.Embed(
            title=f"{data['tag']}",
            description=f"Challenges:",
            color=discord.Colour.random()
        )
        for x in data['activeChallenges']:
            nw_type = ""
            if 'isDaily' in x and x['isDaily'] == True:
                nw_type = "Daily"
            elif x['isElite'] == True:
                nw_type = "Elite Weekly"
            else:
                nw_type = "Weekly"
            embed.add_field(
                name=f"{nw_type}:{x['desc']}",
                value=f"{x['reputation']} Reputation",
                inline=False
            )

        embed.set_footer(text="Valid Languages: en, es, fr, it, ko, pl, pt, ru, zh" + "\n" +
                         f"Total Latency: {round((time.time() - start)*1000)}ms{chr(10)}Download Latency: {round(download_timer*1000)}ms{chr(10)}")
        await ctx.send(embed=embed)

    @discord.app_commands.command(name='nightwave', description="Show the current Nightwave Rotation")
    async def slash_nw(self, interaction: discord.Interaction):
        """
        Usage: -nightwave <language>\n
        Defualt language is en (english)\n
        Show the current Nightwave Rotation
        """
        start = time.time()
        lang = 'en'

        download_start = time.time()
        response = get(
            f"https://api.warframestat.us/PC/nightwave?language={lang}")
        download_timer = time.time() - download_start
        data = json.loads(response.text)

        embed = discord.Embed(
            title=f"{data['tag']}",
            description=f"Challenges:",
            color=discord.Colour.random()
        )
        for x in data['activeChallenges']:
            nw_type = ""
            if 'isDaily' in x and x['isDaily'] == True:
                nw_type = "Daily"
            elif x['isElite'] == True:
                nw_type = "Elite Weekly"
            else:
                nw_type = "Weekly"
            embed.add_field(
                name=f"{nw_type}:{x['desc']}",
                value=f"{x['reputation']} Reputation",
                inline=False
            )

        embed.set_footer(
            text=f"Total Latency: {round((time.time() - start)*1000)}ms{chr(10)}Download Latency: {round(download_timer*1000)}ms{chr(10)}")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(nightwave(bot))
