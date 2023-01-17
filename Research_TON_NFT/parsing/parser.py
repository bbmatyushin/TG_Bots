from requests import Session
from fake_headers import Headers
import time
import emoji
import json

class ParserFoxTailsIO():
    def __init__(self):
        self.url_collection = "https://foxtails.io/v1/collections"
        self.url_search = 'https://foxtails.io/v1/search'
        self.url_nft = 'https://foxtails.io/v1/nft-public/get-ntf-rarity-score'
        self.item_link = 'https://getgems.io/collection/'
        # self.headers = Headers().generate()
        self.headers = {
                        'Connection': 'keep-alive',
                        'Cache-Control': 'max-age=0',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 OPR/40.0.2308.81',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'DNT': '1',
                        'Accept-Encoding': 'gzip, deflate, lzma, sdch',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
                    }

    def get_response(self, url: str, params: dict):
        session = Session()
        session.headers.update(self.headers)
        response = session.get(url, params=params, stream=True).json()

        return response

    def get_data_collections(self, rate="trending") -> tuple:
        count_page = 1
        # while True:  ## цикл парсил бы вcе коллекции, но нужны только ТОП-10 популярных, трендовых
        params = {"page": count_page,
                  "rate": rate}
        collections = self.get_response(self.url_collection, params)
        # if collections["collections"] is None:
        #     break
        for i in range(len(collections["collections"])):
            name = collections["collections"][i]["name"]
            # в названиях коллекций встречаются эмодзи, нужно от них избавиться
            clear_name = "".join([l for l in name if l not in emoji.EMOJI_DATA]).strip()
            address = collections["collections"][i]["display_address"]

            yield clear_name, address
        # time.sleep(2)
        # count_page += 1

    def get_collections(self, rate="trending"):
        data_collections = [row for row in self.get_data_collections(rate)]  # [(name, address),...]
        collections = {key: val for key, val in data_collections}

        return collections

    def get_data_items(self, collection_address=''):
        count_page = 1
        while True:
            params = {"page": count_page,
                      "type": "nfts",
                      "collection_address": collection_address,
                      "filters": '{"status": ["sale"]}'
                      }
            # чтобы смотреть и NFT с аукциона - "status":["sale","auction"]
            data_items = self.get_response(self.url_search, params)
            if data_items["nfts"] is None:
                break
            for i in range(len(data_items["nfts"])):
                if data_items['nfts'][i]['name'] is None:
                    name = 'Unknown'
                else:
                    name = data_items['nfts'][i]['name'].replace("'", "''")
                price = data_items['nfts'][i]['nft_price']
                nft_address = data_items['nfts'][i]['display_address']
                item_link = f'{self.item_link}{collection_address}/{nft_address}'
                rarity_rating = self.get_rarity(nft_address, collection_address)
                rarity = float(rarity_rating[0])
                rating = rarity_rating[1]
                attribute = rarity_rating[2]

                yield name, attribute, price/1000000000, rarity, rating, item_link, \
                    nft_address, collection_address
            time.sleep(3)
            count_page += 1

    def get_rarity(self, nft_address, collection_address):
        """У разных коллекций нужные атрибуты (признаки) находятся в разных местах словаря"""
        params = {
           "address": nft_address,
            "collectionAddress": collection_address
        }
        data_rarity = self.get_response(self.url_nft, params)
        if 'message' in data_rarity:
            rarity = 0.0
            rating = 0
            attribute = "Unknow"
        else:
            # TON Diamonds
            if collection_address == 'EQAG2BH0JlmFkbMrLEnyn2bIITaOSssd4WdisE4BdFMkZbir':
                rarity = f'{data_rarity["attributes"][5]["sum_score"]:.2f}'
                rating = data_rarity['rating']
                attribute = data_rarity["attributes"][5]["value"]  # Size
            else:
                rarity = f'{data_rarity["attributes"][0]["sum_score"]:.2f}'
                rating = data_rarity['rating']
                attribute = "Unknow"

        return rarity, rating, attribute

    def get_result(self):
        pass


if __name__ == '__main__':
    pars = ParserFoxTailsIO()
    # with open("parsing/data_popular_collections.json") as f:
    #     collections_address = json.load(f)
    # for name, address in collections_address.items():
    #     pars.get_data_items(address)

    with open("data_test.txt", "w") as f:
        for line in pars.get_data_items(collection_address='EQDvRFMYLdxmvY3Tk-cfWMLqDnXF_EclO2Fp4wwj33WhlNFT'):
            f.write(str(line))
    # print(pars.get_data_items('EQAG2BH0JlmFkbMrLEnyn2bIITaOSssd4WdisE4BdFMkZbir'))
    print(1)