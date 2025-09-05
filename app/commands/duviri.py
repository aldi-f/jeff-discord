import discord
import logging
import requests

from discord.ext import commands
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


CYCLES = [
    # name       kullervo?      POI
    ("Sorrow", True, ["Archarbor", "Kullervo's Hold"]),
    ("Fear", True, ["Amphitheater", "Kullervo's Hold"]),
    ("Joy", False, ["Archarbor", "Amphitheater"]),
    ("Anger", True, ["Amphitheater", "Kullervo's Hold"]),
    ("Envy", False, ["Archarbor", "Amphitheater"]),
]

url = "https://api.warframestat.us/pc/duviriCycle/"


def find_next_cycle(current_cycle: str) -> str:
    index = [cycle[0] for cycle in CYCLES].index(current_cycle)
    next_index = (index + 1) % len(CYCLES)
    return CYCLES[next_index][0]


class duviri(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="duviri", with_app_command=True, description="Current Duviri rotation")
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def duviri(self, ctx: commands.Context):
        duviri_api = requests.get(
            "https://api.warframestat.us/pc/duviriCycle/").json()

        expiry = duviri_api['expiry']
        state = duviri_api['state']
        target_timestamp = datetime.strptime(expiry, "%Y-%m-%dT%H:%M:%S.%fZ")

        current_timestamp = datetime.now(tz=None)

        if current_timestamp.dst():
            current_timestamp = current_timestamp - timedelta(hours=1)

        current_timestamp_string = current_timestamp.strftime(
            "%Y-%m-%dT%H:%M:%S")

        time_left = target_timestamp - current_timestamp

        negative = False
        if time_left.total_seconds() < 0:  # check for
            time_left = abs(time_left)
            negative = True

        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        timing = ""
        if negative:
            timing += "- "
        if hours:
            timing += f"{hours} hour "
        if minutes > 1:
            timing += f"{minutes} minutes "
        elif minutes:
            timing += f"{minutes} minute "
        if seconds > 1:
            timing += f"{seconds} seconds "
        elif seconds:
            timing += f"{seconds} second"

        current_cycle = state.capitalize()
        current_name, current_kullervo, current_poi = [
            cycle for cycle in CYCLES if cycle[0] == current_cycle][0]

        next_cycle = find_next_cycle(current_cycle)
        next_name, next_kullervo, _ = [
            cycle for cycle in CYCLES if cycle[0] == next_cycle][0]

        poi = "**Points of Interest**:\n"
        for point in current_poi:
            poi += f"- {point}\n"

        embed = discord.Embed(
            title=f"Duviri Cycles",
            description=f"# {current_name} \n{'*Kullervo can spawn here*' if current_kullervo else ''}\n\n{poi}\n",
            color=discord.Colour.random()
        )
        embed.set_footer(
            text=f"{next_name} {'(kullervo)' if next_kullervo else ''} in {timing}\nCurrent time: {current_timestamp_string}"
        )

        await ctx.send(embed=embed)


async def setup(bot: discord):
    await bot.add_cog(duviri(bot))
