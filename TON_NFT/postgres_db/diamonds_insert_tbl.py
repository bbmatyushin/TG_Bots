from postgres_db.pg_create_tbl import pg_create_conn
from parsers import parsing_diamonds

# Пока это скрипт запускается в ручную (или настроить запуск в crontab)
def insert_values(conn=pg_create_conn(), generator=parsing_diamonds.get_data()):
    """
    Добавляются спарсенные данные в обе таблице ton_diamonds и ton_diamonds_url_images.
    Данные добавляются парсером посчтрочно, через yield, чтобы не перегружать память.
    Код на создание таблиц запускается сразу при вызове 'postgres_db.pg_create_tbl'.
    """
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM ton_diamonds;")

    for row in generator:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO ton_diamonds(name, size, rarity, last_sale_price, current_price,
                                         nft_status, date)
                VALUES ('{list(row)[0]}',
                        '{list(row)[1]}',
                        {list(row)[2]},
                        {list(row)[3]},
                        {list(row)[4]},
                        '{list(row)[5]}',
                        current_timestamp);
            """)

            # Пока не придумал для чего хранить эту инфу.
            # cursor.execute(f"""
            #     INSERT INTO ton_diamonds_all_data(name, size, rarity, last_sale_price, current_price,
            #                              nft_status, date)
            #     VALUES ('{list(row)[0]}',
            #             '{list(row)[1]}',
            #             {list(row)[2]},
            #             {list(row)[3]},
            #             {list(row)[4]},
            #             '{list(row)[5]}',
            #             current_timestamp);
            # """)

            cursor.execute(f"""
                INSERT INTO ton_diamonds_url_images (name, url_image, date)
                VALUES ('{list(row)[0]}', '{list(row)[6]}', current_timestamp)
                ON CONFLICT (name) DO NOTHING;
            """)

            conn.commit()


if __name__ == '__main__':
    insert_values(pg_create_conn(), parsing_diamonds.get_data())
