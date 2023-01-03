import psycopg2


def pg_create_conn():
    conn = psycopg2.connect(
        dbname='ton_db',
        user='admin',
        password='admin',
        host='localhost',
        port='5432'
    )

    return conn


def pg_create_table(conn):

    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ton_diamonds(
            id SERIAL PRIMARY KEY,
            name VARCHAR(20),
            size VARCHAR(10),
            rarity NUMERIC(8,2),
            last_sale_price NUMERIC(10,2),
            current_price NUMERIC(10,2),
            nft_status VARCHAR(10),
            date TIMESTAMP
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ton_diamonds_url_images(
            id SERIAL PRIMARY KEY,
            name VARCHAR(20) UNIQUE,
            url_image VARCHAR(255),
            date TIMESTAMP
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_tbl(
            id SERIAL PRIMARY KEY,
            name VARCHAR(20),
            date TIMESTAMP
            );
        """)

        conn.commit()


if __name__ == 'postgres_db.pg_create_db':  # при импорте модуля сразу создадуться таблицы
    pg_create_table(pg_create_conn())


if __name__ == '__main__':
    conn = pg_create_conn()

    with conn.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS test_tbl, ton_diamonds_url_images, ton_diamonds")
        conn.commit()