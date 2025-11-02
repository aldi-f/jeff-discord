import discord
import logging
import time

from discord.ext import commands

from app.api.worldstate import worldstate_client

logger = logging.getLogger(__name__)


class BaroView(discord.ui.View):
    def __init__(self, embeds: list[discord.Embed], timeout: int = 180):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.message = None

        # Disable buttons if only one page
        if len(self.embeds) <= 1:
            self.previous_button.disabled = True
            self.next_button.disabled = True
        else:
            self.previous_button.disabled = True

    def update_buttons(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.embeds) - 1

    @discord.ui.button(label="◀", style=discord.ButtonStyle.primary)
    async def previous_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page], view=self
            )

    @discord.ui.button(label="▶", style=discord.ButtonStyle.primary)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page], view=self
            )


class Baro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="baro",
        with_app_command=True,
        description="Show current baro status and his inventory",
    )
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def baro(self, ctx):
        """
        Usage: -baro\n
        Show current baro status and his inventory
        """
        start = time.time()

        worldstate = await worldstate_client.get_worldstate()
        baro_data = worldstate.void_traders[0]

        items_per_page = 15  # discord limit
        manifest = baro_data.manifest
        total_items = len(manifest)
        total_pages = (total_items + items_per_page - 1) // items_per_page

        embeds = []
        for page in range(total_pages):
            start_idx = page * items_per_page
            end_idx = min(start_idx + items_per_page, total_items)

            embed = discord.Embed(
                title="Baro Ki'Teer",
                description=f"Location: {baro_data.node}\nLeaving: <t:{int(baro_data.expiry.timestamp())}:R>",
            )

            for item in manifest[start_idx:end_idx]:
                embed.add_field(
                    name=item.item_type,
                    value=f"{item.ducats}<:Ducat:967433339868950638> | {item.credits}<:Credits:967435392427106348>",
                    inline=False,
                )

            embed.set_footer(
                text=f"Page {page + 1}/{total_pages} | Latency: {round((time.time() - start) * 1000)}ms"
            )
            embeds.append(embed)

        if len(embeds) == 1:
            await ctx.send(embed=embeds[0])
        else:
            view = BaroView(embeds)
            await ctx.send(embed=embeds[0], view=view)


async def setup(bot):
    await bot.add_cog(Baro(bot))
