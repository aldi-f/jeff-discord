import redis
from funcs import update_cache

class RedisManager(object):
    def __init__(self):
        conn = redis.Redis(host="redis_jeff",port=6378, db=1)
        self.cache = conn
    
    def get(self, key):
        if not self.cache.exists(key):
            update_cache(key,self)
        return self.cache.get(key)

cache = RedisManager()
