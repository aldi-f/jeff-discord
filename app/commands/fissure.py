import logging
import time

import discord
from discord import app_commands
from discord.ext import commands

from app.api.worldstate import worldstate_client

logger = logging.getLogger(__name__)


class fissure(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fissure", description="Show the current Fissures")
    async def fissure(self, ctx, fissure_type: str = ""):
        """
        Usage: -fissure <type>
        """
        start = time.time()
        if fissure_type == "sp":
            f_type = "Steel Path "
        # elif fissure_type == 'rj':
        #     f_type = 'Railjack'
        else:
            f_type = ""

        start = time.time()
        worldstate = await worldstate_client.get_worldstate()
        fissures = worldstate.active_missions

        embed = discord.Embed(title=f"{f_type}Fissures", color=discord.Colour.random())

        fissure_list = []

        for fissure in fissures:
            modifier = fissure.modifier
            tier = fissure.tier
            mission_type = fissure.mission_type
            node = fissure.node

            if fissure.hard and fissure_type != "sp":
                continue

            fissure_list.append(
                (
                    tier,
                    f"{modifier} - {mission_type} ({fissure.hard})",
                    f"{node}\nEnds: <t:{int(fissure.expiry.timestamp())}:R>",
                )
            )

        fissures_sorted = sorted(fissure_list, key=lambda x: x[0])

        for fissure in fissures_sorted:
            embed.add_field(name=fissure[1], value=fissure[2], inline=False)

        embed.set_footer(
            text="Valid fissure types are: rj (Railjack), sp (Steel Path), <empty> (Normal)"
            + "\n"
            + f"Latency: {round((time.time() - start) * 1000)}ms"
        )
        await ctx.send(embed=embed)

    @app_commands.command(name="fissures", description="Show the current Fissures")
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    @app_commands.choices(
        fissure_type=[
            discord.app_commands.Choice(name="Normal", value=""),
            discord.app_commands.Choice(name="Steel Path", value="sp"),
            discord.app_commands.Choice(name="Railjack", value="rj"),
        ]
    )
    async def fissures(
        self,
        interaction: discord.Interaction,
        fissure_type: discord.app_commands.Choice[str] = None,
    ):
        """
        Usage: -fissure <type>
        """
        start = time.time()
        if fissure_type == "sp":
            f_type = "Steel Path "
        # elif fissure_type == 'rj':
        #     f_type = 'Railjack'
        else:
            f_type = ""

        start = time.time()
        worldstate = await worldstate_client.get_worldstate()
        fissures = worldstate.active_missions

        embed = discord.Embed(title=f"{f_type}Fissures", color=discord.Colour.random())

        fissure_list = []

        for fissure in fissures:
            modifier = fissure.modifier
            tier = fissure.tier
            mission_type = fissure.mission_type
            node = fissure.node

            if fissure.hard and fissure_type != "Steel Path ":
                continue

            fissure_list.append(
                (
                    tier,
                    f"{modifier} - {mission_type} ({fissure.hard})",
                    f"{node}\nEnds: <t:{int(fissure.expiry.timestamp())}:R>",
                )
            )

        fissures_sorted = sorted(fissure_list, key=lambda x: x[0])

        for fissure in fissures_sorted:
            embed.add_field(name=fissure[1], value=fissure[2], inline=False)

        embed.set_footer(
            text="Valid fissure types are: rj (Railjack), sp (Steel Path), <empty> (Normal)"
            + "\n"
            + f"Latency: {round((time.time() - start) * 1000)}ms"
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(fissure(bot))
