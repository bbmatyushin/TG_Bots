from database.sqlite_create import CreateDatabase
from parsing.parser import MainParser


class SelectQuery(CreateDatabase):
    def __init__(self):
        super().__init__()
        self.parser = MainParser()
        self.output = []

    def select_all(self, table, symbol):
        # (exchange, pair, price, market_url)
        spread_data = [(row) for row in self.parser.get_spread_data(symbol)]
        self.create_table(table)
        self.cursor.execute(f"DELETE FROM {table}")
        self.insert_table(table, spread_data)
        result = self.cursor.execute(f"""SELECT * FROM {table}""")

        return result.fetchall()

    def select_spread(self, table, symbol):
        # (exchange, pair, price, market_url)
        spread_data = [(row) for row in self.parser.get_spread_data(symbol)]
        self.create_table(table)
        self.cursor.execute(f"DELETE FROM {table}")
        self.insert_table(table, spread_data)
        result = self.cursor.execute(
            f"""SELECT exchange, pair, price,
                CASE
                    WHEN ROUND(((SELECT MAX(price) FROM {table}) / price - 1) * 100, 2) == 0
                    THEN '0.0%'
                    ELSE ROUND(((SELECT MAX(price) FROM {table}) / price - 1) * 100, 2) || '%'
                END AS 'diff_%',
                CASE
                    WHEN ROUND((SELECT MAX(price) FROM {table}) - price, 2) == 0
                    THEN 0
                    ELSE ROUND((SELECT MAX(price) FROM {table}) - price, 2)
                END AS 'diff_usd',
                market_url
            FROM {table}
            WHERE price == (
                    SELECT MIN(price) FROM {table}
                    ) 
                OR price == (
                    SELECT MAX(price) FROM {table}
                    )
            ORDER BY price DESC"""
        )

        return result.fetchall()

    def spread_output(self, table, symbol):
        data = self.select_spread(table=table, symbol=symbol)
        # data[0] - лежит максимальная цена за токен
        self.output = f"◗ <b>Максимальная цена:</b>\n" \
                      f"<b>Биржа:</b> <a href='{data[0][-1]}'>{data[0][0]}</a>, " \
                      f"{data[0][1]}, <b>цена:</b> ${data[0][2]}\n\n" \
                      f"◗ <b>Минимальная цена:</b>\n" \
                      f"<b>Биржа:</b> <a href='{data[1][-1]}'>{data[1][0]}</a>, " \
                      f"{data[1][1]}, <b>цена:</b> ${data[1][2]}\n" \
                      f"<b>Спред:</b> ${data[1][4]:.2f} (+{data[1][3]})"

        return self.output


if __name__ == "__main__":
    symbol = 'CSPR'
    get_select = SelectQuery()
    x = get_select.spread_output(table=symbol, symbol=symbol)
    print(x)
    # for i in range(len(x)):
    #     print(','.join(map(str, x[i])).split(','))


    # cursor.execute(f"""SELECT * FROM {table} WHERE pair == ?""", ('ETH/USDT',))