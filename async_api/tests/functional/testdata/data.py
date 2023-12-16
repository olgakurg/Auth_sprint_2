import uuid
import random

from faker import Faker

FILM_COUNT = 60
PERSON_COUNT = 50
GENRE_COUNT = 10
fake = Faker()

# Тут наполняем cписки данных которые должны быть в тестовых данных
test_film_title = []
test_film_title += ['Star Wars ' + fake.word() for _ in range(5 + 1)]

test_film_id = []
test_film_id += [
    '862dc948-d9cf-4377-8330-b0a5486f9fa1',
    '9ed2d08f-85c0-46c9-8032-2bf5710613b4',
    '2c63b3c3-7f38-4fa4-85b9-f3e7b96e80de',
    '87173343-4ae2-4686-935a-c2fbcd81c563',
]

test_person_full_name = []
test_person_full_name += ['Nik ' + fake.name() for _ in range(10 + 1)]

test_person_id = []
test_person_id += [
    'ff10de5a-8b34-4007-8ee9-d62bccda65db',
    '0d897e6d-2425-40ca-8f8b-5dc50ae5c92b',
    '752f3e24-5bf8-4594-be1a-bd202f4df4c7',
    '0b265b02-4419-495a-9cb0-79f2435ace12',
]

test_genre_id = []
test_genre_id += [
    '3fc58c13-32ea-404a-ba83-976f38e607cc',
    'e4b4e84a-0292-4c01-b360-0588ced918a9',
    'a7f5c2b8-a41c-43c5-ac56-3103f86315e5',
    '58447f4d-1664-4b7b-8810-3fd9fa506436',
]

persons_data = [{
    'id': test_person_id.pop() if test_person_id else str(uuid.uuid4()),
    'full_name': test_person_full_name.pop() if test_person_full_name else fake.name(),
    'films': []
} for _ in range(PERSON_COUNT + 1)]
persons_dict = {p['id']: p for p in persons_data}

genres_data = [{
    'id': test_genre_id.pop() if test_genre_id else str(uuid.uuid4()),
    'name': fake.word(),
    'films': []
} for _ in range(GENRE_COUNT + 1)]
genres_dict = {g['id']: g for g in genres_data}

films_data = [{
    'id': test_film_id.pop() if test_film_id else str(uuid.uuid4()),
    'imdb_rating': fake.random_digit(),
    'creation_date': fake.date(),
    'genre': [],
    'title': test_film_title.pop() if test_film_title else fake.word(),
    'description': fake.text(),
    'genre_names': [],
    'director_names': [],
    'actors_names': [],
    'writers_names': [],
    'directors': [],
    'actors': [],
    'writers': [],
} for _ in range(FILM_COUNT + 1)]

for film in films_data:
    film_genres = random.sample(genres_data, 2)
    for genre in film_genres:
        film['genre'].append({'name': genre['name'], 'id': genre['id']})
        film['genre_names'].append(genre['name'])
        genres_dict[genre['id']]['films'].append({'id': film['id']})

    film_persons = random.sample(persons_data, 6)
    film_actors = film_persons[0:4]
    film_writers = film_persons[3:5]
    film_director = film_persons[5]

    for actor in film_actors:
        film['actors'].append({'id': actor['id'], 'full_name': actor['full_name']})
        film['actors_names'].append(actor['full_name'])
        persons_dict[actor['id']]['films'].append({
            'id': film['id'],
            'title': film['title'],
            'imdb_rating': film['imdb_rating'],
            'roles': ['actors']
        })

    for writer in film_writers:
        film['writers'].append({'id': writer['id'], 'full_name': writer['full_name']})
        film['writers_names'].append(writer['full_name'])
        persons_dict[writer['id']]['films'].append({
            'id': film['id'],
            'title': film['title'],
            'imdb_rating': film['imdb_rating'],
            'roles': ['writers']
        })

    film['directors'].append({'id': film_director['id'], 'full_name': film_director['full_name']})
    film['director_names'].append(film_director['full_name'])
    persons_dict[film_director['id']]['films'].append({
        'id': film['id'],
        'title': film['title'],
        'imdb_rating': film['imdb_rating'],
        'roles': ['directors']
    })

data = {
    'films': films_data,
    'persons': persons_dict.values(),
    'genres': genres_dict.values()
}
