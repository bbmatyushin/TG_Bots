from functools import reduce
import datetime

from parsing.parser import GetParserParams
from data_files.delline_cities_code import DellineCitiesCode
from parsing.parser import ShippingParser
from data_files.shippers_and_cities_list import shipper_list


class DellineCalculation:
    def __init__(self):
        self.parser = ShippingParser()
        self.params = GetParserParams()
        self.city_code = DellineCitiesCode().extract_cities_code_dl()

    def delline_get_data(self, request_type='cargo-single', length='0.3', width='0.35', height='0.4',
                         sized_weight='10', sized_volume='0.15', max_length='0.3', max_width='0.35',
                         max_height='0.4', max_weight='10', quantity='1', total_weight='10',
                         total_volume='0.15', stated_value='100000', arrival_variant="toDoor",
                         arrival_prr='0', derival_city='Санкт-Петербург', arrival_city='Москва'):
        """Сюда пользователь будет вводить параметра для расчета доставки груза"""
        try:
            derival_point_code = self.city_code[derival_city.title()]  # пишем город с большой буквы
            arrival_point_code = self.city_code[arrival_city.title()]
            params = \
                self.params.delline_params(request_type=request_type, length=length, width=width, height=height,
                                           sized_weight=sized_weight, sized_volume=sized_volume, max_length=max_length,
                                           max_width=max_width, max_height=max_height, max_weight=max_weight,
                                           quantity=quantity, total_weight=total_weight, total_volume=total_volume,
                                           stated_value=stated_value, arrival_variant=arrival_variant,
                                           arrival_prr=arrival_prr, derival_point_code=derival_point_code,
                                           arrival_point_code=arrival_point_code)
            data = self.parser.delline_parser(params=params)

            return data

        except KeyError:
            return f'Нет данных для расчета доставки: {derival_city} - {arrival_city}.'

    def delline_simple_calc(self, request_type='cargo-single', length='0.4', width='0.35', height='0.3',
                            sized_weight='10', sized_volume='0.05', stated_value='100000',
                            derival_city='Санкт-Петербург', arrival_city='Москва',
                            arrival_variant="", arrival_prr="0"):
        """Расчет простой доставки - между терминалами, без ПРР, одно место, не экспресс
        Пользователю достаточно ввести только города отправки и получения."""

        data = self.delline_get_data(request_type=request_type, length=length, width=width, height=height,
                                     sized_weight=sized_weight, sized_volume=sized_volume,
                                     derival_city=derival_city, arrival_city=arrival_city,
                                     stated_value=stated_value,
                                     arrival_variant=arrival_variant, arrival_prr=arrival_prr)
        status_info = data.get("fatal_informing")  # информирование о статусе
        insurance = data.get("insurance")  # страхование груза
        term_insurance = data.get("term_insurance")  # страхование сроков
        intercity = data.get("intercity")  # межтерминальная перевозка
        arrival_terminal_price = data.get("arrival_terminal_price")  # въезд на терминал
        derival_terminal_price = data.get("derival_terminal_price")  # въезд на терминал
        # arrival_to_door = data.get("arrivalToDoor")  # Доставить груз до адреса получателя
        # derival_to_door = data.get("derivalToDoor")  # Забрать груз от адреса отправителя
        # express = data.get("express")  # Экспресс - перевозка
        # unloading = data.get("unloading")  # Разгрузочные работы (бесплатно при весе до 15 кг)

        result = reduce(lambda a, b: float(a) + float(b), [status_info, insurance, term_insurance, intercity,
                                                           arrival_terminal_price, derival_terminal_price])

        shipment_day = data.get("sender_terminal_arrival_date")
        if shipment_day:
            receipt_day = data.get("recipient_terminal_arrival_date")
            shipping_days = (datetime.datetime.strptime(receipt_day, '%Y-%m-%d').date() -
                             datetime.datetime.strptime(shipment_day, '%Y-%m-%d').date()).days
        else:
            shipping_days = '1'

        return result, shipping_days


class TotalResult(DellineCalculation):
    def __init__(self):
        super().__init__()
        self.shipper_list = shipper_list

    def get_simple_result(self, length='0.4', width='0.35', height='0.3', weight='10', volume='0.05',
                          stated_value='100000',
                          derival_city='Санкт-Петербург', arrival_city='Москва'):

        delline_calc = self.delline_simple_calc(length=length, width=width, height=height,
                                                sized_weight=weight, sized_volume=volume,
                                                stated_value=stated_value,
                                                derival_city=derival_city, arrival_city=arrival_city)

        output = [f"Расчет межтерминальной перевозки *{derival_city}* - *{arrival_city}*.\n"
                  f"*Габариты груза:* Д×Ш×В - {length}×{width}×{height} м\n"
                  f"*Вес:* {weight} кг, *Объём:* {volume} м3\n"
                  f"------------------------------\n"
                  f"*{self.shipper_list[0]}* - {delline_calc[0]:,} руб., срок доставки *{delline_calc[1]} дн.*\n"
                  f"------------------------------"]

        return "".join(output)


if __name__ == "__main__":
    dl_pars = DellineCalculation()
    derival_city = 'Тверь'
    arrival_city = 'Тверь'
    result = TotalResult().get_simple_result(derival_city=derival_city, arrival_city=arrival_city)
    print(result)

    # prr = '1'
    # data = dl_pars.get_data(derival_city=derival_city, arrival_city=arrival_city, arrival_prr=prr)
    #
    # print(f'1 - {data.get("accompanying_documents")}')
    # print(f'2 - {data.get("arrivalToDoor")} - Доставить груз до адреса получателя')
    # print(f'3 - {data.get("commercialMail")}')
    # print(f'4 - {data.get("derivalToDoor")} - Забрать груз от адреса отправителя')
    # print(f'5 - {data.get("express")} - Экспресс-перевозка')
    # print(f'6 - {data.get("fatal_informing")} - информирование о статусе')
    # print(f'7 - {data.get("insurance")} - страхование груза')
    # print(f'8 - {data.get("intercity")} - межтерминальная перевозка')
    # print(f'9 - {data.get("term_insurance")} - страхование сроков')
    # print(f'10 - {data.get("unloading")} - Разгрузочные работы (бесплатно при весе до 15 кг)')

    print('\n1')
