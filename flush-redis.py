# This file clears everything from redis
import os
import redis

def clear_redis():
  print "Clearing redis"
  redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost')
  r = redis.from_url(redis_url) 
  r.flushdb()
