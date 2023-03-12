from discord.ext import commands
from discord import app_commands
import discord
import json
import time
from requests import get
from redis_manager import cache
import datetime
# from logging import info as print

class prime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='prime', with_app_command=True, description="Find what relics drop certain part.")
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def sortie(self, ctx,* ,part:str = None):
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
        # metadata = get('https://wf.snekw.com/void-wiki/meta').json()
        
        cached = True
        # check if we have data cached
        if cache.cache.exists("void:1"):
            cached_void = json.loads(cache.cache.get("void:1"))
            data = cached_void
        else:
            cached = False # recreate it later
            res = get('https://wf.snekw.com/void-wiki')
            data = json.loads(res.text)
            
        download_timer = time.time() - download_start
        calculation_start = time.time()
        primes = data['data']['PrimeData']
        relics = data['data']['RelicData']
        text = ''
        item = ''
        
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
                partt = partt.replace("blueprint","").strip()
            if part_name in partt.lower():
                part_dict = prime_dict["Parts"][part]
                item += f" {part}"
                break      
        
        if not part_dict:
            error = discord.Embed(
                description=f"Did not find the part for {prime}!"
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
            text +=f"`{info:3} {relic} - {rarity}`{chr(10)}"
                
        

        prime_part = discord.Embed(
            description=text,
            title=item,
        )
        calculaton_timer= time.time() - calculation_start
        
        if cached:
            prime_part.set_footer(
                text=f"Total Latency: {round((time.time() - start)*1000)}ms{chr(10)}Cached Latency: {round(download_timer*1000)}ms{chr(10)}Calculation Latency: {round(calculaton_timer*1000)}ms"
            )
        else:
            prime_part.set_footer(
                text=f"Total Latency: {round((time.time() - start)*1000)}ms{chr(10)}Download Latency: {round(download_timer*1000)}ms{chr(10)}Calculation Latency: {round(calculaton_timer*1000)}ms"
            )       
            
        await ctx.send(embed=prime_part)
        
        # if not cached:
        #     print("Adding data to redis")
        #     text = json.dumps(data)
        #     # print(data["meta"])
        #     cache.cache.set("void:1",text, ex=datetime.timedelta(days=1))



async def setup(bot):
    await bot.add_cog(prime(bot))