import json
import os

from data_files.data_file import dir_json_files, dir_path


class UsefulTools:

    def get_currency_list(self):
        with open(f"{dir_json_files}/symbol_tokens.json") as f:
            if os.stat(f.name) != 0:  # проверяем, что файл не пустой
                currency_list = json.load(f)
            else:
                currency_list = []

        return currency_list

    def token_pair(self):
        return ["USDT", "USDC", "BUSD", "USD", "DAI", "TUSD", "USDP", "USDD", "GUSD"]

    def exemption_exchanges(self):
        """По этим биржам спреды не смотреть"""
        return ["FTX", "FTX US", "Kraken", "Coinbase Exchange", "Crypto.com Exchange",
                "Balancer (V2)", "Balancer", "Balancer (V2) (Arbitrum)", "Balancer (V2) (Polygon)",
                "Dapper", "Cryptopay", "WhiteBIT", "Bitstamp", "BitMEX", "LocalBitcoins", "BingX"]


if __name__ == "__main__":
    # ut = UsefulTools()
    # tokens = list(ut.get_currency_list().keys())
    print(dir_path)