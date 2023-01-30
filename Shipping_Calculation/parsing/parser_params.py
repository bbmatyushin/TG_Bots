import datetime


class GetParserParams:
    def __init__(self):
        self.today = datetime.datetime.now().date().strftime('%d.%m.%Y')
        self.tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).date().strftime('%d.%m.%Y')

    def delline_params(self, request_type='cargo-single', length='0.3', width='0.35', height='0.4',
                       sized_weight='10', sized_volume='0.15', max_length='0.3', max_width='0.35',
                       max_height='0.4', max_weight='10', quantity='1', total_weight='16',
                       total_volume='0.15', stated_value='100000', arrival_variant="toDoor",
                       arrival_prr='1', derival_point_code='7800000000000000000000000',
                       arrival_point_code='7700000000000000000000000') -> dict:
        """ Размеры в метрах,
            Вес в кг,
            Объем в м3 
            :rtype: object"""

        params = {
            "requestType": f"{request_type}",  # cargo-multi  - если несколько мест
            "delivery_type": "1",
            "length": f"{length}",  # одно место
            "width": f"{width}",  # одно место
            "height": f"{height}",  # одно место
            "sized_weight": f"{sized_weight}",  # одно место
            "sized_volume": f"{sized_volume}",  # одно место
            "max_length": f"{max_length}",  # несколько мест
            "max_width": f"{max_width}",  # несколько мест
            "max_height": f"{max_height}",  # несколько мест
            "max_weight": f"{max_weight}",  # несколько мест
            "quantity": f"{quantity}",
            "total_weight": f"{total_weight}",  # несколько мест
            "total_volume": f"{total_volume}",  # несколько мест
            "stated_value": f"{stated_value}",
            "arrival_variant": f"{arrival_variant}",
            "produceDate": f"{self.today}",
            "arrival_prr": f"{arrival_prr}",
            "derival_point_noSendDoor": "0",
            "cabinet": "false",
            "derival_point_code": f"{derival_point_code}",
            "arrival_point_code": f"{arrival_point_code}"
        }

        return params


if __name__ == "__main__":
    get_params = GetParserParams()
    print(get_params.tomorrow)



