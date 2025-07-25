import os
import asyncio
import json
import logging
import time
from cachetools.func import ttl_cache
import requests
import base64
import re

from openai import OpenAI
import discord
from discord.ext import commands
from pydantic import ValidationError, BaseModel
from warframe_market.client import WarframeMarketClient
from warframe_market.models.item import ItemShortModel
from models.wfm import PriceCheck

from Levenshtein import distance


logger = logging.getLogger(__name__)

ROUTER_API_KEY = os.getenv("ROUTER_API_KEY")
if not ROUTER_API_KEY:
    raise ValueError("ROUTER_API_KEY environment variable is not set")


class PrimePart(BaseModel):
    name: str
    # quantity: int


class PrimeParts(BaseModel):
    items: list[PrimePart]


def generate_prompt(image_url: str) -> list:
    """Generates a prompt for the AI model to extract prime item names from an image."""
    example_json = str(
        {
            "items": [
                {"name": "Equinox Prime Systems Blueprint"},
                {"name": "Mesa Prime Blueprint"},
                {"name": "Boltor Prime Receiver"},
            ]
        }
    )
    image_bytes = requests.get(image_url).content
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Get me the names of all prime items here. Output the result as json format. Example: {example_json}. Only write the json file and nothing else",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                },
            ],
        }
    ]


def parse_and_validate_json(json_string: str) -> PrimeParts | None:

    # Test out if string itself is a valid json
    try:
        data = json.loads(json_string)
        validated_data = PrimeParts(**data)
        return validated_data
    except Exception as e:
        print(f"Error parsing JSON string: {e}")
        print("Trying to extract JSON from markdown...")

    try:

        # Remove thinking output if present

        think_pattern = r"([\[\◁]think[\▷\]].*?[\[\◁]\/think[\▷\]])"

        matched = re.search(think_pattern, json_string, re.DOTALL)
        if matched:
            json_string = json_string[matched.end() :].strip()

        # Use regex to find the JSON part within the string
        start = json_string.find("```json") + len("```json")
        end = json_string.find("```", start)

        json_content = json_string[start:end].strip()

        data = json.loads(json_content)

        # Validate the dictionary against the Pydantic model
        validated_data = PrimeParts(**data)

        return validated_data

    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return None
    except ValidationError as e:
        print(f"Pydantic Validation Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


async def scrape_screenshot(image_url: str) -> PrimeParts | None:

    def blocking_scrape():
        client = OpenAI(api_key=ROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
        try:
            response = client.chat.completions.parse(
                model="google/gemini-2.0-flash-001",
                messages=generate_prompt(image_url),
                extra_body={
                    "provider": {
                        "require_parameters": True,
                    }
                },
                response_format=PrimeParts,
                n=1,
            )
            print(f"Response: {response.choices[0].message.content}")
            validated_data = parse_and_validate_json(
                response.choices[0].message.content
            )
            if validated_data is None:
                print("Failed to parse or validate JSON response.")
                return None
            return validated_data
        except Exception as e:
            print(f"Error scraping screenshot: {e}")
            return None

    return await asyncio.to_thread(blocking_scrape)


@ttl_cache(ttl=60 * 60 * 2)  # Cache for 2 hour
async def get_all_market_items():
    """Fetches all items from the Warframe Market API."""
    client = WarframeMarketClient()
    try:
        return await client.get_all_items()
    except Exception as e:
        print(f"Error fetching items: {e}")
        return None


async def validate_items(items: list[PrimePart]) -> list[dict]:
    """Validates the items against the Warframe Market API."""
    all_items = await get_all_market_items()

    valid_items = []
    for item in items:
        item_name = "_".join(item.name.lower().strip().split(" "))

        closest_match = None
        closest_distance = float("inf")

        for market_item in all_items.data:
            dist = distance(item_name, market_item.slug)
            if dist < closest_distance:
                closest_distance = dist
                closest_match = market_item

        if closest_match:
            valid_items.append(
                {
                    "object": closest_match,
                    # "quantity": item.quantity
                }
            )

    return valid_items


class pricecheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pricecheck", aliases=["check", "pc"])
    async def check(self, ctx: commands.Context):
        if not ctx.message.attachments:
            error = discord.Embed(
                description="Provide a screenshot of your inventory to use this command"
            )
            await ctx.send(embed=error)
            return

        attachment = ctx.message.attachments[0]

        if not attachment.content_type.startswith("image"):
            error = discord.Embed(description="Provide a valid image file")
            await ctx.send(embed=error)
            return

        async with ctx.typing():
            start = time.time()
            image_url = ctx.message.attachments[0].url

            scrape = await scrape_screenshot(image_url)
            if scrape is None:
                error = discord.Embed(description="Failed to scrape the screenshot.")
                await ctx.send(embed=error)

            items = await validate_items(scrape.items)
            if not items:
                error = discord.Embed(
                    description="No valid items found in the screenshot."
                )
                await ctx.send(embed=error)
                return

            embed = discord.Embed(title="Price Check", color=discord.Color.blue())

            item_text = f"Found {len(items)} items in the screenshot:\n"
            message = await ctx.send(f"Found {len(items)} items. Doing Price checks...")
            for i, item in enumerate(items):
                item_short: ItemShortModel = item["object"]
                # quantity: int = item["quantity"]

                try:
                    price_check = PriceCheck(item=item_short.slug)
                    price_text = await price_check.check()
                    item_text += f"- {item_short.i18n['en'].name}: {price_text}\n"

                except Exception as e:
                    logger.error(
                        f"Error checking price for {item_short.i18n['en'].name}: {e}"
                    )
                    item_text += f"- {item_short.slug}: Error fetching price\n"

                if (i + 1) % 3 == 0:
                    await asyncio.sleep(1)  # Rate limit to avoid hitting API too fast
                    await message.edit(
                        content=f"Found {len(items)} items. Doing Price checks... ({i + 1}/{len(items)})"
                    )

            embed.description = item_text
            embed.set_footer(text=f"Processed in {int(time.time() - start)} seconds")
            await message.edit(content="", embed=embed)


async def setup(bot):
    await bot.add_cog(pricecheck(bot))
