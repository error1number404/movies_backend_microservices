from aioredis import Redis
from elasticsearch import AsyncElasticsearch

from models.film import Film
from models.person import Person
from models.genre import Genre
from typing import Optional
from elasticsearch import NotFoundError


class BaseService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.CACHE_EXPIRE_IN_SECONDS = 60 * 5

    async def _get_from_elastic_by_id(
            self, _id: str, model, index: str
    ) -> list:
        query = {
            "query": {
                "match": {
                    "id": {
                        "query": _id
                    }
                }
            }
        }

        try:
            doc = await self.elastic.search(index=index, body=query)
        except NotFoundError:
            return [None]

        return [model(**item["_source"]) for item in doc["hits"]["hits"]]

    async def _get_from_elastic_by_search(
            self, search: str, fields: list[str], index: str, model
    ):
        query = {
            "query": {
                "multi_match": {
                    "query": search,
                    "fields": fields,
                    "fuzziness": "auto"
                }
            }
        }

        try:
            doc = await self.elastic.search(index=index, body=query)
            return [model(**item["_source"]) for item in doc["hits"]["hits"]]
        except NotFoundError:
            return []

    async def _get_all_data_from_elastic(
            self, index: str, model
    ):
        query = {
            "query": {
                "match_all": {}
            }
        }

        try:
            doc = await self.elastic.search(index=index, body=query, )
            return [model(**item["_source"]) for item in doc["hits"]["hits"]]
        except NotFoundError:
            return []


class BaseGenreService(BaseService):
    model = Genre

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)
        self.index = "genres"

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(
            key=genre.uuid, value=genre.json(),
            expire=self.CACHE_EXPIRE_IN_SECONDS,
        )

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[model]:
        data = await self._get_from_elastic_by_id(
            _id=genre_id, index=self.index, model=self.model,
        )
        return data[0]

    async def _get_genres_from_elastic(self) -> list[model]:
        return await self._get_all_data_from_elastic(
            index=self.index, model=self.model,
        )


class BaseMovieService(BaseService):
    model = Film

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)
        self.index = "movies"

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(
            key=film.id, value=film.json(),
            expire=self.CACHE_EXPIRE_IN_SECONDS,
        )

    async def _get_film_from_elastic(self, film_id: str) -> Optional[model]:
        data = await self._get_from_elastic_by_id(
            _id=film_id, model=self.model, index=self.index
        )
        return data[0]


class BasePersonService(BaseService):
    model = Person

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)
        self.index = "persons"

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(
            key=str(person.uuid), value=person.json(),
            expire=self.CACHE_EXPIRE_IN_SECONDS,
        )

    async def _get_person_from_elastic(self, person_id: str) -> list[model]:
        data = await self._get_from_elastic_by_id(
            _id=person_id, model=self.model, index=self.index,
        )
        return data

    async def _search_persons_in_elastic(self, search: str) -> list[model]:
        data = await self._get_from_elastic_by_search(
            index=self.index, model=self.model, fields=["full_name"],
            search=search
        )
        return data

    async def _get_all_persons_from_elastic(self) -> list[model]:
        return await self._get_all_data_from_elastic(
            index=self.index, model=self.model,
        )