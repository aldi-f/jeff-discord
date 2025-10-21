import os
import asyncio
import json
import logging
import time
import requests
import base64
import re

from openai import OpenAI
import discord
from discord.ext import commands
from pydantic import ValidationError, BaseModel
from warframe_market.client import WarframeMarketClient
from warframe_market.models.item import ItemShortModel
from app.models.wfm import PriceCheck

from Levenshtein import distance

logger = logging.getLogger(__name__)

ROUTER_API_KEY = os.getenv("ROUTER_API_KEY")
if not ROUTER_API_KEY:
    raise ValueError("ROUTER_API_KEY environment variable is not set")


class Items(BaseModel):
    items: list[str]


class ScreenshotScraper:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_prompt(self, image_url: str) -> list:
        image_bytes = requests.get(image_url).content
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        return [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Get me the names of all items here."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                ],
            }
        ]

    def parse_and_validate_json(self, json_string: str) -> Items | None:
        try:
            data = json.loads(json_string)
            return Items(**data)
        except Exception as e:
            print(f"Error parsing JSON string: {e}")
            print("Trying to extract JSON from markdown...")

        try:
            think_pattern = r"([\[\◁]think[\▷\]].*?[\[\◁]\/think[\▷\]])"
            matched = re.search(think_pattern, json_string, re.DOTALL)
            if matched:
                json_string = json_string[matched.end():].strip()

            start = json_string.find("```json") + len("```json")
            end = json_string.find("```", start)
            json_content = json_string[start:end].strip()
            data = json.loads(json_content)
            return Items(**data)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            return None
        except ValidationError as e:
            print(f"Pydantic Validation Error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    async def scrape(self, image_url: str) -> Items | None:
        def blocking_scrape():
            client = OpenAI(api_key=self.api_key, base_url="https://openrouter.ai/api/v1")
            try:
                response = client.chat.completions.parse(
                    model="google/gemini-2.5-flash-lite",
                    messages=self.generate_prompt(image_url),
                    extra_body={"provider": {"require_parameters": True}},
                    response_format=Items,
                    n=1,
                )
                print(f"Response: {response.choices[0].message.content}")
                return self.parse_and_validate_json(response.choices[0].message.content)
            except Exception as e:
                print(f"Error scraping screenshot: {e}")
                return None

        return await asyncio.to_thread(blocking_scrape)
    

class ItemValidator:
    _cached_items = None
    _cached_time = 0
    _CACHE_TTL = 60 * 60 * 2  # 2 hours

    def __init__(self):
        self.client = WarframeMarketClient()

    async def get_all_market_items(self):
        now = time.time()
        if self._cached_items is not None and (now - self._cached_time) < self._CACHE_TTL:
            return self._cached_items
        try:
            self._cached_items = await self.client.get_all_items()
            self._cached_time = now
            return self._cached_items
        except Exception as e:
            print(f"Error fetching items: {e}")
            return None

    async def validate_items(self, items: list[str]) -> list[ItemShortModel]:
        all_items = await self.get_all_market_items()
        valid_items = []
        for item in items:
            item_name = "_".join(item.lower().strip().split(" "))
            closest_match = None
            closest_distance = float("inf")
            for market_item in all_items.data:
                dist = distance(item_name, market_item.slug)
                if dist < closest_distance:
                    closest_distance = dist
                    closest_match = market_item
            if closest_match:
                valid_items.append(closest_match)
        return valid_items

# Cache this market endpoint so we don't hit the API too often
_cached_items = None
_cached_time = 0
_CACHE_TTL = 60 * 60 * 2  # 2 hours

async def get_all_market_items():
    global _cached_items, _cached_time
    now = time.time()
    if _cached_items is not None and (now - _cached_time) < _CACHE_TTL:
        return _cached_items
    client = WarframeMarketClient()
    try:
        _cached_items = await client.get_all_items()
        _cached_time = now
        return _cached_items
    except Exception as e:
        print(f"Error fetching items: {e}")
        return None
    


class PriceCheckCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scraper = ScreenshotScraper(api_key=ROUTER_API_KEY)
        self.validator = ItemValidator()

    @commands.command(name="pricecheck", aliases=["check", "pc"])
    async def check(self, ctx: commands.Context):
        if not ctx.message.attachments:
            error = discord.Embed(description="Provide a screenshot of your inventory to use this command")
            await ctx.send(embed=error)
            return

        valid_attachments = []
        for attachment in ctx.message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image"):
                valid_attachments.append(attachment)

        if len(valid_attachments) == 0:
            error = discord.Embed(description="Provide a valid image file")
            await ctx.send(embed=error)
            return

        async with ctx.typing():
            start = time.time()
            valid_items: list[ItemShortModel] = []
            seen_slugs = set()
            for attachment in valid_attachments:
                image_url = attachment.url
                scrape = await self.scraper.scrape(image_url)
                if scrape is None:
                    continue

                items = await self.validator.validate_items(scrape.items)
                for item in items:
                    if item.slug not in seen_slugs:
                        valid_items.append(item)
                        seen_slugs.add(item.slug)

            if len(valid_items) == 0:
                error = discord.Embed(description="No valid items found in the screenshots.")
                await ctx.send(embed=error)
                return
                

            embed = discord.Embed(title="Price Check", color=discord.Color.blue())
            message = await ctx.send(f"Found {len(valid_items)} items. Doing Price checks...")
            items_with_price = []
            for i, item in enumerate(valid_items):
                try:
                    price_check = PriceCheck(item=item.slug)
                    price_list = await price_check.check_raw()

                    items_with_price.append((item, price_list))
                except Exception as e:
                    logger.error(f"Error checking price for {item.i18n['en'].name}: {e}")
                if (i + 1) % 3 == 0:
                    await asyncio.sleep(1)
                    await message.edit(content=f"Found {len(valid_items)} items. Doing Price checks... ({i + 1}/{len(valid_items)})")

            # sort in this order:
            # most expensive first (first element of list),
            # most expensive average of all elements of the list
            items_with_price.sort(key=lambda x: (x[1][0] if len(x[1]) != 0 else 0,
                                                sum(x[1]) / len(x[1]) if len(x[1]) != 0 else 0
                                                ), reverse=True)
            item_text = f"Found {len(valid_items)} items in the screenshot:\n"
            for item, prices in items_with_price:
                price_text = PriceCheck.format_output(prices)
                item_text += f"- {item.i18n['en'].name}: {price_text}\n"

            embed.description = item_text
            embed.set_footer(text=f"Processed in {int(time.time() - start)} seconds")
            await message.edit(content="", embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(PriceCheckCog(bot))
