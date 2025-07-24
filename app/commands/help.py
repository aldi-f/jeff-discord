from discord.ext import commands
import discord


class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='help',  with_app_command=True, description="Lists all commands")
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def help(self, ctx):
        """
        Usage: -help
        """
        initial_text = "Flags:\n" +\
            "- **[ALPHA]**: Commands may work but data will not be complete (e.g. Unique names are not parsed)\n" +\
            "- **[BETA]**: Commands will work but they are not finalized yet (e.g. Discord embed is not finalized)\n" +\
            "- **[BROKEN]**: Due to updates on endpoints (wiki, warframe-status, worldstate), code rework is required\n" +\
            "\n\n"
        cog_desc = initial_text +\
            "**-arcane** <arcane-name>: Shows arcane stats and market price\n\n" +\
            "**-archon** (optional)<language>: Shows current archon rotation\n\n" +\
            "**[ALPHA]-baro**: Show current baro status and his inventory\n\n" +\
            "**[BETA]-bounty <place>**: Data about currently running bounties on <place>\n\n" +\
            "**[BETA]-calendar**: 1999 Calendar\n\n" +\
            "**-circuit**: List the current rotation of incarnon genesis\n\n" +\
            "**-coda**: Current Coda rotation\n\n" +\
            "**-darvo**: Daily Darvo deal\n\n" +\
            "**-duviri**: Current Duviri rotation\n\n" +\
            "**-fissure** (optional)<rj|sp>: Shows the current fissures\n\n" +\
            "**-mod** <mod-name>: Shows the mod stats and market price\n\n" +\
            "**-nightwave**: Shows current nightwave quests\n\n" +\
            "**-pricecheck**: Scan an image for prime parts and their price\n\n" +\
            "**-prime** <prime-part>: Finds market price and what drops it\n\n" +\
            "**[ALPHA]-profile** <ingame-name>: Get warframe user profile stats\n\n" +\
            "**-pset** <prime-name>: Finds market prices for all parts\n\n" +\
            "**-relic** <relic-name>: Lists all parts dropping from a relic and their market prices\n\n" +\
            "**-riven** <weapon-name>: Shows matching riven prices\n\n" +\
            "**-sortie** (optional)<language>: Shows daily sortie\n\n" +\
            "**-weapon** <weapon-name>: Shows weapon stats\n\n"

        # "**-arbie**: Data about current arbitration\n\n" +\
        # "**-events**: List the currently running events\n\n"+\
        # "**-eda**: Get the currently running Elite Deep Archimedea\n"+\
        embed = discord.Embed(
            title="Commands",
            description=cog_desc
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(help(bot))
