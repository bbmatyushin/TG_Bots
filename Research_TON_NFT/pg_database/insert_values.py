from pg_database.create_tbls import CreateDataTables
from parsing.parser import ParserFoxTailsIO
from import_modules import useful_tools as ut


class InsertTableValues(CreateDataTables):
    def __init__(self):
        super().__init__()
        self.parser = ParserFoxTailsIO()
        self.category_rate = ut.category_rate()  # key - имя таблицы категории, value - rate для парсинга
        # имя таблицы отдельной коллекции и адрес этой коллекции
        self.all_collections = {ut.table_name(name): address
                                for name, address in ut.all_collections().items()}

    def insert_values_categories_tbls(self):
        with self.pg_create_conn() as conn:
            with conn.cursor() as cursor:
                for category, rate in self.category_rate.items():
                    for values in self.parser.get_data_collections(rate=rate):
                        cursor.execute(f"""
                                INSERT INTO {category}(name, address, date)
                                VALUES ('{values[0]}', '{values[1]}', current_timestamp)
                                ON CONFLICT (address) DO NOTHING;
                                """)
                    conn.commit()

    def insert_values_collections_tbls(self, table: str):
        with self.pg_create_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""TRUNCATE temp_{table};""")
                conn.commit()

                for values in self.parser.get_data_items(collection_address=self.all_collections[table]):
                    cursor.execute(f"""
                        INSERT INTO temp_{table}(name, attr, price, rarity, rating,
                                external_url, nft_address, collection_address, date)
                        VALUES ('{values[0]}',
                                '{values[1]}',
                                {values[2]},
                                {values[3]},
                                {values[4]},
                                '{values[5]}',
                                '{values[6]}',
                                '{values[7]}',
                                current_timestamp);
                        """)

                    cursor.execute(f"""TRUNCATE {table};""")
                    conn.commit()

                    cursor.execute(f"""INSERT INTO {table} SELECT * FROM temp_{table};""")
                    conn.commit()
                conn.commit()



if __name__ == "__main__":
    InsertTableValues().insert_values_collections_tbls('ton_dns_domains')