import hashlib
import json
import logging
import requests
import time

from discord.ext import commands, tasks

from funcs import WIKI_URL_BASE, WIKI_MODULE_BODY, WFCD, CHECKSUMS, unserialize_lua_table
from redis_manager import cache

logger = logging.getLogger(__name__)


class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.refill_wiki_data.start()
        self.refill_github_data.start()

    def cog_unload(self):
        self.refill_wiki_data.cancel()
        self.refill_github_data.cancel()

    @tasks.loop(hours=1)
    async def refill_wiki_data(self):
        for key, params in WIKI_MODULE_BODY.items():
            ready = False
            retries = 0
            while not ready and retries < 100:
                retries += 1
                print(
                    f"[refill_wiki_data][{time.ctime()}]:\t[Downloading data for '{key}'...]")
                try:
                    res = requests.post(url=WIKI_URL_BASE, data=params)
                except:
                    print(
                        f"[refill_wiki_data][{time.ctime()}]:\t[Downloading failed '{key}'\n]")
                    continue

                return_data: str = res.json().get('return')

                if return_data:
                    ready = True
                    # get valid lua table result
                    unserialized_data = unserialize_lua_table(return_data)

                    checksum = hashlib.md5(
                        bytes(return_data, encoding="utf-8")).hexdigest()
                    cached = False
                    # check if we have data cached
                    old_checksum = ""
                    if cache.cache.exists(CHECKSUMS[key]):
                        cached = True
                        old_checksum = cache.cache.get(
                            CHECKSUMS[key]).decode("utf-8")

                    if checksum == old_checksum:
                        # create a new checksum
                        if not cached:
                            text = json.dumps(unserialized_data)
                            # save data
                            cache.cache.set(key, text)
                            # save checksum
                            cache.cache.set(CHECKSUMS[key], checksum)
                            print(
                                f"[refill_wiki_data][{time.ctime()}]:\t[{key} data ready on redis!']")
                        else:
                            print(
                                f"[refill_wiki_data][{time.ctime()}]:\t[No new data for {key}! Skipping']")
                    else:
                        text = json.dumps(unserialized_data)
                        cache.cache.set(key, text)
                        cache.cache.set(CHECKSUMS[key], checksum)
                        print(
                            f"[refill_wiki_data][{time.ctime()}]:\t[{key} data ready on redis!']")

                    break
                else:
                    print(
                        f"[refill_wiki_data][{time.ctime()}]:\t[Downloading not succesful for '{key}'data retrieved: {return_data}. Retrying...({retries})]")

    @tasks.loop(hours=1)
    async def refill_github_data(self):
        for key, url in WFCD.items():
            retries = 0
            ready = False

            while not ready and retries < 100:
                retries += 1
                print(
                    f"[refill_github_data][{time.ctime()}]:\t[Downloading data for '{key}'...]")
                try:
                    res = requests.get(url=url)
                except:
                    print(
                        f"[refill_github_data][{time.ctime()}]:\t[Downloading failed '{key}'\n]")
                    continue

                return_data = res.json()
                checksum = hashlib.md5(
                    bytes(json.dumps(res.text), encoding="utf-8")).hexdigest()
                cached = False
                ready = True
                # check if we have data cached
                old_checksum = ""
                if cache.cache.exists(CHECKSUMS[key]):
                    cached = True
                    old_checksum = cache.cache.get(
                        CHECKSUMS[key]).decode("utf-8")

                if checksum == old_checksum:
                    # create a new checksum
                    if not cached:
                        text = json.dumps(return_data)
                        cache.cache.set(key, text)
                        # save checksum
                        cache.cache.set(CHECKSUMS[key], checksum)
                        print(
                            f"[refill_github_data][{time.ctime()}]:\t[{key} data ready on redis!']")
                    else:
                        print(
                            f"[refill_github_data][{time.ctime()}]:\t[No new data for {key}! Skipping']")
                else:
                    text = json.dumps(return_data)
                    cache.cache.set(key, text)
                    cache.cache.set(CHECKSUMS[key], checksum)
                    print(
                        f"[refill_github_data][{time.ctime()}]:\t[{key} data ready on redis!']")
                break


async def setup(bot):
    await bot.add_cog(Scheduler(bot))
