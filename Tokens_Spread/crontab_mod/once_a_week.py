import json

from pathlib import Path
from datetime import datetime

from parsing.parser import MainParser
from data_files.data_file import dir_json_files, exchange_cex_list


if __name__ == "__main__":
    start_t = datetime.now()
    print(start_t)
    parser = MainParser()
    with open(f"{Path(dir_json_files, 'binance_bybit_tokens.txt')}", "w") as f:
        f.write(",".join(parser.collect_tokens_list(exchange_cex_list)))
    print(datetime.now())
    print(datetime.now() - start_t)

    with open(f"{Path(dir_json_files, 'zazam_tokens.json')}", "w") as f:
        json.dump(parser.get_zazam_tokens(), f)
        """Несовпадающие slug_name. Нужно переделать как на СМС"""
        # 'sushi'
        # 'avalanche-2'
        # 'gatechain-token'