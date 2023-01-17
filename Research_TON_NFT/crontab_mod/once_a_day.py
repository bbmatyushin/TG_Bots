import json

from import_modules import useful_tools as ut
from parsing.parser import ParserFoxTailsIO
from pg_database.create_tbls import CreateDataTables
from import_modules.work_data_file import dir_data_path


if __name__ == "__main__":
    creater = CreateDataTables()

    # Создаем таблицы с категориями
    categories = ["trend_collections", "popular_collections"]
    for category in categories:
        creater.create_category_tbls(category)

    # Создаем временные и основные таблицы с коллекциями
    # Во временные будет парсится данные, потом перекидываться в основные таблицы
    tbls_name = ut.all_tables_name()

    for name in tbls_name:
        creater.create_temp_collection_tbls(name)
        creater.create_collection_tbls(name)

    # Парсим трендовые и популярные коллекции
    parser = ParserFoxTailsIO()
    with open(f"{dir_data_path}data_trend_collections.json", 'w') as f:
        json.dump(parser.get_collections(rate="trending"), f)

    with open(f"{dir_data_path}data_popular_collections.json", 'w') as f:
        json.dump(parser.get_collections(rate="top"), f)
