import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

token = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='--', intents=intents, help_command=None)

async def load():
    for file in os.listdir('./commands'):
        if file.endswith('.py'):
            await bot.load_extension(f'commands.{file[:-3]}') 

@bot.tree.command(name="sync")
async def func(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id == 336563297648246785:
        try:
            await bot.tree.sync()
            await interaction.followup.send("Done.", ephemeral=True)
        except: 
            await interaction.followup.send("Something went wrong!", ephemeral=True)
    else:
        file = discord.File("silicate.jpg")
        logging.info(f"Sync command used by {interaction.user}")
        await interaction.followup.send("blehhhh",file=file, ephemeral=True)

@bot.event
async def on_ready():
    await load()
    # await bot.tree.sync()


bot.run(token)
