import time

import psycopg2

from settings import test_settings


# from psycopg2 import OperationalError

def create_conn():
    conn = None
    try:
        conn = psycopg2.connect(
            database=test_settings.db_name,
            user=test_settings.db_user,
            password=test_settings.db_password,
            host=test_settings.db_host,
            port=test_settings.db_port
        )
        print('postgresql connected successfully')

    except Exception:
        print(f"The error occurred")
    return conn


if __name__ == '__main__':
    print('connecting to postgresql instance')
    while True:
        conn = create_conn()
        if conn is not None:
            conn.close()
            break
        else:
            time.sleep(1)
            print('waiting for postgresql connection')
