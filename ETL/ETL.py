import json
import logging
from datetime import datetime

from time import sleep
from typing import Dict

import psycopg2
import requests

from utils.backoff import backoff
from models.models import Movie, Person, Genre, RolesChoice, PostgresSettings, Settings, PersonIndex, GenreIndex, Film
from utils.state import JsonFileStorage, State
from models.constant import sql_check_update, sql_films_table, sql_update_ids, sql_films, sql_genres, sql_persons


class Postgres:
    """
    Класс для отправки запросов в postgres
    """

    def __init__(self, dsn: Dict, batch: int):
        self.dsn = dsn
        self.batch = batch

    @backoff()
    def execute_sql(self, sql: str):
        try:
            with psycopg2.connect(**self.dsn) as conn, conn.cursor() as cursor:
                cursor.execute(sql)
                query = cursor.fetchall()
        finally:
            conn.close()
        return query

    def check_update(self, date, date_finish):
        """
        метод определяющий нужно ли обновлять БД или нет
        :param date: Дата с которой нужно смотреть обновленные записи
        :return: возвращает True если требуется обновить записи, иначе False
        """
        sql = sql_check_update.format(date=date, date_finish=date_finish)
        count = self.execute_sql(sql)[0][0]

        return count > 0

    def get_films_table(self, table, ids, date_start, date_finish):
        """
        метод возвращающий список фильмов которые требуется обновить (применяется для таблиц person and genre)
        :param table: таблица в БД
        :param ids: id элементов по которым связываем с таблицей film_work
        :param date_start: дата с которой просматривать фильмы (требуется что бы забирать данные пачками)
        :param date_finish: дата запуска проверки
        :return: список id фильмов, и время обновления последнего фильма оно запишется дальше как date_start
        """
        ids = """','""".join(ids)
        sql = sql_films_table.format(table=table,
                                     ids=ids,
                                     date_start=date_start,
                                     date_finish=date_finish,
                                     batch=self.batch)
        result = self.execute_sql(sql)
        if result:
            return result, result[-1][1]
        else:
            return result, None

    def get_update_ids(self, table, date_start, date_finish):
        """
        метод возвращающий список id элементов по нужной таблице которые входят во временной диапазон
        :param table: таблица из которой получать данные
        :param date_start: дата начала поиска
        :param date_finish: верхняя граница поиска по дате
        :return: список id элементов, и время обновления последнего элемента оно запишется дальше как date_start
        """
        sql = sql_update_ids.format(table=table, date_start=date_start, date_finish=date_finish, batch=self.batch)
        result = self.execute_sql(sql)
        if result:
            return result, result[-1][1]
        else:
            return result, None

    def get_data(self, ids, sql):
        """
        выгружает фильмы и все связанные с ним таблицы
        :param films: список id фильмов
        :return: возвращает список необработанных данных для загрузки в эластик
        """
        ids = """','""".join(ids)
        sql = sql.format(ids=ids)
        result = self.execute_sql(sql)
        return result

    def get_update_ids_data(self, table_name, time_finish, time_base):
        table_start = get_state(state, "table_start", time_base)
        ids, table_finish = self.get_update_ids(
            table_name, table_start, time_finish)
        ids_l = [idt[0] for idt in ids]

        return ids, ids_l, table_finish

    def get_films_data(self, table_name, ids, time_finish, time_base):
        film_table_start = get_state(state, "film_table_start", time_base)
        films, film_date_finish = postgres.get_films_table(table_name, ids,
                                                           film_table_start, time_finish)
        films_id = {film[0] for film in films}

        return films, films_id, film_date_finish


def data_transform(data):
    """
    функция преобразования списка из постгреса в объект для эластика
    :param data: списко фильмов
    :return: список фильмов для загрузки в эластик, или ошибка при реобразовании типов
    """
    # создаем словарь для облегчения поиска данных по фильму по id
    movies_dict = {}
    for movie_l in data:
        id = movie_l[0]
        title = movie_l[1]
        description = movie_l[2] if movie_l[2] is not None else ""
        imdb_rating = movie_l[3] if movie_l[3] is not None else 0.0
        creation_date = movie_l[4] if movie_l[4] is not None else time_base
        role = movie_l[5]
        pid = movie_l[6]
        pfull_name = movie_l[7]
        gname = movie_l[8]
        gid = movie_l[9]

        # если фильм существует в словаре, то достаем объект, иначе создаем
        # новый
        if id in movies_dict:
            movie = movies_dict[id]
        else:
            dsn = {
                "id": id,
                "imdb_rating": imdb_rating,
                "title": title,
                "description": description,
                "creation_date": creation_date
            }
            try:
                movie = Movie(**dsn)
            except Exception as e:
                return [e, dsn]
        if gid:
            movie.genre_names.add(gname)
            for gen in movie.genre:
                if gen.id == gid:
                    break
            else:
                movie.genre.append(Genre(id=gid, name=gname))
        # распределяем персон по ролям
        if role == RolesChoice.DIRECTOR:
            movie.director_names.add(pfull_name)
            for director in movie.directors:
                if director.id == pid:
                    break
            else:
                movie.directors.append(Person(id=pid, full_name=pfull_name))
        elif role == RolesChoice.ACTOR:
            movie.actors_names.add(pfull_name)
            for actor in movie.actors:
                if actor.id == pid:
                    break
            else:
                movie.actors.append(Person(id=pid, full_name=pfull_name))
        elif role == RolesChoice.WRITER:
            movie.writers_names.add(pfull_name)
            for writer in movie.writers:
                if writer.id == pid:
                    break
            else:
                movie.writers.append(Person(id=pid, full_name=pfull_name))

        movies_dict[id] = movie

    return list(movies_dict.values())


def data_transform_person(data):
    person_dict = {}
    for person_l in data:
        id = person_l[0]
        full_name = person_l[1]
        f_id = person_l[2]
        title = person_l[3]
        rating = person_l[4] if person_l[4] is not None else 0.0
        role = person_l[5]

        # если person существует в словаре, то достаем объект, иначе создаем
        # новый
        if id in person_dict:
            person = person_dict[id]
        else:
            dsn = {
                "id": id,
                "full_name": full_name
            }
            try:
                person = PersonIndex(**dsn)
            except Exception as e:
                return [e, dsn]
        for i in range(len(person.films)):
            if person.films[i] == f_id:
                person.films[i].roles.add(role)
                break
        else:
            dsn = {
                "id": f_id,
                "title": title,
                "imdb_rating": rating
            }
            try:
                film = Film(**dsn)
            except Exception as e:
                return [e, dsn]
            film.roles.add(role)
            person.films.append(film)
        person_dict[id] = person

    return list(person_dict.values())


def data_transform_genre(data):
    genre_dict = {}
    films = set()
    for genre_l in data:
        id = genre_l[0]
        name = genre_l[1]
        f_id = genre_l[2]

        if id in genre_dict:
            genre = genre_dict[id]
        else:
            dsn = {
                "id": id,
                "name": name
            }
            try:
                genre = GenreIndex(**dsn)
            except Exception as e:
                return [e, dsn]
        if f_id is not None:
            if f_id not in films:
                genre.films.append({"id": f_id})
                films.add(f_id)
        genre_dict[id] = genre
    return list(genre_dict.values())


class Elasticsearch:
    """
    класс для работы с эластиком
    """

    def __init__(self, url: str, url_param_load: str):
        self.url = url
        self.url_param_load = url_param_load

    @backoff()
    def loader(self, jsons: str):
        """
        метод отправки данных в эластик
        :param jsons: данные
        :return: возвращает список ошибок
        """
        headers = {"Content-Type": "application/x-ndjson"}
        url = self.url + self.url_param_load
        result = requests.post(url=url, data=jsons, headers=headers)
        return result.content

    def create_json(self, objects, index):
        """
        метод создает json который требуется для отправки данных в эластик
        :param
        movies: список объектов
        index: адрес схемы куда грузить
        :return: список фильмов в json формате
        """
        jsons = ""
        for row in objects:
            index_post = {"index": {"_index": index, "_id": row.id}}
            fields = row.json()

            jsons += f"""{json.dumps(index_post)}\n{fields}\n"""
        return jsons


def get_state(state, key, date_min):
    """
    функция возвращающая дату записанную в хранилище состояний, если ее нет то возвращает минимальную дату
    :param state: объект хранилища состояния
    :param key: ключ который нужно получить из хранилища
    :return: значение ключа если его нет то минимальная возможная дата
    """

    state_value = state.get_state(key)
    if state_value is None:
        state_value = date_min
    return state_value


if __name__ == "__main__":
    # load_dotenv()
    settings = Settings()

    logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=settings.debug)

    # список таблиц. True - означает что требуется вытаскивать в три этапа
    tables = {
        "person": True,
        "genre": True,
        "film_work": False
    }
    indexes = {
        "person": {"index": "persons", "sql": sql_persons, "transform": data_transform_person},
        "genre": {"index": "genres", "sql": sql_genres, "transform": data_transform_genre},
        "film_work": {"index": "films", "sql": sql_films}
    }
    postgres_dsn = PostgresSettings()
    dsn = {
        'dbname': postgres_dsn.db_name,
        'user': postgres_dsn.db_user,
        'password': postgres_dsn.db_pass,
        'host': postgres_dsn.db_host,
        'port': postgres_dsn.db_port
    }
    json_path = settings.jsonpath
    batch = settings.batch
    url = settings.urles
    index_film = settings.index_film

    url_param = settings.urlparamload

    postgres = Postgres(dsn, batch)
    elastic = Elasticsearch(url, url_param)

    json_state = JsonFileStorage(json_path)
    state = State(json_state)
    time_base = datetime.min
    sleep_out = settings.sleep

    while True:
        time_start = get_state(state, "time_start", time_base)
        time_finish = datetime.now()

        # Если нечего обновлять, то ждем 10 секунд
        if not postgres.check_update(time_start, time_finish):
            logging.debug(f"Нечего обновлять ждем {sleep_out} сек")
            sleep(sleep_out)
            continue

        # список фильмов для обновления, формируется что бы не обновлять один
        # фильм несколько раз
        films_update = set()
        for table_name in tables:
            state.set_state("table_start", time_start)
            logging.info(f"Выгружаем таблицу {table_name}")
            if tables[table_name]:
                while True:
                    """
                    получаем id таблиц словарей пачками
                    если не было выгружено ни одной записи, то переходим к другой таблице
                    """
                    ids, ids_l, table_finish = postgres.get_update_ids_data(
                        table_name, time_finish, time_base)
                    logging.debug(f"Выгруженно {len(ids)} элементов")
                    # Если ни один фильм не попал в выборку то переходим к
                    # следующей таблице
                    if not ids:
                        state.set_state("film_table_start", time_base)
                        break
                    # отправляем в эластик данные по проверяемой таблице
                    data = postgres.get_data(ids_l, indexes[table_name]["sql"])
                    data = indexes[table_name]["transform"](data)
                    data = elastic.create_json(data, indexes[table_name]["index"])
                    error = elastic.loader(data)
                    error = json.loads(error.decode())
                    if error:
                        logging.error(error)
                    else:
                        logging.debug(
                            f"{table_name} Загруженно {len(ids_l)} {table_name}")
                    logging.debug(f"ВЫГРУЗКА ФИЛЬМОВ")
                    while True:
                        """
                        выгружаем фильмы
                        убираем уже обновленные
                        преобразовываем и записываем в эластик
                        обновляем время
                        дополняем список с обновленными фильмами
                        """
                        films, films_id, film_date_finish = postgres.get_films_data(
                            table_name, ids_l, time_finish, time_base)
                        films_id -= films_update
                        logging.debug(f"Выгружено {len(films)} фильмов")
                        if films_id:
                            data = postgres.get_data(list(films_id), indexes["film_work"]["sql"])
                            data = data_transform(data)
                            data = elastic.create_json(data, indexes["film_work"]["index"])
                            error = elastic.loader(data)
                            error = json.loads(error.decode())
                            if error:
                                logging.error(error)
                            else:
                                logging.debug(
                                    f"Загруженно {len(films_id)} фильмов")

                        state.set_state("film_table_start", film_date_finish)
                        films_update = films_update | films_id
                        if len(films) != postgres.batch:
                            break

                    state.set_state("film_table_start", time_base)
                    state.set_state("table_start", table_finish)
                    if len(ids) != postgres.batch:
                        break
            else:
                logging.debug(f"ВЫГРУЗКА ФИЛЬМОВ")
                while True:
                    """
                    выгружаем фильмы
                    убираем уже обновленные
                    преобразовываем и записываем в эластик
                    обновляем время
                    дополняем список с обновленными фильмами
                    """
                    films, films_l, table_finish = postgres.get_update_ids_data(
                        table_name, time_finish, time_base)
                    logging.debug(f"Выгружено {len(films)} фильмов")
                    # Если не один фильм не попал в выборку, то переходим к
                    # следующей таблице
                    if not films:
                        state.set_state("film_table_start", time_base)
                        break
                    films_l = set(films_l)
                    films_id = films_l - films_update

                    if films_id:
                        data = postgres.get_data(list(films_id), indexes["film_work"]["sql"])
                        data = data_transform(data)
                        data = elastic.create_json(data, indexes["film_work"]["index"])
                        error = elastic.loader(data)
                        error = json.loads(error.decode())
                        if error:
                            logging.error(error)
                        else:
                            logging.debug(
                                f"Загруженно {len(films_id)} фильмов")

                    state.set_state("table_start", table_finish)
                    films_update = films_update | films_id
                    if len(films) != postgres.batch:
                        break

        state.set_state("time_start", time_finish)
        logging.info(f"Выгружено всего {len(films_update)} фильмов")
