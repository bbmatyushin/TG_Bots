import json
import os

from data_files.data_file import dir_data_path


class UsefulTools:

    def get_currency_list(self):
        with open(f"{dir_data_path}/symbol_tokens.json") as f:
            if os.stat(f.name) != 0:  # проверяем, что файл не пустой
                currency_list = json.load(f)
            else:
                currency_list = []

        return currency_list

    def token_pair(self):
        return ["USDT", "USDC", "BUSD", "USD", "DAI"]


if __name__ == "__main__":
    ut = UsefulTools()
    tokens = list(ut.get_currency_list().keys())
    print(len(tokens))