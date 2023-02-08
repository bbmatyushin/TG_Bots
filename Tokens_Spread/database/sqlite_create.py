import sqlite3

from parsing.parser import MainParser
from data_files.data_file import dir_database

class CreateDatabase():
    """Сoзданиe и наполнение таблиц"""

    def __init__(self):
        self.base = sqlite3.connect(f"{dir_database}/spread_db")
        self.cursor = self.base.cursor()
        self.parser = MainParser()
        self.table = "ethereum"

    def create_temp_table_all_data_coins(self):
        """Сюда собираются данные во время парсинга, потом
        эти данные будут вставляться в основную таблицу, для
        select-запросов."""
        self.base.execute("DROP TABLE IF EXISTS temp_all_data_coins")
        self.base.commit()
        self.base.execute("""CREATE TABLE IF NOT EXISTS temp_all_data_coins(
                        symbol TEXT, name TEXT, slug_name TEXT, cmc_rank FLOAT,
                        price FLOAT, market_cap FLOAT, change_1h FLOAT,
                        change_24h FLOAT, change_7d FLOAT, change_30d FLOAT,
                        change_60d FLOAT, change_90d FLOAT, change_ytd FLOAT,
                        volume_24h FLOAT, volume_7d FLOAT, volume_30d FLOAT,
                        dominance FLOAT, ath FLOAT, atl FLOAT,
                        date_added TIMESTAMP, date TIMESTAMP)""")
        self.base.commit()

    def insert_temp_table_all_data_coins(self):
        self.create_temp_table_all_data_coins()
        for row in self.parser.get_tokens_data():
            self.cursor.execute(f"""INSERT INTO temp_all_data_coins(
                        symbol, name, slug_name, cmc_rank, price, market_cap,
                        change_1h, change_24h, change_7d, change_30d, change_60d,
                        change_90d, change_ytd, volume_24h, volume_7d, volume_30d,
                        dominance, ath, atl, date_added, date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?,
                                ?, ?, ?, ?, current_timestamp)""", (row))
        self.base.commit()

    def create_table_all_data_coins(self):
        """Эта таблица для select запросов"""
        self.base.execute("DROP TABLE IF EXISTS all_data_coins")
        self.base.commit()
        self.base.execute("""CREATE TABLE IF NOT EXISTS all_data_coins(
                        symbol TEXT, name TEXT, slug_name TEXT, cmc_rank FLOAT,
                        price FLOAT, market_cap FLOAT, change_1h FLOAT,
                        change_24h FLOAT, change_7d FLOAT, change_30d FLOAT,
                        change_60d FLOAT, change_90d FLOAT, change_ytd FLOAT,
                        volume_24h FLOAT, volume_7d FLOAT, volume_30d FLOAT,
                        dominance FLOAT, ath FLOAT, atl FLOAT,
                        date_added TIMESTAMP, date TIMESTAMP)""")
        self.base.commit()

    def insert_table_all_data_coins(self):
        """Сначало проверяем, что во врменной таблице достаточно данных,
        которые будем забирать из неё"""
        count_rows = \
            self.cursor.execute("""SELECT COUNT(*) FROM temp_all_data_coins""")
        if int(count_rows.fetchone()[0]) > 1000:
            self.create_table_all_data_coins()
            self.cursor.execute("DELETE FROM all_data_coins")
            self.cursor.execute("""INSERT INTO all_data_coins
                    SELECT * FROM temp_all_data_coins""")

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
    db = CreateDatabase()
    # db.insert_table_best()