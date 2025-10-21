import aiohttp
import asyncio
import msgspec
import json

from typing_extensions import Self

from app.models.worldstate import WorldstateModel


class Worldstate:
    url = "https://api.warframe.com/cdn/worldState.php"
    cache_ttl = 300  # 5 minutes

    _client: Self | None = None

    _cached_worldstate: WorldstateModel | None = None
    _cached_at: float | None = None

    def __new__(cls) -> Self:
        if cls._client is None:
            cls._client = super().__new__(cls)
        return cls._client

    async def _query(self, params: dict) -> WorldstateModel:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, params=params) as response:
                return msgspec.json.decode(await response.text(), type=WorldstateModel)
            

    async def get_worldstate(self) -> WorldstateModel:
        if self._cached_worldstate is None:
            self._cached_worldstate = await self._query({})
            self._cached_at = asyncio.get_event_loop().time()
        else:
            now = asyncio.get_event_loop().time()
            if not self._cached_at:
                self._cached_at = now

            if now - self._cached_at > self.cache_ttl:
                self._cached_worldstate = await self._query({})
                self._cached_at = now
                
        return self._cached_worldstate


worldstate_client = Worldstate()
