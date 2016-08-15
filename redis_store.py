import os
import redis
import pickle

CURR_SESSION = "curr_session"

class RedisStore:

	def __init__(self):
		redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
		self.redis = redis.from_url(redis_url)

	def clear_redis():
		print('Clearing redis')
		self.redis.flushdb()

	def save_session(self, session):
		print('Saving session')
		session = pickle.dumps(session)
		self.redis.set(CURR_SESSION, session)

	def get_curr_session(self):
		print('Getting session')
		curr_session = self.redis.get(CURR_SESSION)
		if curr_session is None:
			return None
		else:
			return pickle.loads(curr_session)


