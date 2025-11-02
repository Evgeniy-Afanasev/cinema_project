import backoff
from redis import Redis
from functional.settings import test_settings


@backoff.on_exception(backoff.expo, Exception, max_time=60)
def ping_redis(redis_client):
    if not redis_client.ping():
        raise Exception("Redis is not reachable.")


if __name__ == '__main__':
    redis_client = Redis(host=test_settings.redis_host, port=test_settings.redis_port)

    try:
        ping_redis(redis_client)
        print("Redis is reachable.")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
