import json
import logging
import re

import discord
from discord.ext import commands
from requests import get

logger = logging.getLogger(__name__)


class eda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="eda", description="Get the currently running EDA", aliases=["deep", "da"]
    )
    async def eda(self, ctx):
        res = get("https://content.warframe.com/dynamic/worldState.php")
        data = res.json()

        # data is currently stored on temp var
        temp = json.loads(data["Tmp"]).get("lqo27")
        if not temp:
            return await ctx.send(f"No data found!")
        try:
            missions = [split_words(miss) for miss in temp["mt"]]
            modifiers = [
                [split_words(mod) for mod in mod_group] for mod_group in temp["c"]
            ]
            deviations = [split_words(dev) for dev in temp["mv"]]
            confitions = [split_words(cond) for cond in temp["fv"]]

            embed = discord.Embed(
                title="Deep Archimedea", color=discord.Colour.random()
            )

            embed.add_field(
                name=f"Conditions", value=f"- {f'\n- '.join(confitions)}", inline=False
            )

            for i, group in enumerate(zip(missions, modifiers, deviations)):
                mission, modifier, deviation = group
                embed.add_field(
                    name=f"{i + 1} - {mission}",
                    value=f"Modifiers:\n- {deviation}\n- {modifier[0]}\n- **{modifier[1]}**\n",
                    inline=False,
                )

            await ctx.send(embed=embed)

        except Exception as e:
            print(e)
            return await ctx.send(f"Something went wrong!")


async def setup(bot):
    await bot.add_cog(eda(bot))


def split_words(word: str) -> str:
    return " ".join(re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z][a-z]*", word))
