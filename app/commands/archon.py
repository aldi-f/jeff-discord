import discord
import json
import logging
import time
from datetime import datetime

from discord import app_commands
from discord.ext import commands
from requests import get

from app.api.worldstate import worldstate_client
from app.funcs import get_shard

logger = logging.getLogger(__name__)


class Archon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='archon', description="Show the current Archon Hunt Rotation", aliases=['archonhunt', 'sportie', 'ah'])
    async def sortie(self, ctx):
        """
        Usage: -archon <language>\n
        Show the current archon Rotation
        """
        start = time.time()
        worldstate = await worldstate_client.get_worldstate()
        archon = worldstate.lite_sorties[0]

        embed = discord.Embed(
            title="Archon Hunt",
            description=f"Boss: {archon.boss}({get_shard(archon.boss)})\nEnds: <t:{int(archon.expiry.timestamp())}:R>",
            color=discord.Colour.random()
        )

        for i, mission in enumerate(archon.missions):
            embed.add_field(name=f"({i+1}) {mission.mission_type}",
                            value=f"{mission.node}",
                            inline=False)

        embed.set_footer(
            text=f"Latency: {round((time.time() - start)*1000)}ms")
        await ctx.send(embed=embed)

    @app_commands.command(name="archon-hunt", description="Show the current Archon Hunt Rotation")
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def archon_hunt(self, interaction: discord.Interaction):
        """
        Usage: -archon <language>\n
        Show the current archon Rotation
        """
        start = time.time()
        worldstate = await worldstate_client.get_worldstate()
        archon = worldstate.lite_sorties[0]

        embed = discord.Embed(
            title="Archon Hunt",
            description=f"Boss: {archon.boss}({get_shard(archon.boss)})\nEnds: <t:{int(archon.expiry.timestamp())}:R>",
            color=discord.Colour.random()
        )

        for i, mission in enumerate(archon.missions):
            embed.add_field(name=f"({i+1}) {mission.mission_type}",
                            value=f"{mission.node}",
                            inline=False)

        embed.set_footer(
            text=f"Latency: {round((time.time() - start)*1000)}ms")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Archon(bot))
