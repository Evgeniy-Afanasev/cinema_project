import backoff
from elasticsearch import Elasticsearch
from functional.settings import test_settings


@backoff.on_exception(backoff.expo, Exception, max_time=60)
def ping_elasticsearch(es_client):
    if not es_client.ping():
        raise Exception("Elasticsearch is not reachable.")


if __name__ == '__main__':
    es_client = Elasticsearch(
        hosts=f'{test_settings.elastic_schema}{test_settings.elastic_host}:{test_settings.elastic_port}')

    try:
        ping_elasticsearch(es_client)
        print("Elasticsearch is reachable.")
    except Exception as e:
        print(f"Failed to connect to Elasticsearch: {e}")
