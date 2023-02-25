import requests
import re
import time
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
            if not response.json()["list"] and response.json()["url"]:
                url = response.json()["url"]
                return self.flat_check_url(url=url)
            elif response.json()["list"]:
                return response.json()["list"]
            elif not response.json()["list"] and not response.json()["url"]:
                return []
        else:
            return False

    def flat_check_url(self, url):
        """КОСТЫЛЬ. Если есть единственный url, то заходим на эту страницу
        и вытаскиваем адресс, чтобы ещё раз через поиск его пропустить"""
        session = requests.Session()
        session.headers.update(self.headers)
        # time.sleep(1)
        res = session.get(url=url, headers=self.headers)
        soup = BeautifulSoup(res.text, 'lxml')
        get_addr = soup.find("h1", string=re.compile('[Оо] дом?')).text
        addr_parts = re.sub(r'[Оо] доме', '', get_addr).strip().split(' в ')
        new_addr = f"{addr_parts[1]}, {addr_parts[0]}"
        url = 'https://flatinfo.ru/services/adres_response.php'
        params = {"term": new_addr}
        time.sleep(1)
        response = session.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            if response.json()["list"]:
                return response.json()["list"]
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
        street = re.sub(r'\s+', ' ', re.sub(r'\b(?:улица|дом|переулок|бульвар|владение|шоссе|проезд|корпус)\b', '',
                                            addr_list[1])).strip()#.split()
        street_name = re.search(r'[а-яёА-ЯЁ\s-]+', street)[0].strip()  # нужны для формирования патерна для regex
        house_num = re.sub(r'\s+', ' ', street.replace(street_name, "").strip())
        # house_num = re.findall(r'\d+|\d+[а-яёА-ЯЁ]+', street)
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
                if re.search(f'{city}', data[i].text):
                    if re.search(f'\\b({street_name})\\b.*({re.sub(" ", ".*", house_num)})', data[i + 1].text):
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
    parser = DomMinGkhParser()
    # parser = DomMosParser()
    addr = 'Москва, проезд Соломенной Сторожки дом 5 корпус 1'  #TODO: Москва, Новолесная улица 17А - плохо отработало на ДОМ.МИНЖКХ (выдача 17/21)
    url_b = 'https://dom.mos.ru/Building/Details/dc722b5c-f9dc-4a59-b24b-5b72661eba7a'  # for example
    data = parser.mingkh_get_address_url(address=addr)

    print(data)

    #Москва, 5-й Донской проезд дом 21 корпус 9

