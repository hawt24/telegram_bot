import redis
import json

from os import getenv

from dotenv import load_dotenv

load_dotenv()

class BaseRepository:
    def __init__(self, host='localhost', port=6379, db=0):
        # Update these values with your remote server details
        remote_host = 'redis-19784.c321.us-east-1-2.ec2.cloud.redislabs.com'
        remote_port = 19784  # Update with your remote server port
        remote_password = getenv("REDIS_PASSWORD")

        #self.redis = redis.Redis(host=remote_host, port=remote_port, db=remote_db)
        self.redis = redis.Redis(host = remote_host, port = remote_port, password = remote_password)


    def get(self, key):
        value = self.redis.get(key)
        return json.loads(value)
        

    def set(self, key, value):
        return self.redis.set(key, json.dumps(value))

    def delete(self, key):
        self.redis.delete(key)

    def exists(self, key):
        return self.redis.exists(key)

    def expire(self, key, seconds):
        self.redis.expire(key, seconds)

    def ttl(self, key):
        return self.redis.ttl(key)

    def keys(self, pattern):
        return self.redis.keys(pattern)

    def flush(self):
        self.redis.flushdb()

    def flush_all(self):
        self.redis.flushall()