import discord
import logging
import time

from discord.ext import commands

from app.api.worldstate import worldstate_client

logger = logging.getLogger(__name__)


class sortie(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="sortie",
        with_app_command=True,
        description="Show the current Sortie Rotation",
    )
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def sortie(self, ctx):
        """
        Usage: -sortie\n
        Show the current Sortie Rotation
        """
        start = time.time()

        worldstate = await worldstate_client.get_worldstate()
        sortie = worldstate.sorties[0]

        embed = discord.Embed(
            title="Sortie",
            description=f"Boss: {sortie.boss}\nEnds: <t:{int(sortie.expiry.timestamp())}:R>",
            color=discord.Colour.random(),
        )

        for i, mission in enumerate(sortie.variants):
            embed.add_field(
                name=f"({i + 1}) {mission.mission_type}",
                value=f"{mission.node}\nCondition: {mission.mission_type}\nEffect: TODO",
                inline=False,
            )

        embed.set_footer(text=f"Total Latency: {round((time.time() - start) * 1000)}ms")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(sortie(bot))
