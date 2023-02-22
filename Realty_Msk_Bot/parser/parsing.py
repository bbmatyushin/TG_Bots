import requests
import re
from bs4 import BeautifulSoup
from fake_headers import Headers


class FlatInfoParser:
    def __init__(self):
        self.headers = Headers().generate()

    def flat_get_address_url(self, address: str):
        """Получаем url нужного адреса"""
        url = 'https://flatinfo.ru/services/adres_response.php'
        params = {"term": address}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            address_info = response.json()["list"]
            return address_info
        else:
            return False

    def flat_get_building_data(self, url):
        """Аргументом служит url конкретной улицы полученный из
        get_address_url -> address_info[0]['url']"""
        response = requests.get(url=url, headers=self.headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            data = soup.find("ul", class_="lsn list-to-house")

            return data
        else:
            return "Bab response ¯\_(ツ)_/¯"


class DomMinGkhParser:
    def __init__(self):
        self.main_mingkh_url = 'https://dom.mingkh.ru'
        self.headers = Headers().generate()

    def mingkh_get_address_url(self, address):
        """Адрес из FlatInfo преобразуем в адрес вида сайта
        ДОМ.МИНЖКХ и вытаскиваем ссылку на страницу здания"""
        addr_list = address.split(",")
        city = addr_list[0].strip()
        street = re.sub(r'\s+', ' ', re.sub(r'\b(?:улица|дом|переулок|бульвар|владение|шоссе|проезд)\b', '',
                                            addr_list[1])).lower().strip().split()
        str_part1, str_part2 = street[0], street[1]  # нужны для формирования патерна для regex
        url = 'https://dom.mingkh.ru/search'
        params = {
            "address": address,
            "searchtype": "house"
        }
        response = requests.get(url=url, params=params, headers=self.headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            data = soup.find("tbody").find_all("td")
            for i in range(len(data) - 1):
                if re.search(f'{city}', data[i].text, flags=re.ASCII):
                    if re.search(f'\\b({str_part1})\\b.*\\b({str_part2})\\b', data[i + 1].text.lower()):
                        # получаем ссылку на страницу строения
                        return self.main_mingkh_url + data[i + 1].find("a")["href"]
            return False

    def mingkh_get_building_data(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            data = soup.find("div", class_='main-block')
            return data
        else:
            return "Bab response ¯\_(ツ)_/¯"


class DomMosParser:
    def __init__(self):
        self.main_dommos_url = 'https://dom.mos.ru'
        self.search_url_dommos = 'https://dom.mos.ru/Lookups/GetSearchAutoComplete'
        self.headers = Headers().generate()
        #?term=проезд Серебрякова, дом 1/2&section=Buildings'

    def dommos_get_building_url(self, address: str):
        """Получить url здания по его адресу.
        В адресе не должно быть города, только улица."""

        addr_list = address.split(",")
        city = addr_list[0].strip()
        street = addr_list[1].strip()
        # Разделяем адрес на 2 части, чтобы собрать патерн для регулярки
        str_format = street.replace(" дом", ", дом").strip().split(", ")
        str_part1, str_part2 = str_format[0], re.findall(r'\b(\D+\d+)\b', str_format[1])
        patern = ").*(".join([str_part1, *str_part2])

        params = {
            "term": street,
            "section": "Buildings"
        }
        response = requests.get(url=self.search_url_dommos, headers=self.headers, params=params)

        if city == 'Москва':  # ищем только Для москвы
            if response.status_code == 200:
                for el in response.json():
                    url = f'{self.main_dommos_url}{el["url"]}' if re.search(f'({patern})', el.get('value')) else None
                    return re.sub(r'Details/', r'Passport?pk=', url) if url else None
            else:
                return None
        else:
            return None

    def dommos_get_building_data(self, url):
        response = requests.get(url=url, headers=self.headers)

        soup = BeautifulSoup(response.text, 'lxml')
        data = soup.find("div", class_="rndBrdBlock mrgT18")

        return data


if __name__ == "__main__":
    # parser = FlatInfoParser()
    # parser = DomMinGkhParser()
    parser = DomMosParser()
    addr = 'Москва, 5-й Донской проезд дом 21 корпус 9'
    url_b = 'https://dom.mos.ru/Building/Details/dc722b5c-f9dc-4a59-b24b-5b72661eba7a'  # for example
    response = parser.dommos_get_building_url(address=addr)
    # data = parser.dommos_get_building_data(url_b)

    # print(data)

    #Москва, 5-й Донской проезд дом 21 корпус 9

