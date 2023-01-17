from pg_database.insert_values import InsertTableValues
from import_modules import useful_tools as ut
import time


if __name__ == "__main__":
    start = time.time()

    inserter = InsertTableValues()
    tables_name = ut.all_tables_name()

    for table in tables_name:
        inserter.insert_values_collections_tbls(table)

    finish = time.time()
    print((finish - start) / 60)

    print(1)
