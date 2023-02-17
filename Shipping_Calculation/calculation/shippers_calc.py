import datetime
import timeit

from parsing.parser_params import GetParserParams
from json_data.delline_get_data_info import DellineTerminals
from data_files import useful_tools as ut
from parsing.parser import DellineParser, VozovozParser, CdekParser, JDEParser


class ShippersTerminalCalculation:
    def __init__(self):
        self.delline_parser = DellineParser()
        self.vozovoz_parser = VozovozParser()
        self.cdek_parser = CdekParser()
        self.jde_parser = JDEParser()
        self.params = GetParserParams()
        self.delline_cities_terminal = DellineTerminals().delline_get_delivery_terminal_data()

        """total_volume = '0', quantity = '1', weight = '10', total_weight = '0',
        length = '0.4', width = '0.35', height = '0.3', insurance = '50000',
        delivery_type='auto', derival_city = 'Москва', arrival_city = "Санкт-Петербург"""

    def delline_terminal_calc(self, total_volume='0', quantity='1', weight='8', total_weight='0',
                              length='0.3', width='0.2', height='0.25', insurance='50000',
                              derival_city='Москва', arrival_city="Санкт-Петербург",
                              delivery_type='auto'):

        if delivery_type == 'express':
            delivery_kladr = self.delline_cities_terminal[derival_city]['city_kladr']
            arrival_kladr = self.delline_cities_terminal[arrival_city]['city_kladr']
            delivery_express = DellineTerminals().delline_search_express_terminal(delivery_kladr)["express"]
            arrival_express = DellineTerminals().delline_search_express_terminal(arrival_kladr)["express"]
            if not delivery_express:  # если вернется пустой список, т.е. нет терминала под экспресс доставку
                return f"Эксперсс доставка из г.{derival_city} невозможна."
            if not arrival_express:
                return f"Эксперсс доставка в г.{arrival_city} невозможна."

        params = self.params.delline_params(total_volume=total_volume, quantity=quantity, weight=weight,
                                            total_weight=total_weight, length=length, width=width,
                                            height=height, insurance=insurance,
                                            derival_city=derival_city, arrival_city=arrival_city,
                                            delivery_type=delivery_type)

        data = self.delline_parser.delline_get_data(params=params)

        if isinstance(data, dict):
            price = data.get("price")
            shipment_day = data.get("orderDates").get("derivalFromOspSender")
            receipt_day = data.get("orderDates").get("arrivalToOspReceiver")
            shipping_days = (datetime.datetime.strptime(receipt_day, '%Y-%m-%d').date() -
                             datetime.datetime.strptime(shipment_day, '%Y-%m-%d').date()).days

            return price, shipping_days
        else:
            return data

    def vozovoz_terminal_calc(self, quantity='1', weight='8', length='0.3', width='0.2', height='0.25',
                              total_weight='10', total_volume='0', insurance='100000',
                              derival_city='Москва', arrival_city="Санкт-Петербург"):

        params = self.params.vozovoz_params(quantity=quantity, weight=weight,
                                            length=length, width=width, height=height,
                                            total_weight=total_weight, total_volume=total_volume,
                                            insurance=insurance,
                                            derival_city=derival_city, arrival_city=arrival_city)

        data = self.vozovoz_parser.vozovoz_get_data(params)

        if data.get("error"):  # возможны ошибки. Если они есть, то берем только её текст
            if 'Перевозка между ППВ запрещена' in data["error"]["message"]:
                return "_Межтерминальная перевозка не осуществляется._"
            else:
                return data["error"]["message"]
        else:
            price = float(data["response"]["price"])
            date_from = data["response"]["deliveryTime"]["from"]  # срок доставки от
            date_to = data["response"]["deliveryTime"]["to"]  # срок доставки до
            if date_from == date_to:
                return price, date_to
            else:  # если даты разные то вернем сроки в виде 1-4
                return price, "-".join(map(str, [date_from, date_to]))

    def cdek_terminal_calc(self, weight='8', length='0.3', width='0.2', height='0.25',
                           delivery_type='auto', insurance='100000',
                           derival_city='Москва', arrival_city="Санкт-Петербург"):
        """Тариф для расчета = Посылка склад-склад, режим доставки = склад -склад - это код 136
        код 483 - Экспресс склад-склад (https://api-docs.cdek.ru/63345519.html) """
        tariff_code = 483 if delivery_type == 'express' else 136

        params = self.params.cdek_params(weight=weight, length=length, width=width, height=height,
                                         tariff_code=tariff_code, insurance=insurance,
                                         derival_city=derival_city, arrival_city=arrival_city)

        try:
            data = self.cdek_parser.cdek_get_data(params)

            if float(weight) <= 30.0:
                price, date_from, date_to = data["total_sum"], data["period_min"], data["period_max"]
                if date_from == date_to:
                    return price, date_to
                else:  # если даты разные то вернем сроки в виде 1-4
                    return price, "-".join(map(str, [date_from, date_to]))
            else:
                return "_Доставка Склад-Склад доступна только для грузов весом менее 30 кг._"
        except KeyError:
            return "_Доставка Склад - Склад невозможна._"
        
    def jde_calc(self, quantity='1', weight='8', length='0.3', width='0.2', height='0.25',
                 total_weight='10', total_volume='0', insurance='100000',
                 derival_city='Москва', arrival_city="Санкт-Петербург",
                 delivery_type='auto',  # такое значение как в Деловых для однообразия
                 pickup='0', delivery='0', services=''):

        type = '2' if delivery_type == "express" else '1'

        params = self.params.jde_params(quantity=quantity, weight=weight, length=length,
                                        width=width, height=height, total_weight=total_weight,
                                        total_volume=total_volume, insurance=insurance,
                                        derival_city=derival_city, arrival_city=arrival_city,
                                        type=type, pickup=pickup, delivery=delivery, services=services)

        try:
            data = self.jde_parser.jde_get_data(params)
            if isinstance(data, dict):
                price = data.get("price")
                mindays = data.get("mindays")
                maxdays = data.get("maxdays")
                if mindays == maxdays:
                    return price, maxdays
                else:
                    return price, "-".join([mindays, maxdays])
            elif isinstance(data, str):
                return data
        except:
            return "_Межтерминальная перевозка не осуществляется._"


class TotalTerminalResult(ShippersTerminalCalculation):
    def __init__(self):
        super().__init__()
        self.shipper_list = ut.shipper_list
        self.output_footer = []

        """ ==== Минимальный набор kwargs: ====
        total_volume = '0', quantity = '1', weight = '10', total_weight = '0',
        length = '0.4', width = '0.35', height = '0.3', insurance = '50000',
        derival_city = 'Москва', arrival_city = "Санкт-Петербург"""

    def get_simple_result(self, total_volume='0', total_weight='0', quantity='1', weight='8',
                          length='0.3', width='0.2', height='0.25', insurance='50000',
                          derival_city='Москва', arrival_city="Санкт-Петербург",
                          delivery_type='auto',
                          pickup='0', delivery='0', services=''):  # эти аргументы для Желдорэкспедиции

        derival_city = derival_city.title()
        arrival_city = arrival_city.title()

        if float(total_volume) == 0.0:
            n = round((float(length) * float(width) * float(height)), 2)
            get_total_volume = '0.01' if n < 0.01 else str(n)
        else:
            get_total_volume = total_volume

        # Проверяем входят ли города в список городов с терминалами ДЛ
        # if derival_city not in list(self.delline_cities_terminal.keys())  #TODO: проверить по одельности каждый город
        if all([list(self.delline_cities_terminal.keys()).count(derival_city),
                list(self.delline_cities_terminal.keys()).count(arrival_city)]):

            delline_calc = self.delline_terminal_calc(total_volume=get_total_volume, quantity=quantity, weight=weight,
                                                      total_weight=total_weight, length=length, width=width,
                                                      height=height, insurance=insurance,
                                                      derival_city=derival_city, arrival_city=arrival_city,
                                                      delivery_type=delivery_type)
            if len(delline_calc) == 2:
                delline_result = f'{delline_calc[0]:,} ₽, срок *{delline_calc[1]} дн.*'
            else:
                delline_result = delline_calc
        else:
            delline_result = "_Межтерминальная перевозка не осуществляется._"

        vozovoz_calc = self.vozovoz_terminal_calc(quantity=quantity, weight=weight,
                                                  length=length, width=width, height=height,
                                                  total_weight=weight, insurance=insurance,
                                                  derival_city=derival_city, arrival_city=arrival_city)
        if len(vozovoz_calc) == 2:
            vozovoz_result = f"{vozovoz_calc[0]:,} ₽, срок *{vozovoz_calc[1]} дн.*"
        else:
            vozovoz_result = vozovoz_calc

        if quantity == '1':
            cdek_calc = self.cdek_terminal_calc(weight=weight, length=length, width=width, height=height,
                                                insurance=insurance,
                                                derival_city=derival_city, arrival_city=arrival_city)
            if len(cdek_calc) == 2:
                cdek_result = f"{cdek_calc[0]:,} ₽, срок *{cdek_calc[1]} дн.*"
            else:
                cdek_result = cdek_calc
        else:
            cdek_result = f"Для количества мест больше 1 расчет не реализован."

        jde_calc = self.jde_calc(quantity=quantity, weight=weight, length=length, width=width,
                                 height=height, total_weight=total_weight, total_volume=get_total_volume,
                                 insurance=insurance, derival_city=derival_city, arrival_city=arrival_city,
                                 delivery_type=delivery_type,   # такое значение как в Деловых для однообразия
                                 pickup=pickup, delivery=delivery, services=services)
        if len(jde_calc) == 2:
            jde_result = f"{float(jde_calc[0]):,} ₽, срок *{jde_calc[1]} дн.*"
        else:
            jde_result = jde_calc


        if quantity == '1':
            output_head = [f"Расчет межтерминальной перевозки *{derival_city}* - *{arrival_city}*\n"
                           f"------------------------------\n"
                           f"📦 _Параметры груза:_\n"
                           f"*Габариты:* {length}×{width}×{height} м (Д×Ш×В)\n"
                           f"*Вес:* {weight} кг, *Объём:* {float(get_total_volume):.2f} м3\n"
                           f"*Объявленная стоимость:* {float(insurance):,.0f} ₽\n"
                           f"------------------------------\n"]
        else:
            output_head = [f"Расчет межтерминальной перевозки *{derival_city}* - *{arrival_city}*.\n"
                           f"------------------------------\n"
                           f"📦 _Параметры груза:_\n"
                           f"*Всего мест:* {quantity}, *Общий вес:* {total_weight} кг,\n"
                           f"*Общий объём:* {float(get_total_volume):.2f} м3, \n"
                           f"*Самое большое место:* {length}×{width}×{height} м\n"
                           f"*Объявленная стоимость:* {float(insurance):,.0f} ₽\n"
                           f"------------------------------\n"]
        if delivery_type == 'express':
            self.output_footer = [f"◗ *{self.shipper_list[0]}* - {vozovoz_result}\n"
                                  f"⚡️ *{self.shipper_list[1]}* - {delline_result}\n"  # есть экспресс доставка
                                  f"⚡️ *{self.shipper_list[2]}* - {jde_result}\n"  # есть экспресс доставка
                                  f"⚡️ *{self.shipper_list[3]}* - {cdek_result}\n"  # есть экспресс доставка
                                  f"------------------------------"]
        else:
            self.output_footer = [f"◗ *{self.shipper_list[0]}* - {vozovoz_result}\n"
                                  f"◗ *{self.shipper_list[1]}* - {delline_result}\n"
                                  f"◗ *{self.shipper_list[2]}* - {jde_result}\n"
                                  f"◗ *{self.shipper_list[3]}* - {cdek_result}\n"
                                  f"------------------------------"]
        output = [*output_head, *self.output_footer]

        return "".join(output)
        # return output_head, self.output_footer


if __name__ == "__main__":
    #TODO: Добавить экспресс доставку для СДЭК (смениться тариф)
    data_calc = ShippersTerminalCalculation()
    calculation_ = TotalTerminalResult()
    derival_city = 'Москва'
    arrival_city = 'Самара'
    data = calculation_.get_simple_result(delivery_type="auto")
    # data = calculation_.get_simple_result(derival_city=derival_city, arrival_city=arrival_city)
    print(data)
    # print(datetime.datetime.now() - start_t)
    # print(timeit.timeit(calculation_.get_simple_result, number=1))
