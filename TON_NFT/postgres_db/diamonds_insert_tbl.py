from postgres_db.pg_create_tbl import pg_create_conn
from parsers import parsing_diamonds
from import_mylib.data_file import collections

# Пока это скрипт запускается в ручную (или настроить запуск в crontab)
def insert_values(conn=pg_create_conn(),
                  generator=parsing_diamonds.get_data(collection='ton-diamonds'),
                  table='ton_diamonds'):
    """
    Добавляются спарсенные данные в обе таблице ton_diamonds и ton_diamonds_url_images.
    Данные добавляются парсером посчтрочно, через yield, чтобы не перегружать память.
    Код на создание таблиц запускается сразу при вызове 'postgres_db.pg_create_tbl'.
    """
    with conn as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"DELETE FROM {table};")
        conn.commit()

        for row in generator:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {table}(name, attr1, rarity, last_sale_price, current_price,
                                             nft_status, nft_address, collection_address, date)
                    VALUES ('{list(row)[0]}',
                            '{list(row)[1]}',
                            {list(row)[2]},
                            {list(row)[3]},
                            {list(row)[4]},
                            '{list(row)[5]}',
                            '{list(row)[7]}',
                            '{list(row)[8]}',
                            current_timestamp);
                """)

                cursor.execute(f"""
                    INSERT INTO {table}_url_images (name, url_image, date)
                    VALUES ('{list(row)[0]}', '{list(row)[6]}', current_timestamp)
                    ON CONFLICT (name) DO NOTHING;
                """)
            conn.commit()


if __name__ == '__main__':
    for key, val in collections.items():
        insert_values(pg_create_conn(),
                      generator=parsing_diamonds.get_data(collection=val),
                      table=key)
    # tbl = "g_bot_sd"
    # col = "g-bots-sd"
    # insert_values(pg_create_conn(),
    #                generator=parsing_diamonds.get_data(collection=col),
    #                 table=tbl
    #                )