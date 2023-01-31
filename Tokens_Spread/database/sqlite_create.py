import sqlite3

class CreateDatabase():
    """Сoзданиe и наполнение таблиц"""

    def __init__(self):
        self.base = sqlite3.connect("spread_db")
        self.cursor = self.base.cursor()
        self.table = "ethereum"

    def create_table(self, table):
        # self.base.execute(f"DROP TABLE IF EXISTS {table}")
        # self.base.commit()
        self.base.execute(f"""CREATE TABLE IF NOT EXISTS {table}(
                        exchange TEXT, pair TEXT, price FLOAT, volume_usd FLOAT, 
                        market_reputation FLOAT, market_url TEXT) """)
        self.base.commit()

    def insert_table(self, table, list_data):
        # Вставлять нужно список списков
        self.cursor.executemany(f"""INSERT INTO {table}(exchange, pair, price, volume_usd,
                                                        market_reputation, market_url)
                            VALUES (?, ?, ?, ?, ?, ?)""", (list_data))
        self.base.commit()


if __name__ == "__main__":
    pass