import psycopg2
from import_modules.work_data_file import PORT
from import_modules import useful_tools as ut


class CreateConnect():
    def __init__(self):
        self.port = PORT

    def pg_create_conn(self):
        conn = psycopg2.connect(
            dbname="ton_nfts_db",
            user="admin",
            password='admin',
            host="localhost",
            port=self.port
        )
        return conn


class CreateDataTables(CreateConnect):

    def create_category_tbls(self, category: str):
        with self.pg_create_conn() as conn:
            with conn.cursor() as cursor:
                # cursor.execute(f"DROP TABLE IF EXISTS {category}")
                # Таблица трендовых коллекций
                cursor.execute(f"""
                        CREATE TABLE IF NOT EXISTS {category}(
                            id SERIAL PRIMARY KEY,
                            name TEXT,
                            address TEXT UNIQUE,
                            date TIMESTAMP
                            );""")
                conn.commit()

    def create_temp_collection_tbls(self, table_name: str):
        """
        Временная таблица. Сюда будут складываться спарсенные данные и после этого
        забираться в основную таблицу, чтобы при запросе не попасть на процесс
        парсинга (парсинг одной таблици занимает 15-20 минут).
        """
        with self.pg_create_conn() as conn:
            with conn.cursor() as cursor:
                # Таблицы для хранения предметов разных коллекций
                cursor.execute(f"""
                        CREATE TABLE IF NOT EXISTS temp_{table_name}(
                            id SERIAL PRIMARY KEY,
                            name TEXT,
                            attr TEXT,
                            price NUMERIC(20,2),
                            rarity NUMERIC(8,2),
                            rating INTEGER,
                            external_url TEXT,
                            nft_address VARCHAR(70),
                            collection_address VARCHAR(70),
                            date TIMESTAMP
                            );""")

                # cursor.execute(f"DROP TABLE IF EXISTS temp_{table_name}")
                conn.commit()

    def create_collection_tbls(self, table_name: str):
        with self.pg_create_conn() as conn:
            with conn.cursor() as cursor:
                # Таблицы для хранения предметов разных коллекций
                cursor.execute(f"""
                        CREATE TABLE IF NOT EXISTS {table_name}(
                            id SERIAL PRIMARY KEY,
                            name TEXT,
                            attr TEXT,
                            price NUMERIC(20,2),
                            rarity NUMERIC(8,2),
                            rating INTEGER,
                            external_url TEXT,
                            nft_address VARCHAR(70),
                            collection_address VARCHAR(70),
                            date TIMESTAMP
                            );""")

                # cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                conn.commit()


if __name__ == "__main__":
# if __name__ == "pg_database.create_tbls":
    tables_name = ut.all_tables_name()
    creater = CreateDataTables()

    for table in tables_name:
        creater.create_collection_tbls(table)



