sql_check_update = """
            select count(*)
            from content.film_work as fw
            join content.person_film_work as pfw on pfw.film_work_id=fw.id
            join content.person as p on p.id=pfw.person_id
            join content.genre_film_work as gfw on gfw.film_work_id=fw.id
            join content.genre as g on g.id=gfw.genre_id
            where (fw.updated_at>'{date}' and  fw.updated_at<'{date_finish}') or
                (p.updated_at>'{date}' and  p.updated_at<'{date_finish}') or
                (g.updated_at>'{date}' and  g.updated_at<'{date_finish}') """

sql_films_table = """
            select fw.id, fw.updated_at
            from content.film_work as fw
            join content.{table}_film_work as pfw on pfw.film_work_id=fw.id
            where fw.updated_at >= '{date_start}' and updated_at < '{date_finish}' and pfw.{table}_id in ('{ids}')
            limit {batch}
            """

sql_update_ids = """
            select id, updated_at
            from content.{table}
            where updated_at >= '{date_start}' and updated_at < '{date_finish}'
            limit {batch}
            """

sql_films = """
            SELECT
                fw.id as fw_id,
                fw.title,
                fw.description,
                fw.rating,
                fw.creation_date,
                pfw.role,
                p.id,
                p.full_name,
                g.name,
                g.id
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.id IN ('{ids}');
            """

sql_persons = """
            SELECT
                p.id as pid,
                p.full_name,
                fw.id,
                fw.title,
                fw.rating,
                pfw.role
            FROM content.person p
            LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
            LEFT JOIN content.film_work fw ON fw.id = pfw.film_work_id
            WHERE p.id IN ('{ids}')
            """

sql_genres = """
            SELECT
                g.id as gid,
                g.name,
                fw.id
            FROM content.genre g
            LEFT JOIN content.genre_film_work pfw ON pfw.genre_id = g.id
            LEFT JOIN content.film_work fw ON fw.id = pfw.film_work_id
            WHERE g.id IN ('{ids}')
            """
