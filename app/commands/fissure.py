import discord
import json
import logging
import time
from datetime import datetime

from discord import app_commands
from discord.ext import commands
from requests import get

logger = logging.getLogger(__name__)

url = "https://api.warframestat.us/PC/fissures?language=en"

class fissure(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='fissure', description="Show the current Fissures")
    async def fissure(self, ctx, type: str = None):
        """
        Usage: !fissure <type> \n
        Default language is en (english)\n
        """
        start = time.time()
        if type == 'sp':
            f_type = 'Steel Path'
        elif type == 'rj':
            f_type = 'Railjack'
        else:
            f_type = ''

        response = get(url)
        data = json.loads(response.text)

        embed = discord.Embed(
            title=f"{f_type} Fissures",
            color=discord.Colour.random()
        )

        fissure_list = []

        if f_type == '':
            for x in data:
                if not x['isStorm'] and not x['isHard']:
                    fissure_list.append(
                        (x['tierNum'], f"{x['tier']} - {x['missionType']} - {x['enemy']}", f"{x['node']}\nEnds: <t:{int(datetime.strptime(x['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())}:R>"))

        elif f_type == 'Steel Path':
            for x in data:
                if x['isHard']:
                    fissure_list.append(
                        (x['tierNum'], f"{x['tier']} - {x['missionType']} - {x['enemy']}", f"{x['node']}\nEnds: <t:{int(datetime.strptime(x['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())}:R>"))

        elif f_type == 'Railjack':
            for x in data:
                if x['isStorm']:
                    fissure_list.append(
                        (x['tierNum'], f"{x['tier']} - {x['missionType']} - {x['enemy']}", f"{x['node']}\nEnds: <t:{int(datetime.strptime(x['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())}:R>"))

        fissures_sorted = sorted(fissure_list, key=lambda x: x[0])

        for fissure in fissures_sorted:
            embed.add_field(
                name=fissure[1],
                value=fissure[2],
                inline=False
            )

        embed.set_footer(text=f"Valid fissure types are: rj (Railjack), sp (Steel Path), <empty> (Normal)" +
                         "\n"+f"Latency: {round((time.time() - start)*1000)}ms")
        await ctx.send(embed=embed)

    @app_commands.command(name="fissures", description="Show the current Fissures")
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    @app_commands.choices(type=[
        discord.app_commands.Choice(name="Normal", value=""),
        discord.app_commands.Choice(name="Steel Path", value="sp"),
        discord.app_commands.Choice(name="Railjack", value="rj"),
    ])
    async def fissures(self, interaction: discord.Interaction, type: discord.app_commands.Choice[str] = None):
        start = time.time()

        if type is None or type.name == "Normal":
            f_type = ''
        else:
            f_type = type.name

        response = get(url)
        data = json.loads(response.text)

        embed = discord.Embed(
            title=f"{f_type} Fissures",
            color=discord.Colour.random()
        )

        fissure_list = []

        if f_type == '':
            for x in data:
                if not x['isStorm'] and not x['isHard']:
                    fissure_list.append(
                        (x['tierNum'], f"{x['tier']} - {x['missionType']} - {x['enemy']}", f"{x['node']}\nEnds: <t:{int(datetime.strptime(x['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())}:R>"))

        elif f_type == 'Steel Path':
            for x in data:
                if x['isHard']:
                    fissure_list.append(
                        (x['tierNum'], f"{x['tier']} - {x['missionType']} - {x['enemy']}", f"{x['node']}\nEnds: <t:{int(datetime.strptime(x['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())}:R>"))

        elif f_type == 'Railjack':
            for x in data:
                if x['isStorm']:
                    fissure_list.append(
                        (x['tierNum'], f"{x['tier']} - {x['missionType']} - {x['enemy']}", f"{x['node']}\nEnds: <t:{int(datetime.strptime(x['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())}:R>"))

        fissures_sorted = sorted(fissure_list, key=lambda x: x[0])

        for fissure in fissures_sorted:
            embed.add_field(
                name=fissure[1],
                value=fissure[2],
                inline=False
            )

        embed.set_footer(text=f"Valid fissure types are: rj (Railjack), sp (Steel Path), <empty> (Normal)" +
                         "\n"+f"Latency: {round((time.time() - start)*1000)}ms")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(fissure(bot))
