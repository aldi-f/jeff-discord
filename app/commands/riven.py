import json
import logging
import time

import discord
import requests
from discord.ext import commands
from warframe_market.api import Rivens
from warframe_market.client import WarframeMarketClient

logger = logging.getLogger(__name__)


class riven(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="riven",
        with_app_command=True,
        description="Shows the matching riven prices.",
    )
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def riven(self, ctx, *, weapon: str | None = None):
        """
        Usage: !riven <weapon-name>\n
        Shows the matching riven prices
        """
        start = time.time()
        if weapon is None:
            error = discord.Embed(description="Please provide a weapon name.")
            await ctx.send(embed=error)

        try:
            wfm_client = WarframeMarketClient()
            rivens = await wfm_client.get(Rivens)

            slug = ""
            emb_title = ""

            for riven in rivens.data:
                if (
                    weapon.lower() == riven.i18n["en"].lower()  # exact match
                    or weapon.lower() in riven.i18n["en"].lower()  # partial match
                ):
                    slug = riven.slug
                    emb_title = riven.i18n["en"]

            riven_embed = discord.Embed(title=emb_title)

            if len(slug) != 0:
                res_market = requests.get(
                    f"https://api.warframe.market/v1/auctions/search?type=riven&weapon_url_name={slug}&sort_by=price_asc"
                )
                market = json.loads(res_market.text)["payload"]["auctions"]
                counter = 0
                for x in market:
                    if counter == 3:
                        break

                    if x["owner"]["status"] != "offline":
                        attributes = ""
                        for att in x["item"]["attributes"]:
                            sign = ""
                            symbol = "%"
                            bonus = " ".join(att["url_name"].split("_")).capitalize()
                            if "positive" in att:
                                sign = "+"

                            if "range" in att["url_name"]:
                                symbol = "m"
                            elif "combo_duration" in att["url_name"]:
                                symbol = "s"
                            elif "punch" in att["url_name"]:
                                symbol = ""

                            attributes += f"{sign}{att['value']}{symbol} {bonus}\n"

                        counter += 1

                        riven_embed.add_field(
                            name=f"{x['owner']['ingame_name']}: {x['item']['weapon_url_name'].capitalize()} {x['item']['name'].capitalize()} {x['buyout_price']}<:Platinum:992917150358589550>",
                            value=attributes,
                            inline=False,
                        )

                riven_embed.set_footer(
                    text=f"Latency: {round((time.time() - start) * 1000)}ms"
                )
                await ctx.send(embed=riven_embed)
            else:
                error = discord.Embed(
                    description="Riven not found, make sure to type the correct name."
                )
        except Exception as e:
            await ctx.send(f"Something went wrong: {e}")


async def setup(bot):
    await bot.add_cog(riven(bot))
