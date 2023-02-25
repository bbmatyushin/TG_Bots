import re

from parser.parsing import FlatInfoParser, DomMinGkhParser, DomMosParser


class BuildingData(FlatInfoParser, DomMinGkhParser, DomMosParser):
    """В FlatInfoParser().get_building_data получаем данные по зданию"""
    def __init__(self):
        super().__init__()
        self.output_result = []

    def get_addr_data(self, address):
        """Здесь происходит поиск нужного адреса через сайт flatinfo.ru
        Если точный адрес не найден, то бот предложит список возможных адресов для уточнения."""
        addr_data = self.flat_get_address_url(address=address)
        if len(addr_data) == 1:
            # return name, url, id, coords
            return addr_data[0] if addr_data[0].get("url") else [addr_data[0]["name"]]
        elif address.strip() in [addr["name"] for addr in addr_data]:
            for i in range(len(addr_data)):
                if addr_data[i]["name"] == address:
                    # name, url, id, coords
                    return addr_data[i]
        elif not addr_data:
            return False  # "Адрес не найден."
        else:
            address_list = [addr["name"] for addr in addr_data]
            return address_list

    def flatinfo_data(self, url):
        """Собираем информацию с сайта flatinfo.ru"""
        flatinfo_dict = {}
        data = self.flat_get_building_data(url)
        if isinstance(data, str):
            return data
        else:
            for i in data.find_all("span", class_="text-darker"):
                if i.text in ["Типовая серия:", "Год постройки:", "Каркас:", "Стены:",
                              "Назначение:", "Этажей всего:", "Подвальных этажей:", "Подъездов:",
                              "Перекрытия:", "Фундамент:", "Подвальных этажей:"]:
                    n = i.next_sibling.next_element
                    flatinfo_dict[i.text] = n.text
            if data.find(string="В квартирах подключен газ"):
                flatinfo_dict["Газоснабжение:"] = data.find(string="В квартирах подключен газ")

            return flatinfo_dict

    def mingkh_data(self, url):
        mingkh_dict = {}
        data = self.mingkh_get_building_data(url=url)
        # Нужного параметра может не быть, тогда значение None
        mingkh_dict["Назначение:"] = data.find("dt", string="Тип дома").next_sibling.next_sibling.text\
            if data.find("dt", string="Тип дома") else None
        mingkh_dict["Типовая серия:"] = data.find("dt", string="Серия, тип постройки").next_sibling.next_sibling.text\
            if data.find("dt", string="Серия, тип постройки") else None
        mingkh_dict["Год постройки:"] = data.find("dt", string="Год постройки").next_sibling.next_sibling.text\
            if data.find("dt", string="Год постройки") else None
        mingkh_dict["Перекрытия:"] = data.find("dt", string="Тип перекрытий").next_sibling.next_sibling.text\
            if data.find("dt", string="Тип перекрытий") else None
        mingkh_dict["Этажей всего:"] = data.find("dt", string="Количество этажей").next_sibling.next_sibling.text\
            if data.find("dt", string="Количество этажей") else None
        # Стены:
        mingkh_dict["Несущие стены:"] = data.find("td", string="Несущие стены").next_sibling.next_sibling.text\
            if data.find("td", string="Несущие стены") else None
        mingkh_dict["Внутр.стены:"] = data.find(string="Тип внутренних стен")\
                                          .next_element.next_element.next_element.text\
            if data.find(string="Тип внутренних стен") else None
        mingkh_dict["Фундамент:"] = data.find(string="Фундамент").next_element.next_element.next_element.text\
            if data.find(string="Фундамент") else None
        mingkh_dict["Площадь подвала:"] = data.find(string="Площадь подвала, кв.м").next_element\
                                              .next_element.next_element.text\
            if data.find(string="Площадь подвала, кв.м") else None
        mingkh_dict["Подъездов:"] = data.find(string="Количество подъездов").next_element.next_element.next_element.text\
            if data.find(string="Количество подъездов") else None
        mingkh_dict["Газоснабжение:"] = data.find(string="Газоснабжение").next_element.next_element.next_element.text\
            if data.find(string="Газоснабжение") else None

        return mingkh_dict

    def dommos_data(self, url):
        dommos_dict = {}
        data = self.dommos_get_building_data(url=url)
        # Нужного параметра может не быть, тогда значение None
        dommos_dict["Назначение:"] = f'многоквартирный дом' \
            if data.find("h1", string=re.compile('Общие сведения о многоквартирном доме')) else None
        dommos_dict["Год постройки:"] = data.find(string=re.compile('Год постройки')).next_element.next_element.text\
            if data.find(string=re.compile('Год постройки')) else None
        dommos_dict["Типовая серия:"] = data.find(string=re.compile('Серия проекта')).next_element.next_element.text\
            if data.find(string=re.compile('Серия проекта')) else None
        #TODO: Смотреть как будет отрабатывать
        dommos_dict["Этажей всего:"] = data.find(string=re.compile('наибольшее')).next_element.next_element.text\
            if data.find(string=re.compile('наибольшее')) else None
        dommos_dict["Подвальных этажей:"] = data.find(string=re.compile('Количество технических подвалов'))\
            .next_element.next_element.text if data.find(string=re.compile('Количество технических подвалов')) \
            else None
        dommos_dict["Подъездов:"] = data.find(string=re.compile('Количество подъездов')).next_element\
            .next_element.text if data.find(string=re.compile('Количество подъездов')) else None

        return dommos_dict



if __name__ == "__main__":
    # url = 'https://dom.mos.ru/Building/Details/cb9c42b4-6ecd-4415-a125-d871fa1b3997'
    url = 'https://dom.mos.ru/Building/Passport?pk=cb9c42b4-6ecd-4415-a125-d871fa1b3997'
    full_addr = 'Москва, Мининский переулок'
    data = BuildingData().get_addr_data(address=full_addr)
    # data = BuildingData().dommos_data(url=url)
    print(data)

