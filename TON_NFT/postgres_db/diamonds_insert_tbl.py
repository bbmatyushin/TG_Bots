from postgres_db.pg_create_tbl import pg_create_conn
from parsers import parsing_diamonds


def insert_values(conn=pg_create_conn(), generator=parsing_diamonds.get_data()):
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

            cursor.execute(f"""
                INSERT INTO ton_diamonds_url_images (name, url_image, date)
                VALUES ('{list(row)[0]}', '{list(row)[6]}', current_timestamp)
                ON CONFLICT (name) DO NOTHING;
            """)

            conn.commit()


if __name__ == '__main__':
    # pass
    insert_values(pg_create_conn(), parsing_diamonds.get_data())
