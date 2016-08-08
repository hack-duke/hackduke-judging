import os
import redis

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)

def clear_redis():
  print("Clearing redis")
  redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost')
  r = redis.from_url(redis_url) 
  r.flushdb()
