import discord
import json
import logging
import time

from discord.ext import commands
from Levenshtein import distance

from funcs import dispo, update_cache
from redis_manager import cache

logger = logging.getLogger(__name__)


class weapon(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def get_weapon(self, ctx: commands.Context, message: str):
        start = time.time()
        if message is None:
            error = discord.Embed(description="Usage: !weapon <weapon-name>")
            await ctx.send(embed=error)
            return
        download_start = time.time()

        # check if we have data cached
        cached = True
        if cache.cache.exists("weapon:1"):
            cached_weapons = json.loads(cache.cache.get("weapon:1"))
            data = cached_weapons
        else:
            cached = False
            update_cache("weapon:1", cache)
            cached_weapons = json.loads(cache.cache.get("weapon:1"))
            data = cached_weapons

        download_timer = time.time() - download_start

        wiki_data = data
        snekw = ""
        # first we test if we have weapon on wiki
        message = message.lower()
        wiki_wep = ""
        # test with full text first
        for x in wiki_data:
            if message == x.lower():
                wiki_wep = x
                break

        # if not full word then partial
        if wiki_wep == "":
            for x in wiki_data:
                if message in x.lower():
                    wiki_wep = x
                    break

        if len(wiki_wep) == 0:
            error = discord.Embed(
                description="Be sure to write the right weapon name")
            await ctx.send(embed=error)
            return
        snekw = wiki_data[wiki_wep]

        calculaton_start = time.time()
        if len(snekw) == 0:
            error = discord.Embed(
                description="Be sure to write the right weapon name")
            await ctx.send(embed=error)
            return
        description = ''
        if snekw['Slot'] != 'Melee':
            description += (f"Class: {snekw['Slot']}\n" +
                            f"Type: {snekw['Class']}\n" +
                            f"Mastery: {snekw.get('Mastery', '-')}\n" +
                            f"Ammo: {snekw['AmmoMax'] if 'AmmoMax' in snekw else '∞'}\n" +
                            f"Ammo Pickup: {snekw['AmmoPickup'] if 'AmmoPickup' in snekw else ''}{chr(10) if 'AmmoPickup' in snekw else ''}" +
                            f"Magazine: {snekw['Magazine']}\n" +
                            f"Reload: {snekw['Reload']}\n" +
                            f"Trigger: {snekw['Trigger']}\n"
                            # f"{'**Zoom**:'+\n+ chr(10).join([str(zoom_option) for zoom_option in snekw['Zoom']]) if 'Zoom' in snekw else ''}\n"
                            )

            if 'Zoom' in snekw:
                description += '**Zoom**:\n'
                description += '\n'.join([str(zoom_option)
                                         for zoom_option in snekw['Zoom']])
                description += '\n'

            description += f"Disposition: {snekw['Disposition']}  ({dispo(float(snekw['Disposition']))})\n\n"
        else:
            description += (f"Class: {snekw['Slot']}\n" +
                            f"Type: {snekw['Class']}\n" +
                            f"Mastery: {snekw.get('Mastery', '-')}\n" +
                            f"Attack Speed: {snekw['Attacks'][0]['FireRate']}\n" +
                            f"Combo Duration: {snekw.get("ComboDur", "∞")}\n" +
                            f"Range: {snekw['MeleeRange']}\n" +
                            f"Disposition: {snekw['Disposition']}  ({dispo(float(snekw['Disposition']))})\n\n"
                            )

        wepembed = discord.Embed(
            title=snekw['Name'],
            description=description,
            url=f"https://warframe.fandom.com/wiki/{'_'.join(snekw['Name'].split(' '))}",
            color=discord.Colour.random())

        for x in snekw['Attacks']:
            total = 0
            max = ''
            percentmax = 0
            damagestring = ''
            damage = x['Damage']
            for type in damage:
                damagestring += f"{type.capitalize()}: {damage[type]}\n"
                total += damage[type]
                if damage[type] >= percentmax:
                    percentmax = damage[type]
                    max = type.capitalize()

            if snekw['Slot'] != 'Melee':
                wepembed.add_field(
                    name=f"***Attack Mode***: {x['AttackName'] if 'AttackName' in x else 'Normal Attack'}\n" +
                    f"Type: {x['ShotType'] if 'ShotType' in x else '-'}",
                    value=f"{'Critical Chance: '+str(round(x['CritChance']*100))+'%'+chr(10) if 'CritChance' in x else ''}" +
                    f"{'Critical Damage: ' + str(x['CritMultiplier'])+'x'+chr(10) if 'CritMultiplier' in x else ''}" +
                    f"{'Status Chance: ' + str(round(x['StatusChance']*100))+'%'+chr(10) if 'StatusChance' in x else ''}" +
                    f"Multishot: {x['Multishot'] if 'Multishot' in x else '1'}\n" +
                    f"{'Charge Time: ' + str(x['FireRate'])+'s'+chr(10) if 'ShotType' in x and x['ShotType'] == 'Charged Shot' else 'Firerate: '+str(x['FireRate'])+chr(10) if 'FireRate' in x else ''}" +
                    f"{'AoE Radius: '+str(x['Radius'])+'m'+chr(10) if 'Radius' in x and 'ShotType' in x and x['ShotType'] == 'AoE' else 'AoE Radius: '+str(x['Falloff']['EndRange'])+'m'+chr(10) if 'Falloff' in x and 'ShotType' in x and x['ShotType'] == 'AoE' else ''}" +
                    f"{'Falloff: '+(str(round(x['Falloff']['Reduction'] * 100))+'%' if 'Reduction' in x['Falloff'] else '')+'('+str(x['Falloff']['StartRange'])+' - '+str(x['Falloff']['EndRange'])+'m)'+chr(10) if 'Falloff' in x else ''}" +
                    f"{'Punchthrough: '+str(x['PunchThrough'])+chr(10) if 'PunchThrough' in x else ''}" +
                    f"**Damage**:\n" +
                    damagestring + chr(10) +
                    f"{'Total: '+'{0:.2f} ({1:.2f}%{2})'.format(total * x.get('Multishot', 1), percentmax*100/total, max)}",
                    inline=True
                )
            else:
                wepembed.add_field(
                    name=f"***Attack Mode***: {x['AttackName'] if 'AttackName' in x else 'Normal Attack'}\n" +
                    f"{'Type: '+x['ShotType'] if 'ShotType' in x else ''}",
                    value=f"{'Critical Chance: '+str(round(x['CritChance']*100))+'%'+chr(10) if 'CritChance' in x else ''}" +
                    f"{'Critical Damage: ' + str(x['CritMultiplier'])+'x'+chr(10) if 'CritMultiplier' in x else ''}" +
                    f"{'Status Chance: ' + str(round(x['StatusChance']*100))+'%'+chr(10) if 'StatusChance' in x else ''}" +
                    multishot(x) +
                    # f"{ '' if 'Multishot' not in x else 'Multishot: '+str(x['Multishot'])+chr(10)}"+
                    # f"{'Charge Time: '+ x['ChargeTime']+'\n' if 'ChargeTime' in x and 'AttackName' not in x else 'Firerate: '+x['FireRate']+'\n' if 'FireRate' in x else ''}"+
                    f"{'AoE Radius: '+str(x['Radius'])+'m'+chr(10) if 'Radius' in x and 'ShotType' in x and x['ShotType'] == 'AoE' else 'AoE Radius: '+str(x['Falloff']['EndRange'])+'m'+chr(10) if 'Falloff' in x else ''}" +
                    f"{'Falloff: '+str(round(x['Falloff']['Reduction']) * 100)+'%('+str(x['Falloff']['StartRange'])+' - '+str(x['Falloff']['EndRange'])+'m'+chr(10) if 'Falloff' in x else ''}" +
                    # f"{'Punchthrough: '+x['PunchThrough']+'\n' if 'PunchThrough' in x else ''}"+
                    f"**Damage**:\n" +
                    damagestring + chr(10) +
                    f"{'Total: '+'{0:.2f} ({1:.2f}%{2})'.format(total * x.get('Multishot', 1), percentmax*100/total, max)}",
                    inline=True
                )
        calculaton_timer = time.time() - calculaton_start
        if cached:
            wepembed.set_footer(
                text=f"Total Latency: {round((time.time() - start)*1000)}ms\nCached Latency: {round(download_timer*1000)}ms\nCalculation Latency: {round(calculaton_timer*1000)}ms"
            )
        else:
            wepembed.set_footer(
                text=f"Total Latency: {round((time.time() - start)*1000)}ms\nDownload Latency: {round(download_timer*1000)}ms\nCalculation Latency: {round(calculaton_timer*1000)}ms"
            )
        await ctx.send(embed=wepembed)

    @commands.command(name='wep', description="Find the stats of certain weapon", aliases=['w', 'weap', "weapon"])
    async def weapon_alt(self, ctx, *, message: str = None):
        """
        Usage: -weapon <weapon-name>\n
        Find the stats of certain weapon
        """
        await self.get_weapon(ctx, message)

    async def autocomplete(self, interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
        if not cache.cache.exists("weapon:1"):
            update_cache("weapon:1", cache)

        data: dict = json.loads(cache.cache.get("weapon:1"))

        current = current.lower()

        weapon_distances = [
            (
                weapon,  # For alphabetical sorting
                # For Levenshtein distance sorting
                distance(current, weapon.lower()),
                0 if weapon.lower().startswith(current) else 1  # For prefix sorting
            )
            for weapon in data.keys()
        ]
        # Sort by distance first, then by prefix, then alphabetically
        weapon_distances.sort(key=lambda x: (x[1], x[2]. x[0]))

        return [discord.app_commands.Choice(name=weapon, value=weapon) for weapon, *_ in weapon_distances[:24]]

    @discord.app_commands.command(name='weapon', description="Find the stats of certain weapon")
    @discord.app_commands.autocomplete(weapon=autocomplete)
    async def weapon_slash(self, interaction: discord.Interaction, weapon: str = None):
        """
        Usage: /weapon <weapon-name>\n
        Find the stats of certain weapon
        """
        ctx = await self.bot.get_context(interaction)
        await self.get_weapon(ctx, weapon)


async def setup(bot):
    await bot.add_cog(weapon(bot))


def multishot(x):
    if 'Multishot' in x:
        return f"Multishot: {x['Multishot']}\n"
    else:
        return ''
