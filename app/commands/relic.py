import asyncio
import discord
import json
import logging
import time

from discord.ext import commands

from app.models.wfm import PriceCheck
from app.redis_manager import cache

logger = logging.getLogger(__name__)


class relic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='relic', with_app_command=True, description="Find what parts your relic drops")
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def baro(self, ctx, *, relic: str = None):
        """
        Usage: !relic\n
        Find what parts your relic drops
        """
        if relic is None:
            error = discord.Embed(
                description=f"Please provide a relic to check."
            )
            await ctx.send(embed=error)
            return

        start = time.time()
        relic = relic.title()

        data = json.loads(cache.get("void:1"))['RelicData']
        if relic not in data:
            error = discord.Embed(
                description="This relic doesn't exist! \nCheck if you typed it correctly."
            )
            await ctx.send(embed=error)
        else:
            drop = data[relic]['Drops']

            info = ''
            relic_check = PriceCheck(item=relic+" relic")
            price = await relic_check.check_with_quantity()
            if 'IsBaro' in relic and relic['IsBaro']:
                info = '(B)'
            elif 'Valuted' in relic and relic['Valuted']:
                info = '(V)'

            embed = discord.Embed(
                title=f"{info} {relic}\n",
                color=discord.Colour.random(),
                description=f"Price × Quantity: {price}"
            )

            # download the stuff
            returns = {}
            tasks = []
            for x in range(6):
                returns[x] = {}
                name = drop[x]["Item"] + " " + drop[x]["Part"]
                returns[x]["name"] = name
                price_checker = PriceCheck(item=name)
                task = asyncio.create_task(self.fetch_price(
                    price_checker, "price", returns[x]))
                tasks.append(task)

            await asyncio.gather(*tasks)

            embed.add_field(
                name="Common/Bronze",
                value=f"{returns[0]["name"]} {returns[0]["price"]}\n"
                + f"{returns[1]["name"]} {returns[1]["price"]}\n"
                + f"{returns[2]["name"]} {returns[2]["price"]}", inline=False)
            embed.add_field(
                name="Uncommon/Silver",
                value=f"{returns[3]["name"]} {returns[3]["price"]}\n"
                + f"{returns[4]["name"]} {returns[4]["price"]}", inline=False)
            embed.add_field(
                name="Rare/Gold",
                value=f"{returns[5]["name"]} {returns[5]["price"]}", inline=False)

            embed.set_footer(
                text=f"Latency: {round((time.time() - start)*1000)}ms"
            )
            await ctx.send(embed=embed)

    async def fetch_price(self, price_checker: PriceCheck, key: str | int, returns_dict: dict):
        """Helper method to fetch price for a part and store it in the returns dictionary"""
        try:
            if "forma" in price_checker.slug.lower():
                returns_dict[key] = "(N/A)"
                return
            result = await price_checker.check()
            returns_dict[key] = result
        except Exception as e:
            print(e)
            returns_dict[key] = f"(failed)"


async def setup(bot):
    await bot.add_cog(relic(bot))
