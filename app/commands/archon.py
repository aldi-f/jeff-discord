import discord
import json
import logging
import time
from datetime import datetime

from discord import app_commands
from discord.ext import commands
from requests import get

from funcs import get_shard

logger = logging.getLogger(__name__)


class archon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='archon', description="Show the current Archon Hunt Rotation", aliases=['archonhunt', 'sportie', 'ah'])
    async def sortie(self, ctx, lang: str = None):
        """
        Usage: !archon <language>\n
        Defualt language is en (english)\n
        Show the current archon Rotation
        """
        start = time.time()
        if lang is None:
            lang = 'en'

        download_start = time.time()
        response = get(
            f"https://api.warframestat.us/pc/archonHunt?language={lang}")
        download_timer = time.time() - download_start
        data = json.loads(response.text)

        embed = discord.Embed(
            title="Archon Hunt",
            description=f"Boss: {data['boss']}({get_shard(data['boss'])})\nFaction: {data['faction']}",
            color=discord.Colour.random()
        )

        for x in range(len(data["missions"])):
            mission = data["missions"][x]
            embed.add_field(name=f"({x+1}) {mission['type']}",
                            value=f"{mission['node']}",
                            inline=False)

        expiration = int(datetime.strptime(data['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
        embed.set_footer(
            text=f"Ends: <t:{expiration}:R>\nValid Languages: en, es, fr, it, ko, pl, pt, ru, zh\nTotal Latency: {round((time.time() - start)*1000)}ms\nDownload Latency: {round(download_timer*1000)}ms")
        await ctx.send(embed=embed)

    @app_commands.command(name="archon-hunt", description="Show the current Archon Hunt Rotation")
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    @app_commands.choices(language=[
        discord.app_commands.Choice(name="English", value="en"),
        discord.app_commands.Choice(name="Spanish", value="es"),
        discord.app_commands.Choice(name="French", value="fr"),
        discord.app_commands.Choice(name="Italian", value="it"),
        discord.app_commands.Choice(name="Korean", value="ko"),
        discord.app_commands.Choice(name="Polish", value="pl"),
        discord.app_commands.Choice(name="Portuguese", value="pt"),
        discord.app_commands.Choice(name="Russian", value="ru"),
        discord.app_commands.Choice(name="Chinese", value="zh")
    ])
    async def archon_hunt(self, interaction: discord.Interaction, language: discord.app_commands.Choice[str] = None):
        if language is None:
            lang = 'en'
        else:
            lang = language.value
        response = get(
            f"https://api.warframestat.us/pc/archonHunt?language={lang}")
        data = json.loads(response.text)

        embed = discord.Embed(
            title="Archon Hunt",
            description=f"Boss: {data['boss']}({get_shard(data['boss'])})\nFaction: {data['faction']}\nEnds: <t:{expiration}:R>",
            color=discord.Colour.random()
        )

        for x in range(len(data["missions"])):
            mission = data["missions"][x]
            embed.add_field(name=f"({x+1}) {mission['type']}",
                            value=f"{mission['node']}",
                            inline=False)

        expiration = int(datetime.strptime(data['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
        embed.set_footer(
            text=f"Valid Languages: en, es, fr, it, ko, pl, pt, ru, zh")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(archon(bot))
