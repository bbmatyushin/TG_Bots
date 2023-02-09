from database.sqlite_create import CreateDatabasePump
import datetime


# Данные для pump_db
def insert_into_pump_tables():
    creater = CreateDatabasePump()
    creater.insert_temp_table_all_data_coins()


if __name__ == "__main__":
    """Раз в час парсим сайт и вставляем полученные данные во врменную таблицу.
    После этого наполняем этими данными основную таблицу."""
    start_t = datetime.datetime.now()
    insert_into_pump_tables()
    CreateDatabasePump().insert_table_all_data_coins()
    print(datetime.datetime.now() - start_t)
