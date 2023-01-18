from import_modules import useful_tools as ut
from pg_database.create_tbls import CreateDataTables


class SelectQueries(CreateDataTables):

    def select_top_5(self, client_message='90', limit=5, table='ton_diamonds',
                     condition='price') -> list:
        # client_price - та цена которую напишут боту в чат
        with self.pg_create_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""SELECT DISTINCT name,
                                        attr,
                                        price::float,
                                        rarity::float,
                                        rating ::integer,
                                        external_url,
                                        nft_address,
                                        collection_address,
                                        to_char(date, 'DD-MON-YYYY'),
                                        to_char(date, 'HH24:MI') as time                                    
                                        FROM {table}
                                        WHERE {condition} <= {float(client_message)}
                                        ORDER BY rarity DESC, price DESC 
                                        LIMIT {int(limit)};
                                """)
                rows = cursor.fetchall()

        return rows

    def get_select_data_rarity(self, value_rarity='70', table='ton_diamonds',
                               lower_limit=15, upper_limit=15) -> list:
        """В этом методе получаем данные для анализа редкости.
            Можно задать лимиты выборки для более детального анализа"""

        if table == "ton_dns_domains":
            return [f"У этой коллекции нет значени я редкости и рейтинга."]
        else:
            with self.pg_create_conn() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""SELECT ROUND(AVG(rarity), 2)::float,
                                        ROUND(AVG(price), 2)::float,
                                        PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY price)::float,
                                        MODE() WITHIN GROUP(ORDER BY price)::float,
                                        COUNT(rarity)::int,
                                        ROUND(AVG(rating), 2)::float,
                                        PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY rarity)::float,
                                        MIN(rarity)::float,
                                        MAX(rarity)::float
                                        FROM (
                                            (SELECT * FROM {table}
                                            WHERE rarity <= {value_rarity}
                                            ORDER BY rarity DESC
                                            LIMIT {lower_limit})
                                            UNION
                                            (SELECT * FROM {table}
                                            WHERE rarity > {value_rarity}
                                            ORDER BY rarity
                                            LIMIT {upper_limit})) as tbl;                            
                                    """)
                    rows = cursor.fetchall()

                    cursor.execute(f"""SELECT price::float,
                                        rarity::float,
                                        rating::int                             
                                        FROM (
                                            (SELECT * FROM {table}
                                            WHERE rarity <= {value_rarity}
                                            ORDER BY rarity DESC
                                            LIMIT {lower_limit})
                                            UNION
                                            (SELECT * FROM {table}
                                            WHERE rarity > {value_rarity}
                                            ORDER BY rarity
                                            LIMIT {upper_limit})) as tbl
                                            ORDER BY price; 
                                    """)
                    rows_2 = cursor.fetchall()

                    rows.append([rows_2[i] for i in range(len(rows_2))])

            return rows

    def select_min_max_price(self, table='ton_diamonds') -> list:
        with self.pg_create_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""SELECT MIN(price)::float,
                                          MAX(price)::float,
                                          COUNT(price)::int
                                    FROM {table};
                                """)
                rows = cursor.fetchall()

        return rows

    def select_max_min_rarity(self, table='ton_diamonds') -> list:
        if table == "ton_dns_domains":
            return [f"У этой коллекции нет значения редкости и рейтинга."]
        else:
            with self.pg_create_conn() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""SELECT MIN(rarity)::float,
                                              MAX(rarity)::float,
                                              MIN(rating)::int,
                                              MAX(rating)::int,
                                              COUNT(rarity)::int
                                        FROM {table}
                                        WHERE rarity <> 0;
                                    """)
                    rows = cursor.fetchall()

            return rows


class SelectResult(SelectQueries):
    def __init__(self):
        super().__init__()
        self.output = []
        self.print_row = ''

    def get_top_5(self, client_message='10000', limit=5,
                  table='ton_diamonds', condition='price'):
        try:
            rows = self.select_top_5(client_message=client_message, limit=limit, table=table,
                                     condition=condition)
            try:
                if not rows:
                    min_max_price = self.select_min_max_price(table)
                    min_price = min_max_price[0][0]
                    max_price = min_max_price[0][1]
                    self.output = [f'<b>Нет данных по вашему запросу</b> ¯\_(ツ)_/¯\n'
                                   f'Попробуйте ввести большее количество <b>TON</b>.\n\n'
                                   f'<i>Минимальная стоимость предмета в коллекции сейчас - {min_price} TON, '
                                   f'максимальная - {max_price} TON</i>']
                else:
                    for row in rows:
                        self.output.append(f"◗ <b>Предмет:</b> <a href='{row[5]}'>{row[0]}</a>\n"
                                           f"◗ <b>Редкость:</b> {row[3]}\n"
                                           f"◗ <b>Рейтинг:</b> {row[4]}\n"
                                           f"◗ <b>Стоимость:</b> {row[2]:,} TON\n"
                                           f"◗ <b>Атрибут:</b> {row[1]}\n"
                                           f"◗ <b>Данные обновлены:</b> {row[8]} в {row[9]} UTC")

                return '\n\n'.join(self.output)
            except Exception as e:
                return f'Some ERROR: {e}\n...( ╯°□°)╯'
        except ValueError:
            return f"Бот ожидает в сообщении только цифры в формате 123.45 (￢_￢;)"

    def rariry_output_data(self, client_message='70', table='ton_diamonds',
                           lower_limit=15, upper_limit=15, select_data=None):
        """Данные для выдачи результатов анализа редкости"""
        try:
            data = select_data(value_rarity=client_message, table=table,
                               lower_limit=lower_limit, upper_limit=upper_limit)
            try:
                # data[-1] - это списко кортежей с ценой, редкостью и рейтингом предметов из выборки
                if len(data[-1]) == 1:
                    self.print_row = f"""◗ <b>Цена:</b> {data[-1][0][0]:,} TON | <b>R:</b> {data[-1][0][1]:.2f}"""
                elif len(data[-1]) == 2:
                    s1 = f"◗ <b>Мин.цена:</b> {data[-1][0][0]:,} TON | <b>R:</b> {data[-1][0][1]:.2f}\n"
                    s2 = f"◗ <b>Макс.цена:</b> {data[-1][-1][0]:,} TON | <b>R:</b> {data[-1][-1][1]:.2f}"
                    self.print_row = s1 + s2
                elif len(data[-1]) == 3:
                    s1 = f"◗ <b>Мин.цена:</b>\n↳ 1) {data[-1][0][0]:,} TON | <b>R:</b> {data[-1][0][1]:.2f}\n"
                    s2 = f"↳ 2) {data[-1][1][0]:,} TON (+{(data[-1][1][0] / data[-1][0][0] - 1) * 100:.2f}%) | <b>R:</b> {data[-1][1][1]:.2f}\n"
                    s3 = f"◗ <b>Макс.цена:</b> {data[-1][-1][0]:,} TON | <b>R:</b> {data[-1][-1][1]:.2f}"
                    self.print_row = s1 + s2 + s3
                elif len(data[-1]) >= 4:
                    s1 = f"◗ <b>Мин.цена:</b>\n↳ 1) {data[-1][0][0]:,} TON | <b>R:</b> {data[-1][0][1]:.2f}\n"
                    s2 = f"↳ 2) {data[-1][1][0]:,} TON (+{(data[-1][1][0] / data[-1][0][0] - 1) * 100:.2f}%) | <b>R:</b> {data[-1][1][1]:.2f}\n"
                    s3 = f"↳ 3) {data[-1][2][0]:,} TON (+{(data[-1][2][0] / data[-1][0][0] - 1) * 100:.2f}%) | <b>R:</b> {data[-1][2][1]:.2f}\n"
                    s4 = f"◗ <b>Макс.цена:</b> {data[-1][-1][0]:,} TON | <b>R:</b> {data[-1][-1][1]:.2f}"
                    self.print_row = s1 + s2 + s3 + s4

                self.output.append(f"Статистика по предметам с медианным значением "
                                   f"редкости - <b>{round(data[0][6], 1)}</b> "
                                   f"<em>(min - {data[0][7]}, "
                                   f"ср.знач. - {round(data[0][0])}, "
                                   f"max - {data[0][8]})</em>\n"
                                   f"----------------------------\n"
                                   f"◗ <b>Количество предметов:</b> {data[0][4]}\n"
                                   f"{self.print_row}\n"
                                   f"◗ <b>Средняя цена:</b> {data[0][1]:,} TON\n"
                                   f"◗ <b>Медианная цена:</b> {data[0][2]:,} TON\n"
                                   f"----------------------------")
            except TypeError:
                min_max_rarity = self.select_max_min_rarity(table)
                min_rarity = min_max_rarity[0][0]
                max_rarity = min_max_rarity[0][1]
                # min_rating = min_max_rarity[0][2]
                # max_rating = min_max_rarity[0][3]
                self.output = [f'<b>Нет данных по вашему запросу</b> ¯\_(ツ)_/¯\n'
                               f'Минимальная редкость предмета выставленного на продажу - {min_rarity}, '
                               f'а максимальная - {max_rarity}.\n\n'
                               f'<b>Попробуйте написать другое значение редкости, чтобы увидеть результат.</b>']
        except ValueError:
            self.output = [f"Бот ожидает в сообщении только цифры (￢_￢;)"]

        return ''.join(self.output)

    def get_rarity_analytic(self, client_message='70', table='ton_diamonds',
                            lower_limit=15, upper_limit=15):
        select_data = self.get_select_data_rarity
        return self.rariry_output_data(client_message=client_message, table=table,
                                       lower_limit=lower_limit, upper_limit=upper_limit,
                                       select_data=select_data)

    def get_target_rarity_analytic(self, client_message='70', table='ton_diamonds',
                                   lower_limit=3, upper_limit=2):
        """Это такой же метод как и get_rarity_analytic, но с меньшей выборкой.
            Пока нижняя и верхняя границы не передаются пользователем."""
        select_data = self.get_select_data_rarity
        return self.rariry_output_data(client_message=client_message, table=table,
                                       lower_limit=lower_limit, upper_limit=upper_limit,
                                       select_data=select_data)


if __name__ == "__main__":
    result = SelectResult()
    # print(result.get_rarity_analytic(client_message='400', table='ton_punks'))
    print(result.get_top_5(client_message='500', table='whales_club'))
