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
		session = pickle.dumps(session)
		self.redis.execute_command('MULTI')
		self.redis.set(session_name, session)
		result = self.redis.execute_command('EXEC')
		self.redis.execute_command('WATCH ' + session_name)
		return result

	def get_curr_session(self, session_name):
		curr_session = self.redis.get(session_name)
		self.redis.execute_command('WATCH ' + session_name)
		if curr_session is None:
			return None
		else:
			return pickle.loads(curr_session)


