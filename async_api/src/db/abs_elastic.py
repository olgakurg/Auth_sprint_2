import logging

from elasticsearch import AsyncElasticsearch, NotFoundError, ConnectionError

from src.db.abs import AbstractDB, M


class AsyncElastic(AbstractDB):
    def __init__(self, elastic: AsyncElasticsearch, model: M, index: str):
        self.elastic = elastic
        self.model = model
        self.index = index

    async def get_object(self, id: str) -> M | None:
        try:
            doc = await self.elastic.get(index=self.index, id=id)
        except NotFoundError:
            return None
        except ConnectionError:
            logging.error(ConnectionError)
            return None
        return self.model(**doc['_source'])

    async def get_list(self, **kwargs) -> list[M] | None:
        if kwargs.get('filters'):
            logging.info(f'get_list params {kwargs}')
        body = await self._get_query(**kwargs)
        if kwargs.get('filters'):
            logging.info(f'body for index query {body}')
        try:
            docs = await self.elastic.search(body=body, index=self.index)
        except NotFoundError:
            return None
        except ConnectionError:
            logging.error(ConnectionError)
            return None
        return [self.model(**doc['_source']) for doc in docs['hits']['hits']]

    @staticmethod
    async def _get_query(**kwargs) -> dict:
        page_size = kwargs.get('page_size')
        page_number = kwargs.get('page_number')
        query = kwargs.get('query')
        sort = kwargs.get('sort')
        filters = kwargs.get('filters') if kwargs.get('filters') else None
        body = {}
        if page_size:
            body['size'] = page_size
        if page_number:
            body['from'] = page_size * (page_number - 1) + 1
        if sort:
            keyword = 'desc' if sort.startswith('-') else 'asc'
            sort = sort[1:]
            body['sort'] = {sort: keyword}
        if filters:
            if 'query' not in body:
                body['query'] = {'bool': {'filter': [], 'must': []}}
            filters = filters.split("=")
            match_id = {f"{filters[0]}.id": f"{filters[1]}"}
            body['query']['bool']['filter'].append({
                'nested': {
                    'path': f"{filters[0]}",
                    'query': {
                        'bool': {
                            'must': [
                                {
                                    'match': match_id
                                }

                            ]
                        }
                    }
                }
            })
        if query:
            if 'query' not in body:
                body['query'] = {'bool': {'must': []}}
            query_dict = {
                'query_string': {
                    "query": query
                },
            }
            body['query']['bool']['must'].append(query_dict)
        return body
