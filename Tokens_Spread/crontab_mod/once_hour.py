from database.sqlite_create import CreateDatabase
import datetime


def insert_into_temp_table():
    creater = CreateDatabase()
    creater.insert_temp_table_all_data_coins()


if __name__ == "__main__":
    start_t = datetime.datetime.now()
    insert_into_temp_table()
    print(datetime.datetime.now() - start_t)
