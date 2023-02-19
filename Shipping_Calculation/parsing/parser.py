import requests
from fake_headers import Headers
# import time

from parsing.parser_params import GetParserParams
from data_files.data_file import API_VOZOVOZ, cdek_client_id, cdek_client_secret
from data_files import useful_tools as ut


class DellineParser:
    def __init__(self):
        self.headers = Headers().generate()
        self.get_params = GetParserParams()

    def delline_get_data(self, params):
        url = f'https://api.dellin.ru/v2/calculator.json'
        response = requests.post(url, json=params)

        if response.status_code == 200:
            # из полученного словаря по ключу "price" можно вытащить общую стоимость
            return response.json()["data"]
        else:
            return f"Some requests error 🙈"


class VozovozParser(DellineParser):
    def __init__(self):
        super().__init__()
        self.api_vozovoz = API_VOZOVOZ

    def vozovoz_get_data(self, params):
        url_work = f'https://vozovoz.ru/api/?token={self.api_vozovoz}'
        headers = {"Content-type": "application/json"}
        response = requests.post(url_work, headers=headers, json=params).json()

        # if response["error"]["message"]:  # возможны ошибки
        #     return response["error"]["message"]
        # else:
        #     return response

        return response


class CdekParser(DellineParser):
    def __init__(self):
        super().__init__()
        self.api_cdek = ut.get_cdek_token(client_id=cdek_client_id, client_secret=cdek_client_secret)

    def cdek_get_data(self, params):
        # url = 'https://api.cdek.ru/v2/calculator/tarifflist'
        url = 'https://api.cdek.ru/v2/calculator/tariff'  # Расчет по коду тарифа
        headers = {
            "Authorization": f"Bearer {self.api_cdek}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=params).json()

        return response


class JDEParser(DellineParser):
    def __init__(self):
        super().__init__()
        self.url = ''
        self.headers = {"Content-Type": "application/json"}

    def jde_get_data(self, params):
        if params.get("from_kladr"):
            self.url = f"https://api.jde.ru/vD/calculator/PriceAddress"
        else:
            self.url = f"https://api.jde.ru/vD/calculator/price"

        response = requests.get(self.url, headers=self.headers, params=params).json()

        if response["result"] == '1':
            return response
        elif response["services"][0]["error"].split(": ")[-1]:
            return response["services"][0]["error"].split(": ")[-1]
        else:
            return response["services"][0]["error"]


if __name__ == "__main__":
    params = GetParserParams().jde_params(total_volume='0', quantity='1', weight='10', total_weight='0',
                                                  length='0.4', width='0.35', height='0.3', insurance='50000',
                                                  derival_city='Москва', arrival_city="Санкт-Петербург")

    parser = JDEParser()
    data = parser.jde_get_data(params)

    print(data)