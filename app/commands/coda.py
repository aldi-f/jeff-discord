import discord
import logging
import requests
from datetime import datetime, timedelta
from pytz import UTC

from discord.ext import commands

logger = logging.getLogger(__name__)
# pinned start with summer time aware datetime to avoid issues with timezones

PINNED_START = datetime(2023, 6, 23, 0, 0, 0, tzinfo=UTC)
ROTATIONS = [
    {
        "Primary": ["Coda Hema", "Coda Sporothrix"],
        "Secondary": ["Coda Catabolyst", "Coda Pox", "Coda Dual Torxica"],
        "Melee": ["Coda Mire, Coda Motovore"]
    },
    {
        "Primary": ["Coda Bassocyst", "Coda Synapse"],
        "Secondary": ["Coda Tysis"],
        "Melee": ["Coda Caustacyst, Coda Hirudo", "Coda Pathocyst"]
    }
]


class coda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="coda", with_app_command=True, description="Current Coda rotation.")
    async def coda(self, ctx: commands.Context):
        """Display the current Coda rotation."""
        now = datetime.now(UTC)
        days_since_start = (now - PINNED_START).days
        rotation_index = (days_since_start // 4) % len(ROTATIONS)
        rotation = ROTATIONS[rotation_index]

        next_rotation = f"<t:{int((PINNED_START + timedelta(days=(rotation_index + 1) * 4)).timestamp())}:f>"

        embed = discord.Embed(
            title="Current Coda Rotation",
            description=f"Rotation #{rotation_index + 1}",
            color=discord.Color.green(),

        )
        for weapon_type, weapons in rotation.items():
            embed.add_field(name=weapon_type, value="- "+"\n- ".join(weapons), inline=False)

        embed.set_footer(text=f"Next rotation: {next_rotation}")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(coda(bot))
