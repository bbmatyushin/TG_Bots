"""Сбор информации по названиям города, их ID, ID терминалов Деловых Линий и т.п. """
import os
from pathlib import Path
import requests
import json

from fake_headers import Headers

from data_files.data_file import API_DELLINE
from data_files import useful_tools as ut


class DellineTerminals:
    def __init__(self):
        self.api_delline = API_DELLINE
        self.path_json_data = ut.dir_json_data

    def delline_download_terminals(self) -> None:
        """Получить полный список всех терминалов Деловых"""
        url = 'https://api.dellin.ru/v3/public/terminals.json'
        params = {"appkey": self.api_delline}
        headers = Headers().generate()
        response = requests.post(url, headers=headers, json=params).json()
        terminals = requests.get(url=response["url"], headers=headers).json()
        with open(f"{Path(self.path_json_data, 'delline_data_terminals.json')}", "w") as f:
            json.dump(terminals, f, ensure_ascii=False)

    def delline_local_file_terminal(self) -> None:
        """Сохранять ID терминалов в отдельный файл, чтобы быстрее их от туда доставать"""
        if os.path.exists(f"{Path(self.path_json_data, 'delline_data_terminals.json')}"):
            pass
        else:
            self.delline_download_terminals()
        with open(f"{Path(self.path_json_data, 'delline_data_terminals.json')}", "r") as f:
            data_dict, feater_dict = {}, {}
            terminals_id = json.load(f)
            for _ in terminals_id["city"]:
                feater_dict["terminal_id"], feater_dict["city_kladr"] = \
                    _["terminals"]["terminal"][0]["id"], _["code"]
                data_dict[_["name"]] = feater_dict.copy()
            with open(f"{Path(self.path_json_data, 'delline_city_kladr_terminalid.json')}",
                      "a", encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False)

    def delline_get_delivery_terminal_data(self) -> dict:
        """Получить данные для межтерминальной перевозки.
         Нужно указать город, чтобы получить terminal_id, city_kladr"""
        if os.path.exists(f"{Path(self.path_json_data, 'delline_city_kladr_terminalid.json')}"):
            pass
        else:
            self.delline_local_file_terminal()
        with open(f"{Path(self.path_json_data, 'delline_city_kladr_terminalid.json')}") as f:
            data = json.load(f)

        return data

    def delline_search_express_terminal(self, city_kladr):
        """Поиск терминала по КЛАДР города, чтобы узнать есть там
        экспресс доставка."""
        url = 'https://api.dellin.ru/v1/public/request_terminals.json'
        params = {
            "appkey": self.api_delline,
            "code": city_kladr
        }
        headers = Headers().generate()
        response = requests.post(url, json=params, headers=headers).json()
        terminals = dict(express=[el["id"] for el in response["terminals"] if el["express"]],
                         auto=[el["id"] for el in response["terminals"] if not el["express"]])
        return terminals

    def delline_search_city(self, city_search: str):
        """Поиск данных по города по его названию или части названия
        ПОКА НЕ ИСПОЛЬЗУЕТСЯ"""
        url = 'https://api.dellin.ru/v2/public/kladr.json'
        params = {
            "appkey": self.api_delline,
            "q": city_search,
            "limit": 10
        }
        response = requests.post(url, json=params).json()
        return response

    def delline_get_streets_info(self):
        """Справочник улиц Деловых"""
        url = 'https://api.dellin.ru/v1/public/streets.json'
        params = {
            "appkey": self.api_delline
        }
        response = requests.post(url, json=params).json()
        return response

    def delline_get_place_info(self):
        """Справочник населенных пунктов"""
        url = 'https://api.dellin.ru/v1/public/places.json'
        params = {
            "appkey": self.api_delline
        }
        response = requests.post(url, json=params).json()
        return response

    def delline_get_full_city_list(self):
        """Данные буруться из скаченного справочника населенных пунктов
        Переводится в формат json для удобного обращения и поиска внутри файла"""

        data, temp_data = {}, {}
        with open(f"{Path(ut.dir_json_data, 'delline_places.csv')}", "r",
                  encoding='utf-8') as f:
            for line in f:
                l = line.rstrip().replace('"', '').split(',')
                # temp_data["city_name"] = l[3]
                temp_data["city_id"] = l[0]
                temp_data["full_name"] = l[1]
                temp_data["kladr"] = l[2]
                temp_data["reg_name"] = l[4]
                temp_data["reg_kladr"] = l[7]
                if temp_data["kladr"][2] == '0':  # вроде бы так мы отсекаем не Российские города
                    data[f"{l[3]}_{l[0]}"] = temp_data.copy()
                # data.append(temp_data.copy())

        with open(f"{Path(ut.dir_json_data, 'delline_full_cites_info.json')}", 'w',
                  encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)

    def delline_get_full_street_list(self):
        """Данные буруться из скаченного справочника улиц
        Переводится в формат json для удобного обращения и поиска внутри файла.
        Ключом будет codeID города."""

        data, temp_data = {}, {}
        with open(f"{Path(ut.dir_json_data, 'delline_streets.csv')}", "r",
                  encoding='utf-8') as f:
            for line in f:
                l = line.rstrip().replace('"', '').split(',')
                # temp_data["city_id"] = l[1]
                temp_data["full_name"] = l[3]
                temp_data["name"] = l[2]
                temp_data["kladr_st"] = l[0]
                data[f'{l[1]}_{l[2]}'] = temp_data.copy()

        with open(f"{Path(ut.dir_json_data, 'delline_full_streets.json')}", 'w',
                  encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)


class DellinePackages(DellineTerminals):

    def delline_get_packages_info(self) -> None:
        url = 'https://api.dellin.ru/v1/public/request_services.json'
        params = {"appkey": self.api_delline}
        headers = Headers().generate()
        response = requests.post(url, headers=headers, json=params).json()
        packages_info = requests.get(url=response["url"], headers=headers)
        with open(f"{Path(self.path_json_data, 'delline_packages_info.csv')}", "w") as f:
            f.write(packages_info.text)


if __name__ == "__main__":
    cl = DellinePackages()
    city_kladr = '9100000700000000000000000'
    city_search = 'Москва'
    data = cl.delline_get_full_street_list()
    # print(data)

    # terminal_id["city"][0]["name"] - город
    # terminal_id["city"][0]["terminals"]["terminal"][0]["id"] - id терминала