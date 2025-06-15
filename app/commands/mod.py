import discord
import json
import logging
import time

from discord.ext import commands
from requests import get

from funcs import polarity, update_cache
from models.wfm import PriceCheck
from redis_manager import cache

logger = logging.getLogger(__name__)


class mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='mod', with_app_command=True, description="Shows the closest matching mod")
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def mod(self, ctx, *, mod: str = None):
        """
        Usage: !mod <mod-name>\n
        Shows the closest matching mod and its market price
        """
        start = time.time()
        if mod is None:
            error = discord.Embed(
                description="Please provide a mod."
            )
            await ctx.send(embed=error)
            return

        download_start = time.time()
        response = get(f"https://api.warframestat.us/mods/{mod}")
        download_timer = time.time() - download_start
        data = json.loads(response.text)

        if 'code' in data and data['code'] == 404:
            error = discord.Embed(
                description="Be sure to type the correct mod name"
            )
            await ctx.send(embed=error)
            return
        else:
            download_start = time.time()
            # check if we have data cached
            if cache.cache.exists("mod:1"):
                cached = True
                cached_mods = json.loads(cache.cache.get("mod:1"))
                snekw = cached_mods['Mods']
            else:
                cached = False
                update_cache("mod:1", cache)
                cached_mods = json.loads(cache.cache.get("mod:1"))
                snekw = cached_mods['Mods']

            download_timer += time.time() - download_start
            snekw_mod = None
            for x in snekw:
                if data['name'].lower() == snekw[x]['Name'].lower():
                    snekw_mod = snekw[x]
                    break

            if snekw_mod is None:
                await ctx.send("Internal Error!")
                return

            price_ranked = ''
            price_unranked = ''
            market_start = time.time()
            if snekw_mod['Tradable']:
                try:
                    price_checker = PriceCheck(item=snekw_mod['Name'])
                    price_ranked = await price_checker.check(rank=int(snekw_mod['MaxRank']))
                    price_unranked = await price_checker.check(rank=0)
                except Exception as e:
                    print(
                        f"Error fetching market price for {snekw_mod['Name']}: {e}")
                    price_ranked = "(failed)"
                    price_unranked = "(failed)"

            market_timer = time.time() - market_start

            price_text = f"{('**Unranked: **'+str(price_unranked)+'\n**Maxed: **'+str(price_ranked)) if snekw_mod['Tradable'] else ''}"

            embed = discord.Embed(color=discord.Colour.random())

            if 'wikiaThumbnail' in data:
                # For mods with thumbnail
                embed.description = price_text
                embed.set_image(url=data['wikiaThumbnail'])
            else:
                # For mods without thumbnail
                pol = ''
                if 'Polarity' in snekw_mod:
                    pol = polarity(snekw_mod['Polarity'])

                embed.title = f"{snekw_mod['Name']}{pol} ({data['rarity']})\n{snekw_mod['Type']} Mod"
                embed.description = (f"Drain cost: {snekw_mod['BaseDrain']} - {snekw_mod['BaseDrain'] + snekw_mod['MaxRank']} (Ranks 0 - {snekw_mod['MaxRank']})"
                                     + '\n\n' +
                                     f"**Effect at rank {snekw_mod['MaxRank']}:**" +
                                     '\n'+snekw_mod['Description']
                                     + '\n\n'+price_text)

            # Set footer based on cached status
            transmutable_text = f"{'Transmutable' if 'Transmutable' in snekw_mod else 'Not transmutable'}"
            latency_type = "Cached Latency" if cached else "Download Latency"
            footer_text = (f"{transmutable_text}\n\n"
                           f"Total Latency: {round((time.time() - start)*1000)}ms\n"
                           f"{latency_type}: {round(download_timer*1000)}ms\n"
                           f"Market Price Latency: {round(market_timer*1000)}ms")

            embed.set_footer(text=footer_text)
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(mod(bot))
