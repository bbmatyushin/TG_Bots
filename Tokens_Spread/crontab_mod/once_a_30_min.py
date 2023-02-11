import os
import time, datetime
from pathlib import Path

from data_files.data_file import dir_json_files
from parsing.parser import MainParser
from database.sqlite_create import CreateDatabaseSpread


def insert_zazam_table():
    parser = MainParser()
    creater = CreateDatabaseSpread()
    if os.path.isfile(f"{Path(dir_json_files, 'zazam_tokens.json')}"):
        tokens_dict = parser.ut.get_zazam_tokens_dict()
    else:
        parser.get_zazam_tokens()
        tokens_dict = parser.ut.get_zazam_tokens_dict()
    creater.create_zazam_table()
    creater.cursor.execute("DELETE FROM zazam_table")
    creater.base.commit()
    for key, val in tokens_dict.items():
        symbol = key,
        name = val["name"]
        slug = val["slug"]
        for row in parser.get_spread_data_zazam(symbol=symbol, name=name, slug=slug):
            creater.insert_zazam_table([row[0][0], *row[1:]])
        time.sleep(2)


if __name__ == "__main__":
    start_t = datetime.datetime.now()
    print(start_t)
    insert_zazam_table()
    print(datetime.datetime.now())
    print(datetime.datetime.now() - start_t)

