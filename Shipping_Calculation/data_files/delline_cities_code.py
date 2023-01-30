import json
from parsing.parser import ShippingParser


class DellineCitiesCode:
    def __init__(self):
        self.file_name = 'delline_cities_code.json'

    def collect_cities_code_dl(self):
        parser = ShippingParser()
        code_collect = {}
        with open(f'{self.file_name}', 'w', encoding='utf-8') as f:
            data = parser.get_cities_code_delline()
            for i in range(len(data)):
                for k, v in data[i].items():
                    if k == 'city':
                        c = v
                    if k == 'kladr':
                        kl = v
                        code_collect[c] = kl
            json.dump(code_collect, f)

    def extract_cities_code_dl(self):
        """Получаем словарь Город: Код_города (код который принимает Деловые Линии).
        Так же можем извлечь список городов."""
        try:
            with open(f'{self.file_name}') as f:
                cities = json.load(f)
                return cities
        except FileNotFoundError:
            self.collect_cities_code_dl()

    # def ex


if __name__ == "__main__":
    cities = DellineCitiesCode()
    # cities.collect_cities_code_dl()
    data = cities.extract_cities_code_dl()
    print(1)