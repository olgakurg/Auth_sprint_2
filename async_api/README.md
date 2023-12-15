### Ссылка на репозиторий

git@github.com:valapp23/Async_API_sprint_2.git

### Запуск тестов

- Для запуска тестовой среды необходим файл tests/functional/.env, составленный по образцу:

```
PROJECT_NAME='movies'
REDIS_HOST=test_redis
REDIS_PORT=6379
ELASTIC_HOST=test_elastic
ELASTIC_PORT=9200
APP_HOST=test_api
APP_PORT=8000
API_VERSION=/api/v1/films
```

- Запуск тестов и приложения изолированно в рамках Docker-compose.

```
docker-compose -f tests/functional/docker-compose-api.yml up -d
docker-compose -f tests/functional/docker-compose-tests.yml build
```

- Запуск локальных тестов, для проверки работу всего приложения в рамках Docker-контейнера

```
docker-compose -f tests/functional/docker-compose-api.yml up -d
pytest tests/functional/src
```

- Запуск локально сервиса и тестов
    ```
    docker-compose -f tests/functional/docker-compose-basic.yml up --build -d
    python main.py
    pytest tests/functional/src
