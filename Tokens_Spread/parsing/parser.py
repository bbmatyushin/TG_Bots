import requests
from fake_headers import Headers
import time, json

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

    def get_zazam_tokens(self):
        url_1inch_w = 'https://api.icodrops.com/portfolio/api/portfolioGroup/individualShare/1inch-wallet-4n77nknicd'
        url_trust_w = 'https://api.icodrops.com/portfolio/api/portfolioGroup/individualShare/trust-wallet-lwu80viger'
        url_cexes_w = 'https://api.icodrops.com/portfolio/api/portfolioGroup/individualShare/cexes-dw5zkzz62f'
        params = {}
        tokens_dict = {}
        feature_dict = {}
        for url in [url_1inch_w, url_trust_w, url_cexes_w]:
            response = self.get_response_json(url, params)
            for d in response["portfolios"]:
                feature_dict["name"] = d["name"]
                feature_dict["slug"] = d["slug"]
                tokens_dict[d["symbol"]] = feature_dict.copy()
        return tokens_dict

    def get_tokens_data(self):
        count = 0
        while True:
        # while count == 0:
            params = {"start": f"{str(count)}01",
                      "limit": "100",
                      "sortBy": "market_cap",
                      "sortType": "desc",
                      "convert": "USD",
                      "cryptoType": "all",
                      "tagType": "all",
                      "audited": "false",
                      "aux": "ath,atl,high24h,low24h,num_market_pairs,cmc_rank,date_added,max_supply,circulating_supply,total_supply,volume_7d,volume_30d,self_reported_circulating_supply,self_reported_market_cap"
                      }
            data = self.get_response_json(self.url_tokens_data, params=params)
            if data["data"]["cryptoCurrencyList"]:
                crypto_currency_list = data["data"]["cryptoCurrencyList"]
                for i in range(len(crypto_currency_list)):
                    symbol = crypto_currency_list[i]["symbol"]
                    name = crypto_currency_list[i]["name"]
                    slug_name = crypto_currency_list[i]["slug"]
                    cmc_rank = crypto_currency_list[i]["cmcRank"]
                    price = crypto_currency_list[i]["quotes"][0]["price"]  # стоимость в USD
                    market_cap = crypto_currency_list[i]["quotes"][0]["marketCap"]  # float
                    change_1h = crypto_currency_list[i]["quotes"][0]["percentChange1h"]  # float
                    change_24h = crypto_currency_list[i]["quotes"][0]["percentChange24h"]  # float
                    change_7d = crypto_currency_list[i]["quotes"][0]["percentChange7d"]  # float
                    change_30d = crypto_currency_list[i]["quotes"][0]["percentChange30d"]  # float
                    change_60d = crypto_currency_list[i]["quotes"][0]["percentChange60d"]  # float
                    change_90d = crypto_currency_list[i]["quotes"][0]["percentChange90d"]  # float
                    change_ytd = crypto_currency_list[i]["quotes"][0]["ytdPriceChangePercentage"]  # float
                    volume_24h = crypto_currency_list[i]["quotes"][0]["volume24h"]  # float
                    volume_7d = crypto_currency_list[i]["quotes"][0]["volume7d"]  # float
                    volume_30d = crypto_currency_list[i]["quotes"][0]["volume30d"]  # float
                    dominance = crypto_currency_list[i]["quotes"][0]["dominance"]  # float
                    ath = crypto_currency_list[i]["ath"]  # float
                    atl = crypto_currency_list[i]["atl"]  # float
                    date_added = crypto_currency_list[i]["dateAdded"][:10]
                    # last_updated = crypto_currency_list[i]["lastUpdated"][:-5]

                    yield symbol, name, slug_name, cmc_rank, price, market_cap, \
                        change_1h, change_24h, change_7d, change_30d, change_60d, \
                        change_90d, change_ytd, volume_24h, volume_7d, volume_30d, \
                        dominance, ath, atl, date_added
                    # return symbol, name, slug_name, cmc_rank
            else:
                break
            time.sleep(3)
            count += 1

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
        try:
            return response['data']['marketPairs']
        except KeyError:  # если не верный slug_name
            return None

    def get_spread_data(self, symbol: str):
        """Метод для получения данных по указанному токену (symbol).
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
                        # return exchange, pair, price, volume_usd, market_reputation, market_url

    def get_spread_data_zazam(self, symbol, name, slug):
        """Метод для сбора данных под таблицу zazam_table"""
        exemption_exchanges = self.ut.exemption_exchanges()  # список бирж для исключения
        data = self.get_spread_response(slug_name=slug)
        if data:  # может вернуться None
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
                            yield symbol, name, exchange, pair, price, \
                                volume_usd, market_reputation, market_url


    def collect_tokens_list(self, exchange_list: list):
        """Для cбора монет, торгующихся на заданных биржах.
        Список бирж передается в exchange_list.
        """
        url = 'https://api.coinmarketcap.com/data-api/v3/exchange/market-pairs/latest'
        tokens_list = []
        for exchange in exchange_list:
            count = 0
            while True:
                params = {
                    "slug": f"{exchange.lower()}",
                    "category": "spot",
                    "start": f"{count}1",
                    "limit": "50"
                }
                data = self.get_response_json(url, params=params)
                if not data["data"]["marketPairs"]:
                    break
                else:
                    for item in data["data"]["marketPairs"]:
                        tokens_list.append(f"'{item['baseSymbol']}'")  # '' стоят для sql запроса
                time.sleep(2)
                count += 5

            return list(set(tokens_list))


if __name__ == '__main__':
    parser = MainParser()
    symbol = "WLKN"
    # d = parser.get_spread_data(symbol)
    # exchange_list = ['Binance', 'Bybit']
    d = parser.get_zazam_tokens()


    print(1)
