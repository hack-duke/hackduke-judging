import os
import redis

class RedisStore:

	def __init__(self):
		redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
		self.redis = redis.from_url(redis_url)

	def clear_redis():
		print("Clearing redis")
		self.redis.flushdb()

	# key and value assumed to be value that can be converted to string
	def set_hash(self, name, key, value):
		return self.redis.hset(name, str(key), str(value))

	# assumes the accessor wants an integer
	def get_hash(self, name, key):
		return int(self.redis.hget(name, key).decode('utf-8'))

	def set_tuple_hash(self, name, key, tup):
		value = ''
		for item in tup:
			value += str(item) + ","
		#removes last character to make accessing easier
		self.redis.hset(name, str(key), value[:-1])

	def get_tuple_hash(self, name, key):
		value = self.redis.hget(name, key).decode('utf-8')
		array = value.split(',')
		int_array = map(lambda x: int(x), array)
		return tuple(int_array)

	def get_all_hash(self, name):
		redis_dict = self.redis.hgetall(name)
		return {k.decode('utf8'): int(v.decode('utf8')) for k, v in redis_dict.items()}

	def key_exists(self, name, key):
		return self.redis.hexists(name, str(key))

	def hash_len(self, name):
		return self.redis.hlen(name)

	# assumes keys is an array
	def delete_hash(self, name, keys):
		self.redis.hdel(name, *keys)

	# assumes key exists and has number value 
	def increment_hash(self, name, key, increment):
		current = self.get_hash(name, key)
		self.set_hash(name, key, current + increment)
