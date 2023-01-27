import requests
from fake_headers import Headers
import time

from data_files.useful_tools import UsefulTools


class MainParser:
    def __init__(self):
        self.url_tokens_data = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing'
        self.start_count = 0
        self.ut = UsefulTools()
        self.headers = Headers().generate()
        self.stable = self.ut.token_pair()
        self.token_dict = {}

    def get_response_json(self, url, params):
        session = requests.Session()
        session.headers.update(self.headers)

        return session.get(url, params=params, stream=True).json()

    def get_symbol_tokens_data(self):
        count = self.start_count
        while True:
            params = {"start": f"{str(count)}01",
                      "limit": "100"
            }
            data = self.get_response_json(self.url_tokens_data, params=params)
            if data["data"]["cryptoCurrencyList"]:
                crypto_currency_list = data["data"]["cryptoCurrencyList"]
                for i in range(len(crypto_currency_list)):
                    symbol = crypto_currency_list[i]["symbol"]
                    name = crypto_currency_list[i]["name"]
                    slug_name = crypto_currency_list[i]["slug"]
                    cmc_rank = crypto_currency_list[i]["cmcRank"]
                    last_updated = crypto_currency_list[i]["lastUpdated"][:-5]

                    yield symbol, (name, slug_name, cmc_rank, last_updated)
                    # yield symbol, self.token_dict
            else:
                break
            time.sleep(3)
            count += 1

    def get_symbol_tokens(self):
        # data = self.get_symbol_tokens_data()
        data = [row for row in self.get_symbol_tokens_data()]
        currency_list = {key: val for key, val in data}
        return currency_list

    def get_spread_response(self, slug_name):
        url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/market-pairs/latest"
        params = {
            "slug": slug_name,
            "start": "1",
            "limit": "100",
            "category": "spot",
            "centerType": "all",
            "sort": "cmc_rank_advanced"
        }

        response = requests.get(url, headers=self.headers, params=params).json()

        return response['data']['marketPairs']

    def get_spread_data(self, symbol: str):
        tokens_list = self.ut.get_currency_list()
        data = self.get_spread_response(tokens_list[symbol.upper()][1])
        for item in data:
            if item["marketPair"].split("/")[1] in self.stable:  # пары только со стэйблами
                exchange = item["exchangeName"]
                pair = item["marketPair"]
                price = item["price"]
                volume_usd = item["volumeUsd"]
                market_url = item["marketUrl"]  # всегда оставлять последним

                yield exchange, pair, price, volume_usd, market_url


if __name__ == '__main__':
    parser = MainParser()

    parser.get_symbol_tokens()

    # symbol = 'eth'
    #
    # spread_data =[(row) for row in parser.get_spread_data(symbol)]
    # print(spread_data)

    print(1)
