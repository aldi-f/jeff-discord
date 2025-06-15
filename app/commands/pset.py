import asyncio
import discord
import json
import logging
import time

from discord.ext import commands

from models.wfm import PriceCheck
from redis_manager import cache
from warframe_market.common import Subtype

logger = logging.getLogger(__name__)


class pset(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="pset", with_app_command=True)
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def ping(self, ctx, *, prime_set=None):
        start = time.time()
        if prime_set is None:
            error = discord.Embed(
                description="Be sure to provide a prime name"
            )
            await ctx.send(embed=error)
            return
        elif 'forma' in prime_set.lower():
            error = discord.Embed(
                description="Why would you search forma"
            )
            await ctx.send(embed=error)
            return

        download_start = time.time()

        primes = json.loads(cache.get("void:1"))['PrimeData']
        item_name = prime_set.lower()
        text = ''
        item = ''
        prime_dict = None
        # get the prime dict
        for prime in primes:
            if "Prime" not in prime:
                continue
            prime_name = prime.lower()
            if item_name in prime_name:
                prime_dict = primes[prime]
                item = prime

        if not prime_dict:
            error = discord.Embed(
                description="Did not find any primes with that name"
            )
            await ctx.send(embed=error)
            return

        try:
            set_name = f"{item} set"
            set_price_checker = PriceCheck(item=set_name)
            pieces = await set_price_checker.get_set_pieces()
        except Exception as e:  # try again without set suffix
            set_price_checker = PriceCheck(item=item)
            pieces = await set_price_checker.get_set_pieces()

        returns = {}
        await asyncio.gather(*[self.fetch_price(PriceCheck(item=data["slug"]), piece, returns) for piece, data in pieces.items()])

        # pop out the set price by checking the data
        set_piece = next(x for x in pieces.items() if x[1]["set"])
        set_part = pieces.pop(set_piece[0])

        for part, data in pieces.items():
            # Only keep part name
            part_name = part.replace(item, "").strip()
            quantity = data["quantity"]
            text += f"{quantity}× {part_name}: {returns[part]}\n"

        set_price = f"Full set: {returns[set_piece[0]]}"

        download_timer = time.time() - download_start

        set_embed = discord.Embed(
            description=set_price+"\n\n"+text,
            title=item
        )

        set_embed.set_footer(
            text=f"Total Latency: {round((time.time() - start)*1000)}ms\nDownload Latency: {round(download_timer*1000)}ms\n"
        )

        await ctx.send(embed=set_embed)

    async def fetch_price(self, price_checker: PriceCheck, part_key: str, returns_dict: dict):
        """Helper method to fetch price for a part and store it in the returns dictionary"""
        try:
            result = await price_checker.check(subtype=Subtype.BLUEPRINT)
            returns_dict[part_key] = result
        except Exception as e:
            print(e)
            returns_dict[part_key] = f"(failed)"


async def setup(bot):
    await bot.add_cog(pset(bot))
