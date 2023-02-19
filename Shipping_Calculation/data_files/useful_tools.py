import json

import requests
import os
from pathlib import Path
import re


shipper_list_full_name = ['ВОЗОВОЗ', 'Деловые Линии', 'ЖелДорЭкспедиция', 'CDEK']
shipper_list = ['ВОЗОВОЗ', 'Деловые', 'ЖДЭ', 'CDEK']

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_json_data = re.sub("Shipping_Calculation.*", "Shipping_Calculation/json_data", dir_path)

def get_cdek_token(client_id, client_secret):
    """Получаем токен, который будет действителен в течении 1 часа
    описание здесь https://api-docs.cdek.ru/29923849.html"""

    url = 'https://api.cdek.ru/v2/oauth/token'
    params = {
        "grant_type": "client_credentials",
        "client_id": f"{client_id}",
        "client_secret": f"{client_secret}"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=params, json=headers)
    cdek_token = response.json()['access_token']

    return cdek_token


def save_popular_cites(city_name: str):
    """Сохранять города которые фигурировали в запросе,
    чтобы не обращаться каждый раз к тяжелым файлам.
    ПРИ ЗАПРОСАХ ДОСТАВКИ ДО АДРЕССА"""
    if os.path.exists(f"{Path(dir_json_data, 'popular_cites.json')}"):
        if os.stat(f"{Path(dir_json_data, 'popular_cites.json')}").st_size != 0:
            with open(f"{Path(dir_json_data, 'popular_cites.json')}", 'r') as f:
                popular = json.load(f)
        else:
            popular = {}
    else:
        with open(f"{Path(dir_json_data, 'popular_cites.json')}", 'w') as f:
          pass
        popular = {}
    with open(f"{Path(dir_json_data, 'delline_full_cites_info.json')}", 'r',
              encoding='utf-8') as f:
        cites_data = json.load(f)

    patern = f"^{city_name.title()}"

    for city in list(cites_data.keys()):
        if re.search(patern, city):
            popular[city] = cites_data[city]
    with open(f"{Path(dir_json_data, 'popular_cites.json')}", 'w') as f:
        json.dump(popular, f, ensure_ascii=False)


def check_cites_on_pop_list(city_name: str):
    """Проверить входит ли в список уже ранее запрашиваемых городов.
    ПРИ ЗАПРОСАХ ДОСТАВКИ ДО АДРЕССА"""
    city_data, data = {}, {}
    patern = f"^{city_name.title()}"
    with open(f"{Path(dir_json_data, 'popular_cites.json')}", 'r') as f:
        popular = json.load(f)
    for city in list(popular.keys()):
        if re.search(patern, city):
            data["city_id"] = popular[city]["city_id"]
            data["kladr"] = popular[city]["kladr"]
            data["name"] = re.sub('_.*', '', city)
            city_data[popular[city]["full_name"]] = data.copy()

    return city_data


def get_kladr_city(city_name):
    checker = check_cites_on_pop_list(city_name)
    if not checker:
        return checker


def save_popular_kladr_street(city_id: str, street_name='Л'):
    if os.path.exists(f"{Path(dir_json_data, 'popular_streets.json')}"):
        if os.stat(f"{Path(dir_json_data, 'popular_streets.json')}").st_size != 0:
            with open(f"{Path(dir_json_data, 'popular_streets.json')}", 'r') as f:
                popular = json.load(f)
        else:
            popular = {}
    else:
        with open(f"{Path(dir_json_data, 'popular_streets.json')}", 'w') as f:
          pass
        popular = {}
    with open(f"{Path(dir_json_data, 'delline_full_streets.json')}", 'r') as f:
        data_st = json.load(f)
    patern = f"^{city_id}_{street_name}"
    for street in list(data_st.keys()):
        if re.search(patern, street):
            popular[street] = data_st[street]
            break  # выходим чтобы не искать все совпадения, т.к. КЛАДР улицы можно взять любой
    with open(f"{Path(dir_json_data, 'popular_streets.json')}", 'w') as f:
        json.dump(popular, f, ensure_ascii=False)


def return_kladr_street(city_id: str, street_name='Л'):
   """Вынесена отдельной функцийей, т.к. будет использоваться внутри другой фунскции"""
   with open(f"{Path(dir_json_data, 'popular_streets.json')}", 'r') as f:
       data = json.load(f)
   patern = f"^{city_id}_{street_name}"
   for street in list(data.keys()):
       if re.search(patern, street):
           return data[street]["kladr_st"]


def get_kladr_street(city_id: str, street_name='Л'):
    if os.path.exists(f"{Path(dir_json_data, 'popular_streets.json')}"):
        if return_kladr_street(city_id=city_id, street_name=street_name):
            return return_kladr_street(city_id=city_id, street_name=street_name)
        else:  # Если вернется пустой словарь добавляем новую улицу в json-файл
            save_popular_kladr_street(city_id=city_id, street_name=street_name)
            return return_kladr_street(city_id=city_id, street_name=street_name)
    else:
        save_popular_kladr_street(city_id=city_id, street_name=street_name)
        return return_kladr_street(city_id=city_id, street_name=street_name)



if __name__ == "__main__":
    # c = get_kladr_street('111')
    c = get_kladr_street('200601')

    print(c)

    # 1000000100000000000000000  кладр ДЛ
    # 1000000100000[:-12]  кладр РФ
