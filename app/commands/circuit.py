import logging

import discord
from discord.ext import commands

from app.api.worldstate import worldstate_client

logger = logging.getLogger(__name__)


class Circuit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="circ",
        description="List the current rotation of incarnon genesis",
        aliases=["circus", "incarnon", "circuit"],
    )
    async def circuit(self, ctx):
        worldstate = await worldstate_client.get_worldstate()
        circuits = worldstate.circuits

        embed = discord.Embed(
            title="Current Circuit Rotation for incarnon genesis",
            color=discord.Colour.random(),
            description=f"Ends:  <t:{int(circuits[0].expiry.timestamp())}:R>",
        )
        for circuit in circuits:
            embed.add_field(
                name=f"{circuit.category}",
                value="- " + "\n- ".join(circuit.choices),
                inline=False,
            )

        await ctx.send(embed=embed)

    @discord.app_commands.command(
        name="circuit", description="List the current rotation of incarnon genesis"
    )
    async def circuit_slash(self, interaction: discord.Interaction):
        worldstate = await worldstate_client.get_worldstate()
        circuits = worldstate.circuits

        embed = discord.Embed(
            title="Current Circuit Rotation for incarnon genesis",
            color=discord.Colour.random(),
            description=f"Ends:  <t:{int(circuits[0].expiry.timestamp())}:R>",
        )
        for circuit in circuits:
            embed.add_field(
                name=f"{circuit.category}",
                value="- " + "\n- ".join(circuit.choices),
                inline=False,
            )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Circuit(bot))
