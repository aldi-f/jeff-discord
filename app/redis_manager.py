from typing_extensions import Self
import redis
from app.funcs import update_cache

class RedisManager(object):
    def __init__(self):
        conn = redis.Redis(host="redis_jeff",port=6378, db=1)
        self.cache = conn

    def __new__(cls) -> Self:
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def get(self, key):
        if not self.cache.exists(key):
            update_cache(key,self)
        return self.cache.get(key)

cache = RedisManager()
