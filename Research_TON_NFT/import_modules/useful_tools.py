import re
import json
from import_modules.work_data_file import dir_data_path


def table_name(word: str):
    word = re.sub(r'[.,"\'?:!;]', '', word.lower().replace(" ", "_").replace("-", "_"))

    return word


def trend_collections() -> dict:
    with open(f"{dir_data_path}data_trend_collections.json") as f:
        trend_collections = json.load(f)

    return trend_collections


def popular_collections() -> dict:
    with open(f"{dir_data_path}data_popular_collections.json") as f:
        popular_collections = json.load(f)

    return popular_collections


def all_collections() -> dict:
    all_collections = {**trend_collections(), **popular_collections()}

    return all_collections


def trend_tables_name():
    tables_name = [table_name(key) for key, val in trend_collections().items()]

    return tables_name


def popular_tables_name():
    tables_name = [table_name(key) for key, val in popular_collections().items()]

    return tables_name


def all_tables_name():
    tables_name = [table_name(key) for key, val in all_collections().items()]

    return tables_name


def category_rate() -> dict:
    category_rate = {"trend_collections": "trending",
                     "popular_collections": "top"}

    return category_rate


if __name__ == "__main__":
    print(trend_tables_name()[0])
