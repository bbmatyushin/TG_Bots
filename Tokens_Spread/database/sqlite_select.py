from database.sqlite_create import CreateDatabase
from parsing.parser import MainParser
from data_files.useful_tools import UsefulTools


class SelectQuery(CreateDatabase):
    def __init__(self):
        super().__init__()
        self.parser = MainParser()
        self.ut = UsefulTools()
        self.output = []

    def select_all(self, table, symbol):
        # (exchange, pair, price, volume_usd, market_url)
        spread_data = [(row) for row in self.parser.get_spread_data(symbol)]
        self.create_table(table)
        self.cursor.execute(f"DELETE FROM {table}")
        self.insert_table(table, spread_data)
        result = self.cursor.execute(f"""SELECT * FROM {table}""")

        return result.fetchall()

    def test_select(self, table, symbol):
        # (exchange, pair, price, volume_usd, market_url)
        spread_data = [(row) for row in self.parser.get_spread_data(symbol)]
        self.create_table(table)
        self.cursor.execute(f"DELETE FROM {table}")
        self.insert_table(table, spread_data)
        result = self.cursor.execute(f"""WITH t1(exchange, pair, price, volume_usd,
                                                market_url, max_vol)
                        AS (SELECT *,
                            MAX(volume_usd) OVER()
                            FROM {table}
                        ),
                        t2
                        AS (SELECT * FROM t1 WHERE volume_usd >= max_vol * 0.5
                        )
                        SELECT * FROM t2""")

        return result.fetchall()

    def select_spread(self, table, symbol, volume=0):
        # (exchange, pair, price, volume_usd, market_url)
        spread_data = [(row) for row in self.parser.get_spread_data(symbol)]
        if spread_data:  # проверка, что данные не пустые
            self.create_table(table)
            self.cursor.execute(f"DELETE FROM {table}")
            self.insert_table(table, spread_data)
            result = self.cursor.execute(
                f"""WITH t1(exchange, pair, price, volume_usd,
                            market_reputation, market_url)
                AS (SELECT * FROM {table}
                    WHERE volume_usd >= {volume})
                SELECT exchange,
                    pair,
                    price,
                    CASE
                        WHEN ROUND(((SELECT MAX(price) FROM t1) / price - 1) * 100, 2) == 0
                        THEN '0.0%'
                        ELSE ROUND(((SELECT MAX(price) FROM t1) / price - 1) * 100, 2) || '%'
                    END AS 'diff_%',
                    CASE
                        WHEN ROUND((SELECT MAX(price) FROM t1) - price, 2) == 0
                        THEN 0
                        ELSE ROUND((SELECT MAX(price) FROM t1) - price, 2)
                    END AS 'diff_usd',
                    volume_usd,
                    CASE
                        WHEN market_reputation > 0.76 THEN '🟢 High'
                        WHEN market_reputation BETWEEN 0.51 AND 0.75 THEN '🟠 Moderate'
                        ELSE '🔴 Low'
                    END AS 'Confidence',
                    market_url
                FROM t1
                WHERE price == (
                        SELECT MIN(price) FROM t1
                        ) 
                    OR price == (
                        SELECT MAX(price) FROM t1
                        )
                ORDER BY price DESC"""
            )

            return result.fetchall()
        else:
            return None

    def spread_output(self, table, symbol, volume=0):
        data = self.select_spread(table=table, symbol=symbol, volume=volume)
        if data:
            if len(data) == 1:  # если был отобран только один вариант по условию
                self.output = f"----------------------------\n" \
                              f"◗ <b>СПРЕД по заданному условию не найден.</b>\n" \
                              f"----------------------------\n" \
                              f"Доступен единственный вариант торгов по токену " \
                              f"<b>{symbol.upper()}</b>:\n\n" \
                              f"<b>Биржа:</b> <a href='{data[0][-1]}'>{data[0][0]}</a> " \
                              f"<b>|</b> {data[0][6]} <b>|</b>\n" \
                              f"<b>Oбъём торгов:</b> ${data[0][5]:,.2f}\n" \
                              f"<b>Пара:</b> {data[0][1]}\n" \
                              f"<b>Цена:</b> ${data[0][2]}"
            elif len(data) > 1:
                # data[0] - лежит максимальная цена за токен
                self.output = f"◗ <b>Максимальная цена:</b>\n" \
                              f"<b>Биржа:</b> <a href='{data[0][-1]}'>{data[0][0]}</a> " \
                              f"<b>|</b> {data[0][6]} <b>|</b>\n" \
                              f"<b>Oбъём торгов:</b> ${data[0][5]:,.2f}\n" \
                              f"<b>Пара:</b> {data[0][1]}\n" \
                              f"<b>Цена:</b> ${data[0][2]}\n\n" \
                              f"◗ <b>Минимальная цена:</b>\n" \
                              f"<b>Биржа:</b> <a href='{data[1][-1]}'>{data[1][0]}</a> " \
                              f"<b>|</b> {data[1][6]} <b>|</b>\n" \
                              f"<b>Объём торгов:</b> ${data[1][5]:,.2f}\n" \
                              f"<b>Пара:</b> {data[1][1]}\n" \
                              f"<b>Цена:</b> ${data[1][2]}\n" \
                              f"----------------------------\n" \
                              f"<b>СПРЕД:</b> ${data[1][4]:.2f} (+{data[1][3]})\n" \
                              f"----------------------------"

            return self.output
        else:
            return f'❌ Нет данных по токену <b>{symbol.upper()}</b> ¯\_(ツ)_/¯\n\n' \
                   f'<b>Проверьте критерии запроса:</b>\n' \
                   f'<b>Токен:</b> {symbol.upper()}\n' \
                   f'<b>Объём торгов не меньше:</b> ${volume:,.2f}\n\n' \
                   f'<em>Данные представлены для бирж с уровнем доверия выше 🔴 <b>"Low"</b> ' \
                   f'и биржа не находится в черном списке ' \
                   f'<b>{self.ut.exemption_exchanges()}</b>.</em>'


if __name__ == "__main__":
    symbol = 'FYN'
    get_select = SelectQuery()
    x = get_select.spread_output(table=symbol, symbol=symbol, volume=2500000)
    print(x, sep='\n')
    # for i in range(len(x)):
    #     print(','.join(map(str, x[i])).split(','))


    # cursor.execute(f"""SELECT * FROM {table} WHERE pair == ?""", ('ETH/USDT',))