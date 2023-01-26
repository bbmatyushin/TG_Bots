import json
import time

from parsing.parser import MainParser
from data_files.data_file import dir_data_path


if __name__ == "__main__":
    start_time = time.time()
    parser = MainParser()
    with open(f"{dir_data_path}/symbol_tokens.json", "w") as f:
        json.dump(parser.get_symbol_tokens(), f)

    finish_time = time.time()
    print(f"Parsing time - {finish_time - start_time} sec.")


