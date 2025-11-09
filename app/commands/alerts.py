import logging
import time

import discord
from discord.ext import commands

from app.api.worldstate import worldstate_client

logger = logging.getLogger(__name__)


class Alerts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="alerts", with_app_command=True, description="Data about current alerts."
    )
    async def alerts(self, ctx):
        """
        Usage: !alerts\n
        Data about current alerts
        """
        start = time.time()
        embed = discord.Embed(color=discord.Colour.random(), title="Alerts")

        worldstate = await worldstate_client.get_worldstate()
        alerts = worldstate.alerts

        if len(alerts) == 0:
            embed.description = "There are no alerts currently running."
            await ctx.send(embed=embed)
            return

        for alert in alerts:
            info = alert.mission_info
            key = f"{info.location} | {info.mission_type} | {info.faction} | ({info.min_level}-{info.max_level})"
            if info.max_waves:
                wave_text = f"Waves: {info.max_waves}\n"
            else:
                wave_text = ""

            rewards = info.mission_reward
            reward_text = "***Rewards:***\n"
            if rewards.credits:
                reward_text += f"- **Credits**: x{rewards.credits}\n"
            for item in rewards.counted_items:
                reward_text += f"- **{item.item}**: x{item.quantity}\n"

            value = (
                f"{wave_text}{reward_text}Ends: <t:{int(alert.expiry.timestamp())}:R>"
            )
            embed.add_field(name=key, value=value, inline=False)

        embed.set_footer(text=f"Latency: {round((time.time() - start) * 1000)}ms")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Alerts(bot))
