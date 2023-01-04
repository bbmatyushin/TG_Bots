from postgres_db.pg_create_tbl import pg_create_conn
"""
Здесь обрабатываются все select-запросы к таблицам.
"""


def ton_diamonds_url_images_select(name: str) -> list:
    conn = pg_create_conn()
    with conn.cursor() as cursor:
        cursor.execute(f"""
                SELECT name, url_image
                FROM ton_diamonds_url_images
                WHERE name = '{name}';
            """)
        rows = cursor.fetchall()
    conn.close()

    return rows


def ton_diamonds_top_5_select(client_price='90', limit=5) -> list:
    # client_price - та цена которую напишут боту в чат
    conn = pg_create_conn()
    with conn.cursor() as cursor:
        cursor.execute(f"""SELECT name, size, rarity::float,
                                last_sale_price::float,
                                current_price::float,
                                nft_status,
                                to_char(date, 'YY-MON-DD'),
                                to_char(date, 'HH24:MI') as time
                                FROM ton_diamonds
                                WHERE current_price <= {float(client_price)}
                                    AND nft_status = 'sale'
                                ORDER BY rarity DESC, date DESC 
                                LIMIT {int(limit)};
                        """)
        rows = cursor.fetchall()
    conn.close()

    return rows


def get_select_result(client_price='90', limit=5):
    if client_price.isnumeric():
        rows = ton_diamonds_top_5_select(client_price, limit)
        output = []
        try:
            if not rows:
                output = ['Нет результатов по вашему запросу ¯\_(ツ)_/¯\n'
                          'Попробуйте ввести большее количество TON']
            else:
                for i in rows:
                    # path = download_img.get_path_to_images(i[0])
                    # image = open(f"{path}, 'rb")
                    output.append(f"Название: {i[0]}\n"
                                  f"Редкость: {i[2]}\n"
                                  f"Стоимость: {i[4]} TON\n"
                                  f"Размер: {i[1]}\n"
                                  f"Последнее обновление цены: {i[6]} в {i[7]} UTC\n"
                                  f"Ссылка: https://ton.diamonds/collection/ton-diamonds/gqj-diamond-{i[0].split('#')[1]}")

            return '\n\n'.join(output)
        except Exception as e:
            return f'Some ERROR: {e}\n...( ╯°□°)╯'
    else:
        return f"Бот пока не понимает, что вы ввели (￢_￢;)"


if __name__ == '__main__':
    print(get_select_result('tt', 8))

    # if not rows:
    #     print('Nothing')
    # else:
    #     for row in rows:
    #         print(row)