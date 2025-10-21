import logging

from discord.ext import commands
from app.redis_manager import cache
logger = logging.getLogger(__name__)


class ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", with_app_command=True)
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def ping(self, ctx: commands.Context):
        cache.cache.ping()
        await ctx.send("Pong")


async def setup(bot):
    await bot.add_cog(ping(bot))
