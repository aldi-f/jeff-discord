from discord.ext import commands
import discord
import json
import time
import re
from redis_manager import cache
from models.wfm import PriceCheck

class arcane(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='arcane', with_app_command=True, description="Shows the matching arcane")
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def arcane(self, ctx,*, arcane:str = None):
        """
        Usage: !arcane <arcane-name>\n
        Shows the closest matching arcane and its market price
        """
        start = time.time()
        if arcane is None:
            error = discord.Embed(
                description="Please provide an arcane."
            )
            await ctx.send(embed=error)
            return

        arcane = arcane.title()
        
        donwload_start = time.time()
        cached = True
        # check if we have data cached
        try:
            cached_arcanes = json.loads(cache.get("arcane:1"))
            wiki_data = cached_arcanes['Arcanes']
        except KeyError:
            error = discord.Embed(
                description="Arcane names could not be pulled from warframe wiki"
            )
            await ctx.send(embed=error)
            return
                
        download_timer = time.time() - donwload_start
        data = None
        for x in wiki_data:
            # print(f"{data['name']} vs {wiki_data[x]['Name']}")
            if arcane in wiki_data[x]['Name']:
                # print('Found mod!!!!!!!!!!!!!!!!!!!!!')
                data = wiki_data[x]
                break

        if data is None:
            error = discord.Embed(
                description="Be sure to type the correct arcane name."
            )
            await ctx.send(embed=error)
            return
        
        market_start = time.time()
        price_check = PriceCheck(item=data.get('Name'))
        price_unranked = price_check.check(rank=0)
        price_ranked = price_check.check(rank=data.get('MaxRank'))
        market_timer = time.time() - market_start
        criteria = ""
        if data['Criteria']:
            criteria = f"{data['Criteria']}:\n"
        stats = f"{criteria}"+re.sub('<br />',chr(10),str(data['Description']))
        arcane_embed = discord.Embed(
            title=f"{data['Name']} | {data['Rarity']}",
            description=f"***At maximum rank ({data['MaxRank']})***\n\n{stats}\n\nUnranked: {price_unranked}\nRank {data['MaxRank']}: {price_ranked}"
        )
        if not cached:
            arcane_embed.set_footer(
                text=f"Total Latency: {round((time.time() - start)*1000)}ms\nDownload Latency: {round(download_timer*1000)}ms\nMarket Price Latency: {round(market_timer*1000)}ms"
            )
        else:
            arcane_embed.set_footer(
                text=f"Total Latency: {round((time.time() - start)*1000)}ms\nCached Latency: {round(download_timer*1000)}ms\nMarket Price Latency: {round(market_timer*1000)}ms"
            )
        await ctx.send(embed=arcane_embed)


async def setup(bot):
    await bot.add_cog(arcane(bot))