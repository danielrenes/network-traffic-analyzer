from redis import StrictRedis

from config import Config

redis_instance = StrictRedis(host=Config.HOST, port=Config.REDIS_PORT, db=0)
pubsub_obj = redis_instance.pubsub()
