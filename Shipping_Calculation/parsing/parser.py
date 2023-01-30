import requests
from fake_headers import Headers
# import time

from parsing.parser_params import GetParserParams


class ShippingParser:
    def __init__(self):
        self.headers = Headers().generate()
        self.get_params = GetParserParams()

    def get_response_json(self, url='', params={}):
        response = requests.get(url, headers=self.headers, params=params).json()

        return response

    def delline_parser(self, params):
        """Парсер расчета стоимости доставки Деловых Линий"""
        url = 'https://www.dellin.ru/api/calculation.json'
        response = self.get_response_json(url=url, params=params)

        return response

    def get_cities_code_delline(self):
        """Парсит инфу по всем городам в базе Деловых Линий (код, адрес, телефоны и т.д.)"""
        url = 'https://www.dellin.ru/api/v1/contacts.json'
        response = self.get_response_json(url=url)

        return response


if __name__ == "__main__":
    dl_pars = ShippingParser()
    params = GetParserParams().delline_params()
    data = dl_pars.delline_parser(params)

    print(f'1 - {data.get("accompanying_documents")}')
    print(f'2 - {data.get("arrivalToDoor")} - Доставить груз до адреса получателя')
    print(f'3 - {data.get("commercialMail")}')
    print(f'4 - {data.get("derivalToDoor")} - Забрать груз от адреса отправителя')
    print(f'5 - {data.get("express")} - Экспресс-перевозка')
    print(f'6 - {data.get("fatal_informing")} - информирование о статусе')
    print(f'7 - {data.get("insurance")} - страхование груза')
    print(f'8 - {data.get("intercity")} - межтерминальная перевозка')
    print(f'9 - {data.get("term_insurance")} - страхование сроков')
    print(f'10 - {data.get("unloading")} - Разгрузочные работы')

    print(1)