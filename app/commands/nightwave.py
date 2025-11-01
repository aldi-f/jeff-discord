import discord
import logging
import time

from discord.ext import commands
from app.api.worldstate import worldstate_client

logger = logging.getLogger(__name__)


class nightwave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='nw', description="Show the current Nightwave Rotation", aliases=['nightwave', 'night'])
    async def nw(self, ctx):
        """
        Usage: -nightwave\n
        Show the current Nightwave Rotation
        """
        start = time.time()
        worldstate = await worldstate_client.get_worldstate()
        nightwave = worldstate.season_info

        embed = discord.Embed(
            title=f"{nightwave.affiliation_tag}",
            description=f"Challenges:",
            color=discord.Colour.random()
        )
        for challenge in nightwave.active_challenges:
            embed.add_field(
                name=f"{challenge.type}:{challenge.challenge}",
                value=f"{challenge.standing} Reputation",
                inline=False
            )

        embed.set_footer(text=f"Latency: {round((time.time() - start)*1000)}ms{chr(10)}")
        await ctx.send(embed=embed)

    @discord.app_commands.command(name='nightwave', description="Show the current Nightwave Rotation")
    async def slash_nw(self, interaction: discord.Interaction):
        """
        Usage: -nightwave\n
        Show the current Nightwave Rotation
        """
        start = time.time()
        worldstate = await worldstate_client.get_worldstate()
        nightwave = worldstate.season_info

        embed = discord.Embed(
            title=f"{nightwave.affiliation_tag}",
            description=f"Challenges:",
            color=discord.Colour.random()
        )
        for challenge in nightwave.active_challenges:
            embed.add_field(
                name=f"{challenge.type}:{challenge.challenge}",
                value=f"{challenge.standing} Reputation",
                inline=False
            )

        embed.set_footer(text=f"Latency: {round((time.time() - start)*1000)}ms{chr(10)}")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(nightwave(bot))
