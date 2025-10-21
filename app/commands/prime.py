import discord
import json
import logging
import time

from discord.ext import commands

from app.funcs import update_cache
from app.models.wfm import PriceCheck
from app.redis_manager import cache

logger = logging.getLogger(__name__)


class prime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='prime', with_app_command=True, description="Find what relics drop certain part.")
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def sortie(self, ctx, *, part: str = None):
        """
        Usage: !prime <prime-part-name>\n

        Find what relics drop certain part.
        """
        start = time.time()
        if part is None:
            error = discord.Embed(
                description="Be sure to provide a prime part name"
            )
            await ctx.send(embed=error)
            return
        elif 'forma' in part:
            error = discord.Embed(
                description="Forma is not implemented for now"
            )
            await ctx.send(embed=error)
            return

        download_start = time.time()
        # check if we have data cached
        cached = True
        if cache.cache.exists("void:1"):
            cached_void = json.loads(cache.cache.get("void:1"))
            data = cached_void
        else:
            cached = False
            update_cache("void:1", cache)
            cached_void = json.loads(cache.cache.get("void:1"))
            data = cached_void

        download_timer = time.time() - download_start
        calculation_start = time.time()
        primes = data['PrimeData']
        relics = data['RelicData']
        text = ''
        item = ''
        price_name = ''
        # testing_needed = False

        part = part.lower().replace("bp", "blueprint").split(" ")

        if len(part) == 2:
            item_name, part_name = part
        elif len(part) == 3:
            item_name, part_name = " ".join(part[:2]), "".join(part[2:])
        else:
            item_name, part_name = " ".join(part[:2]), " ".join(part[2:])

        prime_dict = None
        # get the prime dict
        for prime in primes:
            if "Prime" not in prime:
                continue
            prime_name = prime.lower()
            if item_name in prime_name:
                prime_dict = primes[prime]
                item = prime
                price_name = prime

        # if we didnt not find the correct key, check again by changing item_name
        if not prime_dict and len(part) == 3:
            item_name, part_name = "".join(part[0]), " ".join(part[1:])
            for prime in primes:
                if "Prime" not in prime:
                    continue
                prime_name = prime.lower()
                if item_name in prime_name:
                    prime_dict = primes[prime]
                    item = prime
                    price_name = prime

                    break

        # still no key? then no part found
        if not prime_dict:
            error = discord.Embed(
                description="Did not find the prime item!"
            )
            await ctx.send(embed=error)
            return

        # parse the part we want
        part_dict = None
        for part in prime_dict["Parts"]:
            partt = part.lower()
            if len(partt.split(" ")) > 1:
                partt = partt.replace("blueprint", "").strip()
            if part_name in partt.lower():
                part_dict = prime_dict["Parts"][part]
                item += f" {part}"
                price_name = f"{price_name} {part if len(part.split(' ')) == 1 else part.replace('blueprint', '').strip()}"
                break

        if not part_dict:
            error = discord.Embed(
                description=f"Did not find the part for {item}!"
            )
            await ctx.send(embed=error)
            return

        for relic in part_dict["Drops"]:
            data_dict = relics[relic]
            rarity = part_dict["Drops"][relic]
            info = ""
            if 'IsBaro' in data_dict and data_dict['IsBaro']:
                info = '(B)'
            elif 'Vaulted' in data_dict:
                info = '(V)'
            text += f"`{info:3} {relic} - {rarity}`\n"

        # part price
        price = f"Market price: "
        try:
            price_checker = PriceCheck(item=price_name)
            price += f"{await price_checker.check()}"
        except Exception as e:
            print(f"Error fetching price for {price_name}: {e}")
            price += "(failed)"

        prime_part = discord.Embed(
            description=price + "\n\n" + text,
            title=item,
        )
        calculaton_timer = time.time() - calculation_start

        if cached:
            prime_part.set_footer(
                text=f"Total Latency: {round((time.time() - start)*1000)}ms\nCached Latency: {round(download_timer*1000)}ms\nCalculation Latency: {round(calculaton_timer*1000)}ms"
            )
        else:
            prime_part.set_footer(
                text=f"Total Latency: {round((time.time() - start)*1000)}ms\nDownload Latency: {round(download_timer*1000)}ms\nCalculation Latency: {round(calculaton_timer*1000)}ms"
            )

        await ctx.send(embed=prime_part)


async def setup(bot):
    await bot.add_cog(prime(bot))
