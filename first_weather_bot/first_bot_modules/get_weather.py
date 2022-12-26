import requests
from geopy.geocoders import Nominatim


class TGWeatherBot:

    def __init__(self, appid1, appid2=''):
        self.url = 'http://api.openweathermap.org/data/2.5/find'
        self.appid1 = appid1
        self.appid2 = appid2

    def get_location(self, coordinations: str) -> dict:
        """
        Cordinations in the format 'lav, long'
        Функция вычисляет геоданные (улицу, город, регион и т.д.) по координатам.
        Пока реализовано получения региона.
        """
        try:
            dict_result = {}
            loc_data = Nominatim(user_agent='tutorial')
            location = loc_data.reverse(coordinations).raw['address']
            dict_result['region'] = location['state']
            return dict_result
        except Exception as e:
            return f'Some ERROR: {e} ...( ╯°□°)╯'

    def get_result(self, city_name):
        result = []
        try:
            params = {
                'q': city_name + ',RU',
                'type': 'like',
                'units': 'metric',
                'lang': 'RU',
                'APPID': self.appid1
            }
            response = requests.get(self.url, params=params)
            if response.status_code == 200:
                # если запрос выполнен успешно, собираем данные
                data = response.json()
                if data['list'] == []:
                    # Если нет такого города, то выводим сообщение
                    return f'No data by "{city_name}" ¯\_(ツ)_/¯'
                else:
                    cities = [d["name"] for d in data['list']]
                    temp = [t['main']['temp'] for t in data['list']]
                    coord_dict = [c['coord'] for c in data['list']]
                    coord_list = [f'{str(coord_dict[i]["lat"])}, {str(coord_dict[i]["lon"])}'
                                  for i in range(len(coord_dict))]
                    descriptions = [data['list'][j]['weather'][0]['description']
                                    for j in range(len(data['list']))]
                    # через get_location получаем список словарей с регионами
                    locations = list(map(self.get_location, coord_list))
                    # формируем сообщения для вывода пользователю
                    for i in range(len(cities)):
                        result.append(f'Temperature in the {cities[i]} [{locations[i]["region"]}]: '
                                      f'"{temp[i]}°C" and "{descriptions[i]}".')
                    return '\n\n'.join(result)
        except Exception as e:
            return f'Some ERROR: {e} ...( ╯°□°)╯'


    def chat_message(self, user_text):
        """
        хотел сделать отдельную функцию для вывода сообщения
        """
        # end_result_list = get_result(user_text)
        pass


if __name__ == 'first_bot_modules.get_weather':
    """ Module guide """
    # print('Module guide')