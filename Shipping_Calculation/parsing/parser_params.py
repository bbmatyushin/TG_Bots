import datetime
import requests

from data_files.data_file import API_DELLINE, cdek_client_id, cdek_client_secret,\
        jde_user_id, jde_apy_key
from json_data.delline_get_data_info import DellineTerminals
from data_files import  useful_tools as ut


class GetParserParams:
    def __init__(self):
        self.today = datetime.datetime.now().date().strftime('%Y-%m-%d')
        self.tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).date().strftime('%Y-%m-%d')
        # Токен CDEK будет генерироваться каждый раз при обращении к классу
        self.api_cdek = ut.get_cdek_token(client_id=cdek_client_id, client_secret=cdek_client_secret)
        self.api_delline  = API_DELLINE
        self.jde_user_id = jde_user_id
        self.jde_apy_key = jde_apy_key
        # функция ниже вернет {terminal_id: "", city_kladr: ""}
        self.delline_term_kladr_info = DellineTerminals().delline_get_delivery_terminal_data()

    def delline_params(self, **kwargs):
        """
        :param delivery_type:
        :param delivery_variant:
        :param total_volume:
        :param quantity:
        :param weight:
        :param length:
        :param width:
        :param height:
        :param insurance:
        :param arrival_city:
        :param derival_city:
        :return:
        """
        # Если место одно, то объём считается сам, иначе нужно задать общ.объём
        if int(kwargs.get("quantity")) == 1:
            total_volume = str(float(kwargs.get("length")) * float(kwargs.get("width")) *
                               float(kwargs.get("height")))
            total_weight = kwargs.get("weight")
        else:
            total_volume = kwargs.get("total_volume")
            total_weight = kwargs.get("total_weight")

        # Не задан параметр - packages - это вид упаковки
        params = {
            "appkey": self.api_delline,
            "delivery": {
                "deliveryType": {
                    "type": kwargs.get("delivery_type", "auto")  # "auto"- автодоставка; "express" - экспресс-доставка;
                },
                "arrival": {
                    "variant": kwargs.get("delivery_variant", "terminal"),  # "address" - доставка груза до адреса
                    "terminalID": \
                        self.delline_term_kladr_info[kwargs.get("arrival_city")]["terminal_id"]
                },
                "derival": {
                    "produceDate": str(self.today),
                    "variant": kwargs.get("delivery_variant", "terminal"),  # "address" - доставка груза до адреса
                    "terminalID": \
                        self.delline_term_kladr_info[kwargs.get("derival_city")]["terminal_id"]
                }
            },
            "cargo": {
                "quantity": int(kwargs.get("quantity")),  # integer
                "length": float(kwargs.get('length')),  # float
                "width": float(kwargs.get("width")),  # float
                "height": float(kwargs.get("height")),  # float
                "weight": float(kwargs.get("weight")),  # float
                "totalWeight": float(total_weight),  # float
                "totalVolume": float(total_volume),  # float
                "insurance": {
                    "statedValue": float(kwargs.get("insurance")),  # float
                    "term": True
                }
            }
        }

        return params

# ================ Формируем параметры для запросов VOZOVOZ ================
    def vozovoz_params(self, **kwargs):
        """
        :param total_volume:
        :param length:
        :param width:
        :param height:
        :param weight:
        :param total_weight:
        :param quantity:
        :param insurance:
        :param derival_city:
        :param arrival_city:
        :return: 
        """

        if int(kwargs.get("quantity")) == 1:
            total_volume = str(float(kwargs.get("length")) * float(kwargs.get("width")) *
                               float(kwargs.get("height")))
            total_weight = kwargs.get("weight")
        else:
            total_volume = kwargs.get("total_volume")
            total_weight = kwargs.get("total_weight")

        params = {
            "object": "price",
            "action": "get",
            "params": {
                "cargo": {
                    "dimension": {  # габариты
                        "max": {  # макс.габариты одного места
                            "length": float(kwargs.get('length')),
                            "width": float(kwargs.get("width")),
                            "height": float(kwargs.get("height")),
                            "weight": float(kwargs.get("weight")),
                        },
                        "quantity": int(kwargs.get("quantity")),  # количество мест
                        "volume": float(total_volume),  # общий объем
                        "weight": float(total_weight)  # общий вес
                    },
                    "insurance": float(kwargs.get("insurance"))
                },
                "gateway": {
                    "dispatch": {  # откуда
                        "point": {
                            "location": kwargs.get("derival_city"),
                            "terminal": "default"  # терминал по умолчанию
                        }
                    },
                    "destination": {  # куда
                        "point": {
                            "location": kwargs.get("arrival_city"),
                            "terminal": "default"  # терминал по умолчанию
                        }
                    }
                }
            }
        }

        return params
    
# ================ Формируем параметры для запросов СДЭК ================
    #TODO: Возвращает 401, из-за непройденой аунтентификации
    def cdek_get_cities_info(self, city_name: str):
        """Для получения номеров городов согласно документации СДЭК
        https://api-docs.cdek.ru/33829437.html"""

        dict_info = {}
        url = "https://api.cdek.ru/v2/location/cities"
        headers = {"Authorization": f"Bearer {self.api_cdek}"}
        params = {"city": city_name}

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            dict_info["city_code"] = response.json()[0].get("code")
            dict_info["kladr"] = response.json()[0].get("kladr_code")
            return dict_info
        else:
            return None

    def cdek_params(self, **kwargs):
        """Расчет для отправки одного места.
        Для нескольких мест нужно передать список packages [{}, {}]

        :param tariff_code
        :param insurance
        :param length
        :param width
        :param height
        :param weight
        :param derival_city
        :param arrival_city
        """

        derival_city_code = self.cdek_get_cities_info(kwargs.get("derival_city"))["city_code"]
        arrival_city_code = self.cdek_get_cities_info(kwargs.get("arrival_city"))["city_code"]

        # Данные будут приходить в метрах, нужно перевести в см
        length_m, width_m, height_m = map(int, [round(float(kwargs.get("length")) * 100, 0),
                                                round(float(kwargs.get("width")) * 100, 0),
                                                round(float(kwargs.get("height")) * 100, 0)])
        weight_kg = int(round(float(kwargs.get("weight")) * 1000, 0))

        params = {
            "type": 1,  # - "интернет-магазин", type 2 - "доставка"
            "tariff_code": kwargs.get("tariff_code", 136),  # код для тарифа доставки. 136 - Склад-Склад
            "from_location": {
                "code": derival_city_code,
                "city": kwargs.get("derival_city")
            },
            "to_location": {
                "code": arrival_city_code,
                "city": kwargs.get("arrival_city")
            },
            "services": {
                "code": "INSURANCE",
                "parameter": kwargs.get("insurance")
            },
            "packages": [
                {
                    "weight": weight_kg,  # int
                    "length": length_m,  # int
                    "width": width_m,  # int
                    "height": height_m  # int
                }
            ]
        }

        return params

    def jde_params(self, pickup='0', delivery='0',
                   services='', **kwargs):
        """Инфа тут - https://api.jde.ru/dev/api/calculator/calculate-service-cost-smart.html

        url_for_type = 'https://api.jde.ru/vD/calculator/PriceTypeListAvailable'
        {"type":1,"name":"Доставка сборных грузов"},
        {"type":2,"name":"Экспресс доставка грузов"},
        {"type":3,"name":"Индивидуальная доставка грузов"},
        {"type":6,"name":"Интернет-посылка"},
        {"type":7,"name":"Курьерская доставка"}

        service:
        BRD - Евроборт
        CRGREC - Внутренний пересчет
        DCD - Выполнение забора груза в день заявки
        DDO - Забор груза в нерабочее время
        DFT - Забор груза в фиксиров. время
        DLU - ПГР и перенос по территории клиента
        FRAG - Доставка хрупкого грузобагажа
        LATH - Обрешетка
        LWHS - Загрузка груза на локальный склад
        OVERS - Негабаритный груз
        SOVERS - Супер негабаритный груз
        TMP - Доставка в тепле

        :param from
        :param to
        :param smart=1  - обязательный
        :param type
        :param weight  кг
        :param volume  м3, - можно использовать как общий объём
        :param length  м, | При отсутствии параметра volume участвует в вычислении общего объема
        :param width  м, | При отсутствии параметра volume участвует в вычислении общего объема
        :param height  м, | При отсутствии параметра volume участвует в вычислении общего объема
        :param quantity  Количество мест | При отсутствии параметра volume участвует в вычислении общего объема
        :param pickup  Требуется ли забор груза 1 - Да | 0 - нет
        :param delivery  Требуется ли доставка груза 1 - Да | 0 - нет
        :param declared  Объявленная ценность
        :param services  Список дополнительных услуг, через запятую. Коды услуг:
        :param user
        :param token

        """
        if int(kwargs.get("quantity")) == 1:
            total_volume = str(float(kwargs.get("length")) * float(kwargs.get("width")) *
                               float(kwargs.get("height")))
            total_weight = kwargs.get("weight")
        else:
            total_volume = kwargs.get("total_volume")
            total_weight = kwargs.get("total_weight")

        params = {
            "from": kwargs.get("derival_city"),
            "to": kwargs.get("arrival_city"),
            "smart": 1,
            "type": int(kwargs.get("type")),
            "weight": float(total_weight),
            "volume": float(total_volume),
            "length": float(kwargs.get("length")),
            "width": float(kwargs.get("width")),
            "height": float(kwargs.get("height")),
            "quantity": int(kwargs.get("quantity")),
            "pickup": int(pickup),
            "delivery": int(delivery),
            "declared": float(kwargs.get("insurance")),
            "services": services
            # "user": f"{self.jde_user_id}",
            # "token": f"{self.jde_apy_key}"
        }

        return params


if __name__ == "__main__":
    get_params = GetParserParams()
    # print(str(get_params.tomorrow))

    get_params.cdek_get_cities_info('Москва')
    print(1)



