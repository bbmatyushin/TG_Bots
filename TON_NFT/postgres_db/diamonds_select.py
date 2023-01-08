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


def ton_select_rarity(value_rarity='70', table='ton_diamonds') -> list:
    conn = pg_create_conn()
    with conn.cursor() as cursor:
        cursor.execute(f"""SELECT ROUND(AVG(rarity), 2)::float,
                                ROUND(AVG(current_price), 2)::float,
                                PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY current_price)::float,
                                MODE() WITHIN GROUP(ORDER BY current_price)::float,
                                MIN(current_price)::float,
                                MAX(current_price)::float,
                                COUNT(rarity)::int
                                FROM {table}
                                WHERE rarity < ({float(value_rarity)} + 1)
                                    AND rarity > ({float(value_rarity)} - 1);
                        """)
        rows = cursor.fetchall()
    conn.close()

    return rows


def select_max_min_rarity(table='ton_diamonds') -> list:
    conn = pg_create_conn()
    with conn.cursor() as cursor:
        cursor.execute(f"""SELECT MIN(rarity)::float,
                                  MAX(rarity)::float
                            FROM {table};
                        """)
        rows = cursor.fetchall()
    conn.close()

    return rows


#TODO: add this function at separate module
def get_select_result_top_5(client_message='10000', limit=5, table='ton_diamonds', condition='current_price'):
    try:
        rows = ton_diamonds_top_5_select(client_message, limit, table, condition)
        output = []
        diamond_url = 'https://ton.diamonds/collection/ton-diamonds/gqj-diamond-'
        try:
            if not rows:
                output = ['<b>Нет данных по вашему запросу</b> ¯\_(ツ)_/¯\n'
                          'Попробуйте ввести большее количество TON.']
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
        return f"Бот ожидает в сообщении только цифры в формате 123.45 (￢_￢;)"


# Выдача результата для анализа редкости
def get_select_result_rarity(client_message='70', table='ton_diamonds'):
    try:
        data = ton_select_rarity(client_message, table)
        try:
            result = []
            result.append(f"Статистика стоимости предметов со средним значением редкости - <b>{round(data[0][0])}</b>\n"
                          f"----------------------------\n"
                          f"◗ <b>Количество предметов:</b> {data[0][6]}\n"
                          f"◗ <b>Мин.цена:</b> {data[0][4]} TON\n"
                          f"◗ <b>Макс.цена:</b> {data[0][5]} TON\n"
                          f"◗ <b>Средняя цена:</b> {data[0][1]} TON\n"
                          f"◗ <b>Медианная цена:</b> {data[0][2]} TON\n"
                          f"----------------------------")
        except TypeError:
            min_rarity = select_max_min_rarity(table)[0][0]
            max_rarity = select_max_min_rarity(table)[0][1]
            result = [f'<b>Нет данных по вашему запросу</b> ¯\_(ツ)_/¯\n'
                      f'Минимальная редкость предмета выставленного на продажу - {min_rarity}, '
                      f'а максимальная - {max_rarity}.\n\n'
                      f'<b>Укажите редкость в диапазоне от {min_rarity} до {max_rarity}.</b>']
    except ValueError:
        result = [f"Бот ожидает в сообщении только цифры в формате 123.45 (￢_￢;)"]

    return ''.join(result)


if __name__ == '__main__':
    print(get_select_result_rarity('500'))
    # print(get_select_result_top_5(client_message='10000', condition='rarity'))
    #
    # if not rows:
    #     print('Nothing')
    # else:
    #     for row in rows:
    #         print(row)
