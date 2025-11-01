import discord
import logging

from discord.ext import commands

from app.api.worldstate import worldstate_client

logger = logging.getLogger(__name__)


class darvo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="darvo", with_app_command=True, description="Daily Darvo deal")
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def darvo(self, ctx: commands.Context):
        worldstate = await worldstate_client.get_worldstate()
        darvo_deal = worldstate.daily_deals[0]
        expiration = int(darvo_deal.expiry.timestamp())


        set_embed = discord.Embed(
            description=(f"## {darvo_deal.store_item}\n"
                         f"### {darvo_deal.amount_total - darvo_deal.amount_sold}/{darvo_deal.amount_total} left\n"
                         f"Price: ~~{darvo_deal.original_price}~~ {darvo_deal.sale_price}<:Platinum:992917150358589550> ({darvo_deal.discount}% off)\n\n"
                         f"Ends: <t:{expiration}:F>"),
            title="Darvo's Daily Deal"
        )

        await ctx.send(embed=set_embed)


async def setup(bot):
    await bot.add_cog(darvo(bot))
