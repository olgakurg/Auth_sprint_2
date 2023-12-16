import time

from elasticsearch import Elasticsearch

from settings import test_settings

if __name__ == '__main__':
    es_client = Elasticsearch(host=test_settings.ELASTIC_HOST, port=test_settings.ELASTIC_PORT, validate_cert=False,
                              use_ssl=False)
    print('connecting for elasticsearch instance')
    while True:
        print('waiting for elasticsearch connection')
        if es_client.ping():
            print('elasticsearch connected successfully')
            break
        time.sleep(1)
