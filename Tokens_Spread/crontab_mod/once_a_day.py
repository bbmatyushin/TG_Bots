import json
import os
import time

from database.sqlite_create import CreateDatabase
from database.sqlite_select import SelectQuery
from data_files.data_file import dir_json_files, dir_database


if __name__ == "__main__":
    if os.path.isfile(f"{dir_database}/spread_db"):
        with open(f"{dir_json_files}/symbol_tokens.json", "w") as f:
            rows = SelectQuery().select_for_symbol_tokens_json()
            coin_dict, coin_feature = {}, {}
            for row in rows:
                coin_feature["name"] = row[1]
                coin_feature["slug_name"] = row[2]
                coin_feature["cmc_rank"] = row[3]
                coin_feature["last_updated"] = row[4]
                coin_dict[row[0]] = coin_feature.copy()
            json.dump(coin_dict, f)
    else:
        CreateDatabase().insert_temp_table_all_data_coins()


