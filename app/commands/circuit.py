import discord
import logging
import re

from datetime import datetime, timedelta
from discord.ext import commands
from requests import get

from app.funcs import FIRST_WEEK

logger = logging.getLogger(__name__)


class circuit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='circ', description="List the current rotation of incarnon genesis", aliases=['circus', 'incarnon', 'circuit'])
    async def circuit(self, ctx):

        circuit_data = await get_circuit_data()

        embed = discord.Embed(
            title="Current Circuit Rotation for incarnon genesis",
            color=discord.Colour.random()
        )

        embed.add_field(name="Weapons", value="- " +
                        "\n- ".join(circuit_data["weapons"]), inline=False)
        embed.add_field(name="Warframes", value="- " +
                        "\n- ".join(circuit_data["warframes"]), inline=False)

        days, hours, minutes, seconds = circuit_data["time_remaining"]
        embed.set_footer(
            text=f"Rotation ends in:{days}d, {hours}h, {minutes}m, {seconds}s\n")
        await ctx.send(embed=embed)

    @discord.app_commands.command(name='circuit', description="List the current rotation of incarnon genesis")
    async def circuit_slash(self, interaction: discord.Interaction):

        circuit_data = await get_circuit_data()

        embed = discord.Embed(
            title="Current Circuit Rotation for incarnon genesis",
            color=discord.Colour.random()
        )
        embed.add_field(name="Weapons", value="- " +
                        "\n- ".join(circuit_data["weapons"]), inline=False)
        embed.add_field(name="Warframes", value="- " +
                        "\n- ".join(circuit_data["warframes"]), inline=False)

        days, hours, minutes, seconds = circuit_data["time_remaining"]
        embed.set_footer(
            text=f"Rotation ends in:{days}d, {hours}h, {minutes}m, {seconds}s\n")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(circuit(bot))


async def get_circuit_data():
    current_timestamp = datetime.now(tz=None)
    res = get("https://content.warframe.com/dynamic/worldState.php")
    data = res.json()
    weapons = [re.sub(r'([a-z])([A-Z])', r'\1 \2', wep)
               for wep in data["EndlessXpChoices"][1]["Choices"]]
    warframes = [re.sub(r'([a-z])([A-Z])', r'\1 \2', wf)
                 for wf in data["EndlessXpChoices"][0]["Choices"]]
    time_remaining = calculate_time_remaining(current_timestamp)

    return {
        "weapons": weapons,
        "warframes": warframes,
        "time_remaining": time_remaining
    }


def calculate_time_remaining(current_time: datetime):
    # get first week time
    week1_timestamp = datetime.fromtimestamp(FIRST_WEEK)
    # check how much time passed
    time_passed = current_time - week1_timestamp
    # get the number of weeks
    weeks_passed = time_passed.days//7
    # get the timestamp for next reset
    next_reset = week1_timestamp + timedelta(weeks=weeks_passed + 1)

    time_remaining = next_reset - current_time

    # now parse it into different periods
    days = time_remaining.days
    hours, remainder = divmod(time_remaining.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return days, hours, minutes, seconds
