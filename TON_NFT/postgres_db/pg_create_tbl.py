import psycopg2
from import_mylib.data_file import PORT, collections


def pg_create_conn():
    conn = psycopg2.connect(
        dbname='ton_db',
        user='admin',
        password='admin',
        host='localhost',
        port=PORT
    )
    return conn


def pg_create_table(conn: psycopg2.connect, name: str):
    with conn as conn:
        with conn.cursor() as cursor:
            # В этой таблице будут храниться спарсенные данные по коллекциям
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {name}(
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                attr1 VARCHAR(100),
                rarity NUMERIC(8,2),
                last_sale_price NUMERIC(10,2),
                current_price NUMERIC(10,2),
                nft_status VARCHAR(25),
                nft_address VARCHAR(70),
                collection_address VARCHAR(70),
                date TIMESTAMP
                );
            """)

            # Здесь сохраняются url картинки предмета, чтобы потом её можно было скачать
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {name}_url_images(
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE,
                url_image TEXT,
                date TIMESTAMP
                );
            """)

            # cursor.execute("""
            #     CREATE TABLE IF NOT EXISTS test_tbl(
            #     id SERIAL PRIMARY KEY,
            #     name VARCHAR(20),
            #     date TIMESTAMP
            #     );
            # """)

            conn.commit()


if __name__ == 'postgres_db.pg_create_tbl':  # при импорте модуля сразу создадуться таблицы
    for key, val in collections.items():
        pg_create_table(pg_create_conn(), key)


if __name__ == '__main__':
    for key, val in collections.items():
        conn = pg_create_conn()
        pg_create_table(conn, key)

    # with conn.cursor() as cursor:
    #     cursor.execute("DROP TABLE IF EXISTS test_tbl, ton_diamonds_url_images, ton_diamonds")
    #     conn.commit()