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
        self.main_url = 'https://dom.mingkh.ru'
        self.headers = Headers().generate()

    def mingkh_get_address_url(self, address):
        """Адрес из FlatInfo преобразуем в адрес вида сайта
        ДОМ.МИНЖКХ и вытаскиваем ссылку на страницу здания"""
        addr_list = address.split(",")
        city = addr_list[0].strip()
        street = addr_list[1].strip().replace("улица", "").replace("дом", "").replace("переулок", '')\
            .replace("бульвар", "").replace("владение", "").strip()
        street = re.sub("\s+", " ", street).lower()
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
                if city in data[i].text:
                    if street in re.sub("\s+", " ", data[i + 1].text.replace("пер.", "").replace(",", '')
                                        .replace("б-р", '')).lower():
                        # получаем ссылку на страницу строения
                        return self.main_url + data[i + 1].find("a")["href"]
            return False

    def mingkh_get_building_data(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            data = soup.find("div", class_='main-block')
            return data
        else:
            return "Bab response ¯\_(ツ)_/¯"


if __name__ == "__main__":
    # parser = FlatInfoParser()
    parser = DomMinGkhParser()
    addr = 'Москва, бульвар Дмитрия Донского дом 17'
    url_b = 'https://dom.mingkh.ru/moskva/moskva/404449'  # for example
    # response = parser.flat_get_address_url(address=addr)
    data = parser.mingkh_get_building_data(url=url_b)

    print(data)

    #Москва, 5-й Донской проезд дом 21 корпус 9
