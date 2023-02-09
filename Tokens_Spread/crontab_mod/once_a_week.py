from pathlib import Path
from datetime import datetime

from parsing.parser import MainParser
from data_files.data_file import dir_json_files, exchange_cex_list


if __name__ == "__main__":
    start_t = datetime.now()
    print(start_t)
    with open(f"{Path(dir_json_files, 'binance_bybit_tokens.txt')}", "w") as f:
        parser = MainParser()
        f.write(",".join(parser.collect_tokens_list(exchange_cex_list)))
    print(datetime.now())
    print(datetime.now() - start_t)
