import os
import redis
import pickle

class RedisStore:

	def __init__(self):
		redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
		self.redis = redis.from_url(redis_url)

	def clear_redis():
		print('Clearing redis')
		self.redis.flushdb()

	def save_session(self, session, session_name):
		print('Saving session ' + session_name)
		session = pickle.dumps(session)

		self.redis.multi()
		pipe = self.redis.pipeline()
		pipe.set(session_name, session)
		print(pipe.execute())

	def get_curr_session(self, session_name):
		print('Getting session ' + session_name)
		curr_session = self.redis.get(session_name)
		names = [session_name]
		self.redis.watch(*names)
		if curr_session is None:
			return None
		else:
			return pickle.loads(curr_session)


