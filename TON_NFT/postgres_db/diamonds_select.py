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


def ton_diamonds_top_5_select(client_message='90', limit=5, table='ton_diamonds',
                              condition='current_price') -> list:
    # client_price - та цена которую напишут боту в чат
    conn = pg_create_conn()
    with conn.cursor() as cursor:
        cursor.execute(f"""SELECT name, size, rarity::float,
                                last_sale_price::float,
                                current_price::float,
                                nft_status,
                                to_char(date, 'DD-MON-YYYY'),
                                to_char(date, 'HH24:MI') as time
                                FROM {table}
                                WHERE {condition} <= {float(client_message)}
                                    AND nft_status = 'sale'
                                ORDER BY rarity DESC, current_price DESC, date DESC 
                                LIMIT {int(limit)};
                        """)
        rows = cursor.fetchall()
    conn.close()

    return rows


#TODO: add this function at separate module
def get_select_result(client_message='10000', limit=5, table='ton_diamonds', condition='current_price'):
    try:
        rows = ton_diamonds_top_5_select(client_message, limit, table, condition)
        output = []
        diamond_url = 'https://ton.diamonds/collection/ton-diamonds/gqj-diamond-'
        try:
            if not rows:
                if condition == 'current_price':
                    output = ['Нет данных по вашему запросу ¯\_(ツ)_/¯\n'
                              'Попробуйте ввести большее количество TON.']
                elif condition == 'rarity':
                    output = ['Нет данных по вашему запросу ¯\_(ツ)_/¯\n'
                              'Попробуйте ввести другое значение редкости.']
            else:
                for i in rows:
                    # path = download_img.get_path_to_images(i[0])
                    # image = open(f"{path}, 'rb")
                    output.append(f"◗ <b>Предмет:</b> <a href='{diamond_url}{i[0].split('#')[1]}'>{i[0]}</a>\n"
                                  f"◗ <b>Редкость:</b> {i[2]}\n"
                                  f"◗ <b>Стоимость:</b> {i[4]} TON\n"
                                  f"◗ <b>Размер:</b> {i[1]}\n"
                                  f"◗ <b>Последнее обновление цены:</b> {i[6]} в {i[7]} UTC")

            return '\n\n'.join(output)
        except Exception as e:
            return f'Some ERROR: {e}\n...( ╯°□°)╯'
    except ValueError:
        return f"Бот ожидает в сообщении только цифры (￢_￢;)"


if __name__ == '__main__':
    print(get_select_result(client_message='10000', condition='rarity'))

    # if not rows:
    #     print('Nothing')
    # else:
    #     for row in rows:
    #         print(row)
