import time

import redis

from settings import test_settings

if __name__ == '__main__':
    redis_client = redis.Redis(host=test_settings.REDIS_HOST, port=test_settings.REDIS_PORT)
    print('connecting for redis instance')
    while True:
        print('waiting for redis connection')
        if redis_client.ping():
            print('redis connected successfully')
            break
        else:
            time.sleep(1)
