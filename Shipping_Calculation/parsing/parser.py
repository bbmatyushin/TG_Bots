# import requests
import asyncio
import datetime
from asyncio import coroutine

from aiohttp import ClientSession

from fake_headers import Headers
# import time

from parsing.parser_params import GetParserParams
from data_files.data_file import API_VOZOVOZ, cdek_client_id, cdek_client_secret
from data_files import useful_tools as ut


class DellineParser:
    def __init__(self):
        self.headers = Headers().generate()
        self.get_params = GetParserParams()

    async def delline_get_data(self, params):
        async with ClientSession() as session:
            url = f'https://api.dellin.ru/v2/calculator.json'
            async with session.post(url, json=params) as response:
                if response.status == 200:
                    # из полученного словаря по ключу "price" можно вытащить общую стоимость
                    data = await response.json()
                    return data.get("data")
                else:
                    return f"Some requests error 🙈"


class VozovozParser(DellineParser):
    def __init__(self):
        super().__init__()
        self.api_vozovoz = API_VOZOVOZ

    async def vozovoz_get_data(self, params):
        async with ClientSession() as session:
            url_work = f'https://vozovoz.ru/api/?token={self.api_vozovoz}'
            headers = {"Content-type": "application/json"}
            async with session.post(url_work, headers=headers, json=params) as response:
                data_vozovoz = await response.json()
                return data_vozovoz


class CdekParser(DellineParser):
    def __init__(self):
        super().__init__()
        self.api_cdek = ut.get_cdek_token(client_id=cdek_client_id, client_secret=cdek_client_secret)

    async def cdek_get_data(self, params):
        async with ClientSession() as session:
            # url = 'https://api.cdek.ru/v2/calculator/tarifflist'
            url = 'https://api.cdek.ru/v2/calculator/tariff'  # Расчет по коду тарифа
            headers = {
                "Authorization": f"Bearer {self.api_cdek}",
                "Content-Type": "application/json"
            }
            async with session.post(url, headers=headers, json=params) as response:
                return await response.json()


class JDEParser(DellineParser):
    def __init__(self):
        super().__init__()
        self.url = ''
        self.headers = {"Content-Type": "application/json"}

    async def jde_get_data(self, params):
        async with ClientSession() as session:
            if params.get("from_kladr"):
                self.url = f"https://api.jde.ru/vD/calculator/PriceAddress"
            else:
                self.url = f"https://api.jde.ru/vD/calculator/price"
            async with session.get(self.url, headers=self.headers, params=params) as response:
                data = await response.json()
                if data.get("result") == '1':
                    return data
                elif data["services"][0]["error"].split(": ")[-1]:
                    return data["services"][0]["error"].split(": ")[-1]
                else:
                    return data["services"][0]["error"]


async def main():
    params_dl = await GetParserParams().delline_params(total_volume='0', quantity='1', weight='20', handling='no',
                                                 type='1', length='0.3', width='0.3', height='0.3', insurance='33000',
                                                 derival_city='Псков', arrival_city="Тверь",
                                                 delivery_arrival_variant='address',
                                                 delivery_derival_variant='terminal')
    params = await GetParserParams().vozovoz_params(total_volume='0', quantity='1', weight='20', handling='no',
                                                    type='1', length='0.3', width='0.3', height='0.3',
                                                    insurance='33000',
                                                    derival_city='Псков', arrival_city="Тверь",
                                                    delivery_arrival_variant='address',
                                                    delivery_derival_variant='terminal')
    task1 = asyncio.create_task(VozovozParser().vozovoz_get_data(params))
    task2 = asyncio.create_task(DellineParser().delline_get_data(params_dl))
    await task1
    await task2

    print(task1.result())
    print(task2.result())


if __name__ == "__main__":
    t0 = datetime.datetime.now()
    # params = GetParserParams().jde_params(total_volume='0', quantity='1', weight='20', handling='no',
    #                                       type='1', length='0.3', width='0.3', height='0.3', insurance='33000',
    #                                       derival_city='Санкт-Петербург', arrival_city="Смоленск",
    #                                       delivery_arrival_variant='address',
    #                                       delivery_derival_variant='terminal')

    # parser = VozovozParser()
    # data = parser.vozovoz_get_data(params)

    asyncio.run(main())
    print(datetime.datetime.now() - t0)
