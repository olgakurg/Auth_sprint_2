from src.models.film import Film
from src.models.genre import Genre
from src.models.person import Person
from src.db.abs import AbstractDB, AbstractCache


class Service:
    def __init__(self, search_cache: AbstractCache, search_engine: AbstractDB):
        self.search_cache = search_cache
        self.search_engine = search_engine

    async def get_by_id(self, id: str) -> Film | Genre | Person | None:
        object = await self.search_cache.get_object(id)
        if not object:
            object = await self.search_engine.get_object(id)
            if not object:
                return None
            await self.search_cache.put_object(object.id, object)

        return object

    async def get_by_query(self, page_number: int,
                           page_size: int,
                           query: str = '',
                           sort: str = '',
                           filters: str = '') -> list[Film | Genre | Person] | None:

        objects = await self.search_cache.get_list(page_number=page_number,
                                                   page_size=page_size,
                                                   sort=sort,
                                                   filters=filters,
                                                   query=query)
        if not objects:
            objects = await self.search_engine.get_list(page_number=page_number,
                                                        page_size=page_size,
                                                        sort=sort,
                                                        filters=filters,
                                                        query=query)

            if not objects:
                return None
            await self.search_cache.put_list(objects, page_number=page_number,
                                             page_size=page_size,
                                             sort=sort,
                                             filters=filters,
                                             query=query)
        return objects
