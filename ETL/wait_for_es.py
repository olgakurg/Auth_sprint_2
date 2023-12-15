import time

from elasticsearch import Elasticsearch
from models.models import Settings

if __name__ == '__main__':
    settings = Settings()
    es = Elasticsearch(hosts=settings.urles)
    while True:
        if es.ping():
            print(f"successfully connected via {settings.urles}")
            break
        print(f"Нет ответа от {settings.urles}")
        time.sleep(1)
