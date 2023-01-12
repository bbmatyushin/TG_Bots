from postgres_db.pg_create_tbl import pg_create_conn
from import_mylib.data_file import collections
import re
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
    with pg_create_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"""SELECT DISTINCT name,
                                    attr1,
                                    rarity::float,
                                    last_sale_price::float,
                                    current_price::float,
                                    nft_status,
                                    to_char(date, 'DD-MON-YYYY'),
                                    to_char(date, 'HH24:MI') as time,
                                    collection_address,
                                    nft_address                                    
                                    FROM {table}
                                    WHERE {condition} <= {float(client_message)}
                                        AND nft_status = 'sale'
                                    ORDER BY rarity DESC, current_price DESC, date DESC 
                                    LIMIT {int(limit)};
                            """)
            rows = cursor.fetchall()

    return rows


def select_rarity(value_rarity='70', table='ton_diamonds') -> list:
    with pg_create_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchall()

    if count[0][0] > 300:
        max_value = float(value_rarity) + float(1)
        min_value = float(value_rarity) - float(1)
    else:
        max_value = float(value_rarity) + float(5)
        min_value = float(value_rarity) - float(5)

    with pg_create_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"""SELECT ROUND(AVG(rarity), 2)::float,
                                    ROUND(AVG(current_price), 2)::float,
                                    PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY current_price)::float,
                                    MODE() WITHIN GROUP(ORDER BY current_price)::float,
                                    COUNT(rarity)::int
                                    FROM {table}
                                    WHERE rarity < {max_value}
                                        AND rarity > {min_value}
                                        AND rarity <> 0;
                            """)
            rows = cursor.fetchall()

            cursor.execute(f"""SELECT current_price::float                               
                                FROM {table}
                                WHERE rarity < {max_value}
                                    AND rarity > {min_value}
                                    AND rarity <> 0
                                ORDER BY current_price;
                            """)
            rows_2 = cursor.fetchall()

            rows.append([rows_2[i][0] for i in range(len(rows_2))])

    return rows


def select_min_max_price(table='ton_diamonds') -> list:
    with pg_create_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"""SELECT MIN(current_price)::float,
                                      MAX(current_price)::float,
                                      COUNT(current_price)::int
                                FROM {table};
                            """)
            rows = cursor.fetchall()

    return rows


def select_max_min_rarity(table='ton_diamonds') -> list:
    with pg_create_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"""SELECT MIN(rarity)::float,
                                      MAX(rarity)::float,
                                      COUNT(rarity)::int
                                FROM {table}
                                WHERE rarity <> 0;
                            """)
            rows = cursor.fetchall()

    return rows


#TODO: add this function at separate module
def get_select_result_top_5(client_message='10000', limit=5,
                            table='ton_diamonds', condition='current_price'):
    try:
        rows = ton_diamonds_top_5_select(client_message=client_message, limit=limit, table=table,
                                         condition=condition)
        output = []
        try:
            if not rows:
                min_price = select_min_max_price(table)[0][0]
                # max_price = select_min_max_price(table)[0][1]
                output = [f'<b>Нет данных по вашему запросу</b> ¯\_(ツ)_/¯\n'
                          f'Попробуйте ввести большее количество TON.\n\n'
                          f'<i>Минимальная стоимость в коллекции сейчас - {min_price} TON</i>']
            else:
                for i in rows:
                    subject_url = f'https://ton.diamonds/collection/{i[8]}/{i[9]}'
                    # path = download_img.get_path_to_images(i[0])
                    # image = open(f"{path}, 'rb")
                    output.append(f"◗ <b>Предмет:</b> <a href='{subject_url}'>{i[0]}</a>\n"
                                  f"◗ <b>Редкость:</b> {i[2]}\n"
                                  f"◗ <b>Стоимость:</b> {i[4]:,} TON\n"
                                  f"◗ <b>Атрибут:</b> {i[1]}\n"
                                  f"◗ <b>Обновление цены:</b> {i[6]} в {i[7]} UTC")

            return '\n\n'.join(output)
        except Exception as e:
            return f'Some ERROR: {e}\n...( ╯°□°)╯'
    except ValueError:
        return f"Бот ожидает в сообщении только цифры в формате 123.45 (￢_￢;)"


# Выдача результата для анализа редкости
def get_select_result_rarity(client_message='70', table='ton_diamonds'):
    try:
        data = select_rarity(value_rarity=client_message, table=table)
        data_price = [data[-1][i] for i in range(len(data[-1]))]
        try:
            result = []
            print_row = ''
            if len(data_price) == 1:
                print_row = f"""◗ <b>Цена:</b> {data_price[0]:,} TON"""
            elif len(data_price) == 2:
                s1 = f"◗ <b>Мин.цена:</b> {data_price[0]:,} TON\n"
                s2 = f"◗ <b>Макс.цена:</b> {data_price[-1]:,} TON"
                print_row = s1 + s2
            elif len(data_price) == 3:
                s1 = f"◗ <b>Мин.цена (1):</b> {data_price[0]:,} TON\n"
                s2 = f"◗ <b>Мин.цена (2):</b> {data_price[1]:,} TON (+{(data_price[1]/data_price[0] - 1) * 100:.2f}%)\n"
                s3 = f"◗ <b>Макс.цена:</b> {data_price[-1]:,} TON"
                print_row = s1 + s2 + s3
            elif len(data_price) >= 4:
                s1 = f"◗ <b>Мин.цена (1):</b> {data_price[0]:,} TON\n"
                s2 = f"◗ <b>Мин.цена (2):</b> {data_price[1]:,} TON (+{(data_price[1] / data_price[0] - 1) * 100:.2f}%)\n"
                s3 = f"◗ <b>Мин.цена (3):</b> {data_price[2]:,} TON (+{(data_price[2] / data_price[0] - 1) * 100:.2f}%)\n"
                s4 = f"◗ <b>Макс.цена:</b> {data_price[-1]:,} TON"
                print_row = s1 + s2 + s3 + s4

            result.append(f"Статистика стоимости предметов со средним значением "
                          f"редкости - <b>{round(data[0][0])}</b>\n"
                          f"----------------------------\n"
                          f"◗ <b>Количество предметов:</b> {data[0][-1]}\n"
                          f"{print_row}\n"
                          f"◗ <b>Средняя цена:</b> {data[0][1]:,} TON\n"
                          f"◗ <b>Медианная цена:</b> {data[0][2]:,} TON\n"
                          f"----------------------------")
        except TypeError:
            min_rarity = select_max_min_rarity(table)[0][0]
            max_rarity = select_max_min_rarity(table)[0][1]
            result = [f'<b>Нет данных по вашему запросу</b> ¯\_(ツ)_/¯\n'
                      f'Минимальная редкость предмета выставленного на продажу - {min_rarity}, '
                      f'а максимальная - {max_rarity}.\n\n'
                      f'<b>Попробуйте написать другое значение редкости, чтобы увидеть результат.</b>']
    except ValueError:
        result = [f"Бот ожидает в сообщении только цифры в формате 123.45 (￢_￢;)"]

    return ''.join(result)


if __name__ == '__main__':
    # for key, val in collections.items():

    print(get_select_result_rarity(client_message='100', table='ton_diamonds'))
        # print(get_select_result_top_5(client_message='300', table=key))

    print(1)