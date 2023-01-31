import requests
from fake_headers import Headers
import time

from data_files.useful_tools import UsefulTools


class MainParser:
    def __init__(self):
        self.url_tokens_data = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing'
        self.ut = UsefulTools()
        self.headers = Headers().generate()
        self.stable = self.ut.token_pair()

    def get_response_json(self, url, params):
        session = requests.Session()
        session.headers.update(self.headers)

        return session.get(url, params=params, stream=True).json()

    def get_tokens_data(self):
        count = 0
        token_dict, features_coin_dict = {}, {}
        while True:
            params = {"start": f"{str(count)}01",
                      "limit": "100"
            }
            data = self.get_response_json(self.url_tokens_data, params=params)
            if data["data"]["cryptoCurrencyList"]:
                crypto_currency_list = data["data"]["cryptoCurrencyList"]
                for i in range(len(crypto_currency_list)):
                    symbol = crypto_currency_list[i]["symbol"]
                    features_coin_dict["name"] = crypto_currency_list[i]["name"]
                    features_coin_dict["slug_name"] = crypto_currency_list[i]["slug"]
                    features_coin_dict["cmc_rank"] = crypto_currency_list[i]["cmcRank"]
                    features_coin_dict["last_updated"] = crypto_currency_list[i]["lastUpdated"][:-5]

                    token_dict[symbol] = features_coin_dict.copy()
            else:
                break
            time.sleep(4)
            count += 1
        return token_dict

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
        """Функция для получения данных по указанному токену (symbol).
        Эти данные будут записанны в БД."""
        tokens_list = self.ut.get_currency_list()
        exemption_exchanges = self.ut.exemption_exchanges()  # список бирж для исключения
        data = self.get_spread_response(tokens_list[symbol.upper()]["slug_name"])
        for item in data:
            if item["marketPair"].split("/")[1] in self.stable:  # пары только со стэйблами
                exchange = item["exchangeName"]
                pair = item["marketPair"]
                price = item["price"]
                volume_usd = item["volumeUsd"]
                market_reputation = item["marketReputation"]
                market_url = item["marketUrl"]  # всегда оставлять последним
                if exchange not in exemption_exchanges:  # биржа не должна быть в списке исключений
                    if market_reputation >= 0.5:  # у биржи должен быть рейтинг выше 50%
                        yield exchange, pair, price, volume_usd, market_reputation, market_url


if __name__ == '__main__':
    parser = MainParser()
    symbol = "FYN"
    d = parser.get_spread_data(symbol)

    print(1)
