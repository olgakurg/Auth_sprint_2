from pydantic import BaseModel


class Key(BaseModel):
    page_number: int = 1
    page_size: int = 50
    query: str = ''
    index: str = 'films'
    sort: str = '-imdb_rating'
