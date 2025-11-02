import json
import time
from elasticsearch import Elasticsearch, helpers
from faker import Faker
import os
import random

fake = Faker()

GENERATE_DOCS = int(os.getenv('GENERATE_DOCS', 10000))
ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))
ELASTIC_INDEX = os.getenv('ELASTIC_INDEX', 'movies')

client = Elasticsearch(
    f"http://{ELASTIC_HOST}:{ELASTIC_PORT}",
)


def wait_for_elasticsearch(client, timeout=60):
    """Ждет, пока Elasticsearch станет доступным для запросов."""
    start_time = time.time()
    while True:
        try:
            if client.ping():
                print("Elasticsearch доступен.")
                return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")

        if time.time() - start_time > timeout:
            print("Время ожидания истекло. Elasticsearch недоступен.")
            return False

        time.sleep(5)


if not wait_for_elasticsearch(client):
    exit(1)


def create_elastic_schema() -> dict:
    return {
        "settings": {
            "refresh_interval": "1s",
            "analysis": {
                "filter": {
                    "english_stop": {"type": "stop", "stopwords": "_english_"},
                    "english_stemmer": {"type": "stemmer", "language": "english"},
                    "english_possessive_stemmer": {"type": "stemmer", "language": "possessive_english"},
                    "russian_stop": {"type": "stop", "stopwords": "_russian_"},
                    "russian_stemmer": {"type": "stemmer", "language": "russian"},
                },
                "analyzer": {
                    "ru_en": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "english_stop",
                            "english_stemmer",
                            "english_possessive_stemmer",
                            "russian_stop",
                            "russian_stemmer",
                        ],
                    }
                },
            },
        },
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "uuid": {"type": "keyword"},
                "imdb_rating": {"type": "float"},
                "genres": {"type": "keyword"},
                "file_link": {"type": "text"},
                "title": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {"raw": {"type": "keyword"}},
                },
                "description": {"type": "text", "analyzer": "ru_en"},
                **{name: {"type": "keyword"} for name in
                   ["directors_names", "actors_names", "writers_names"]},
                **{role: {"type": "nested", "dynamic": "strict",
                          "properties": {
                              "id": {"type": "keyword"},
                              "name": {"type": "text", "analyzer": "ru_en"}
                          }} for role in ["directors", "actors", "writers"]},
                "created": {"type": "date"},
            },
        },
    }


elastic_schema = create_elastic_schema()
# client.indices.create(index='movies', body=elastic_schema)
genres = fake.words(nb=101, unique=True)


def generate_document():
    return {
        "uuid": fake.uuid4(),
        "imdb_rating": round(random.uniform(1.0, 10.0), 1),
        "genres": random.sample(genres, random.randint(1, 3)),  # Изменено на 1-3 жанра
        "title": fake.sentence(nb_words=3)[:-1],
        "description": fake.text(max_nb_chars=200),
        "directors_names": [fake.name() for i in range(random.randint(1, 5))],
        # Можно оставить как есть, если это поле нужно
        "actors_names": [fake.name() for i in range(random.randint(1, 5))],
        # Можно оставить как есть, если это поле нужно
        "writers_names": [fake.name() for i in range(random.randint(1, 5))],
        # Можно оставить как есть, если это поле нужно
        "directors": [{"id": fake.uuid4(), "name": fake.name()} for _ in range(random.randint(1, 3))],
        "actors": [{"id": fake.uuid4(), "name": fake.name()} for _ in range(random.randint(1, 5))],
        "writers": [{"id": fake.uuid4(), "name": fake.name()} for _ in range(random.randint(1, 3))],
        "created": fake.date_time(),
        "file_link": fake.file_path()
    }


def bulk_insert_documents(num_docs):
    counter = 0
    actions = []
    for _ in range(num_docs):
        actions.append({
            "_index": ELASTIC_INDEX,
            "_source": generate_document()
        })

        if len(actions) == 1000:
            helpers.bulk(client, actions)
            counter += len(actions)
            print(f"Пачка успешно добавлена {counter}")
            actions = []  # Сбрасываем список действий

    if actions:
        helpers.bulk(client, actions)
        counter += len(actions)
        print(f"Пачка успешно добавлена {counter}")


bulk_insert_documents(GENERATE_DOCS)

print(f"Документы успешно добавлены.")
