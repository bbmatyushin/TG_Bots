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
                              delivery_type='auto',
                              derival_city_kladr="", arrival_city_kladr="",
                              delivery_arrival_variant='terminal',
                              delivery_derival_variant='terminal',
                              arrival_street_kladr='', derival_street_kladr=''):

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
                                            delivery_type=delivery_type,
                                            derival_city_kladr=derival_city_kladr,
                                            arrival_city_kladr=arrival_city_kladr,
                                            delivery_arrival_variant=delivery_arrival_variant,
                                            delivery_derival_variant=delivery_derival_variant,
                                            arrival_street_kladr=arrival_street_kladr,
                                            derival_street_kladr=derival_street_kladr)

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
                              derival_city='Москва', arrival_city="Санкт-Петербург",
                              delivery_arrival_variant='terminal',
                              delivery_derival_variant='terminal'):

        params = self.params.vozovoz_params(quantity=quantity, weight=weight,
                                            length=length, width=width, height=height,
                                            total_weight=total_weight, total_volume=total_volume,
                                            insurance=insurance,
                                            derival_city=derival_city, arrival_city=arrival_city,
                                            delivery_arrival_variant=delivery_arrival_variant,
                                            delivery_derival_variant=delivery_derival_variant)

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
                           derival_city='Москва', arrival_city="Санкт-Петербург",
                           delivery_arrival_variant='terminal',
                           delivery_derival_variant='terminal'
                           ):
        """Тариф для расчета = Посылка склад-склад, режим доставки = склад -склад - это код 136
        код 483 - Экспресс склад-склад (https://api-docs.cdek.ru/63345519.html) """

        params = self.params.cdek_params(weight=weight, length=length, width=width, height=height,
                                         insurance=insurance, delivery_type=delivery_type,
                                         derival_city=derival_city, arrival_city=arrival_city,
                                         delivery_arrival_variant=delivery_arrival_variant,
                                         delivery_derival_variant=delivery_derival_variant)

        try:
            data = self.cdek_parser.cdek_get_data(params)

            if float(weight) <= 30.0:
                price, date_from, date_to = data["total_sum"], data["period_min"], data["period_max"]
                if date_from == date_to:
                    return price, date_to
                else:  # если даты разные то вернем сроки в виде 1-4
                    return price, "-".join(map(str, [date_from, date_to]))
            else:
                return "_Доставка доступна только для грузов весом менее 30 кг._"
        except KeyError:
            return "_По данному направлению при заданных условиях выбранный тариф недоступен._"
        
    def jde_calc(self, quantity='1', weight='8', length='0.3', width='0.2', height='0.25',
                 total_weight='10', total_volume='0', insurance='100000',
                 derival_city='Москва', arrival_city="Санкт-Петербург",
                 delivery_type='auto',  # такое значение как в Деловых для однообразия
                 services='',
                 delivery_arrival_variant='terminal',
                 delivery_derival_variant='terminal',
                 arrival_city_kladr='', derival_city_kladr=''
                 ):

        type = '2' if delivery_type == "express" else '1'

        params = self.params.jde_params(quantity=quantity, weight=weight, length=length,
                                        width=width, height=height, total_weight=total_weight,
                                        total_volume=total_volume, insurance=insurance,
                                        derival_city=derival_city, arrival_city=arrival_city,
                                        type=type, services=services,
                                        delivery_arrival_variant=delivery_arrival_variant,
                                        delivery_derival_variant=delivery_derival_variant,
                                        arrival_city_kladr=arrival_city_kladr,
                                        derival_city_kladr=derival_city_kladr
                                        )

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

    def check_city(self, derival_city='Москва', arrival_city="Санкт-Петербург",
                   derival_city_full_name='', arrival_city_full_name=''):
        """Для проверки правильности написания города. Вертнет КЛАДР города и улицы,
        полное навание города с регионом.
        city_full_name - поступает из хэндлера"""

        check_city_dict = {}
        derival_city = derival_city.title()
        arrival_city = arrival_city.title()

        ##===== Проверяется в main_хэндлере ===========!!!!
        ## Здесь для теста
        for city in [derival_city, arrival_city]:
            if ut.check_cites_on_pop_list(city):  # проверяем есть ли город в популярных...
                pass
            else:  # если нет то добавляем туда
                ut.save_popular_cites(city)

        check_derival_city = ut.check_cites_on_pop_list(derival_city)
        check_arrival_city = ut.check_cites_on_pop_list(arrival_city)

        if check_derival_city:
            if len(check_derival_city) == 1:
                derival_city = list(check_derival_city.values())[0]["name"]
                derival_city_kladr = list(check_derival_city.values())[0]["kladr"]
                derival_city_id = list(check_derival_city.values())[0]["city_id"]  # для Деловых
            else:
                derival_city = check_derival_city[derival_city_full_name]["name"]
                derival_city_kladr = check_derival_city[derival_city_full_name]["kladr"]
                derival_city_id = check_derival_city[derival_city_full_name]["city_id"]  # для Деловых
        else:
            return f"Город {derival_city} не найден. Возможно опечатка в названии.\n" \
                   f"Попробуйте ввести только первые буквы названия города."
        if check_arrival_city:
            if len(check_arrival_city) == 1:
                arrival_city = list(check_arrival_city.values())[0]["name"]
                arrival_city_kladr = list(check_arrival_city.values())[0]["kladr"]
                arrival_city_id = list(check_arrival_city.values())[0]["city_id"]  # для Деловых
            else:
                arrival_city = check_arrival_city[arrival_city_full_name]["name"]
                arrival_city_kladr = check_arrival_city[arrival_city_full_name]["kladr"]
                arrival_city_id = check_arrival_city[arrival_city_full_name]["city_id"]  # для Деловых
        else:
            return f"Город {arrival_city} не найден. Возможно опечатка в названии.\n" \
                   f"Попробуйте ввести только первые буквы названия города."

        check_city_dict["derival_city"] = derival_city
        check_city_dict["derival_city_kladr"] = derival_city_kladr
        check_city_dict["derival_city_id"] = derival_city_id
        check_city_dict["arrival_city"] = arrival_city
        check_city_dict["arrival_city_kladr"] = arrival_city_kladr
        check_city_dict["arrival_city_id"] = arrival_city_id

        derival_street_kladr = ut.get_kladr_street(check_city_dict["derival_city_id"])
        arrival_street_kladr = ut.get_kladr_street(check_city_dict["arrival_city_id"])

        check_city_dict["derival_street_kladr"] = derival_street_kladr
        check_city_dict["arrival_street_kladr"] = arrival_street_kladr

        return check_city_dict

    def dellin_get_result(self, **kwargs):
        delline_calc = self.delline_terminal_calc(total_volume=kwargs.get("total_volume"),
                                                  quantity=kwargs.get("quantity"), weight=kwargs.get("weight"),
                                                  total_weight=kwargs.get("total_weight"),
                                                  length=kwargs.get("length"), width=kwargs.get("width"),
                                                  height=kwargs.get("height"), insurance=kwargs.get("insurance"),
                                                  derival_city_kladr=kwargs.get("derival_city_kladr"),
                                                  arrival_city_kladr=kwargs.get("arrival_city_kladr"),
                                                  derival_city=kwargs.get("derival_city"),
                                                  arrival_city=kwargs.get("arrival_city"),
                                                  delivery_type=kwargs.get("delivery_type"),
                                                  delivery_arrival_variant=kwargs.get("delivery_arrival_variant"),
                                                  delivery_derival_variant=kwargs.get("delivery_derival_variant"),
                                                  arrival_street_kladr=kwargs.get("arrival_street_kladr"),
                                                  derival_street_kladr=kwargs.get("derival_street_kladr"))
        if len(delline_calc) == 2:
            return f'{delline_calc[0]:,} ₽, срок *{delline_calc[1]} дн.*'
        else:
            return delline_calc

    def get_simple_result(self, total_volume='0', total_weight='0', quantity='1', weight='8',
                          length='0.3', width='0.2', height='0.25', insurance='50000',
                          derival_city='Москва', arrival_city="Санкт-Петербург",
                          delivery_type='auto',
                          services='',  # эти аргументы для Желдорэкспедиции
                          derival_city_full_name='', arrival_city_full_name='',
                          delivery_arrival_variant='terminal',
                          delivery_derival_variant='terminal'):

        #  derival_city_full_name, arrival_city_full_name - будут приходить с инлайн кнопок
        check_cites_dict = self.check_city(derival_city=derival_city, arrival_city=arrival_city,
                                           derival_city_full_name=derival_city_full_name,
                                           arrival_city_full_name=arrival_city_full_name)

        derival_city = check_cites_dict["derival_city"]
        arrival_city = check_cites_dict["arrival_city"]
        derival_city_kladr = check_cites_dict["derival_city_kladr"]
        arrival_city_kladr = check_cites_dict["arrival_city_kladr"]
        arrival_street_kladr = check_cites_dict["arrival_street_kladr"]
        derival_street_kladr = check_cites_dict["derival_street_kladr"]

        if float(total_volume) == 0.0:
            n = round((float(length) * float(width) * float(height)), 2)
            get_total_volume = '0.01' if n < 0.01 else str(n)
        else:
            get_total_volume = total_volume

        # Проверяем входят ли города в список городов с терминалами ДЛ
        if delivery_arrival_variant == 'terminal' and delivery_derival_variant == 'terminal':
            if all([list(self.delline_cities_terminal.keys()).count(derival_city),
                    list(self.delline_cities_terminal.keys()).count(arrival_city)]):
                delline_result = self.dellin_get_result(total_volume=total_volume, quantity=quantity, weight=weight,
                                                      total_weight=total_weight, length=length, width=width,
                                                      height=height, insurance=insurance,
                                                      derival_city_kladr=derival_city_kladr,
                                                      arrival_city_kladr=arrival_city_kladr,
                                                      derival_city=derival_city, arrival_city=arrival_city,
                                                      delivery_type=delivery_type,
                                                      delivery_arrival_variant=delivery_arrival_variant,
                                                      delivery_derival_variant=delivery_derival_variant,
                                                      arrival_street_kladr=arrival_street_kladr,
                                                      derival_street_kladr=derival_street_kladr)
            else:
                delline_result = "_Межтерминальная перевозка не осуществляется._"
        else:
            delline_result = self.dellin_get_result(total_volume=get_total_volume, quantity=quantity, weight=weight,
                                                    total_weight=total_weight, length=length, width=width,
                                                    height=height, insurance=insurance,
                                                    derival_city_kladr=derival_city_kladr,
                                                    arrival_city_kladr=arrival_city_kladr,
                                                    derival_city=derival_city, arrival_city=arrival_city,
                                                    delivery_type=delivery_type,
                                                    delivery_arrival_variant=delivery_arrival_variant,
                                                    delivery_derival_variant=delivery_derival_variant,
                                                    arrival_street_kladr=arrival_street_kladr,
                                                    derival_street_kladr=derival_street_kladr)

        vozovoz_calc = self.vozovoz_terminal_calc(quantity=quantity, weight=weight,
                                                  length=length, width=width, height=height,
                                                  total_weight=weight, insurance=insurance,
                                                  derival_city=derival_city, arrival_city=arrival_city,
                                                  delivery_arrival_variant=delivery_arrival_variant,
                                                  delivery_derival_variant=delivery_derival_variant,
                                                  )
        if len(vozovoz_calc) == 2:
            vozovoz_result = f"{vozovoz_calc[0]:,} ₽, срок *{vozovoz_calc[1]} дн.*"
        else:
            vozovoz_result = vozovoz_calc

        if quantity == '1':
            cdek_calc = self.cdek_terminal_calc(weight=weight, length=length, width=width, height=height,
                                                insurance=insurance, delivery_type=delivery_type,
                                                derival_city=derival_city, arrival_city=arrival_city,
                                                delivery_arrival_variant=delivery_arrival_variant,
                                                delivery_derival_variant=delivery_derival_variant
                                                )
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
                                 services=services,
                                 delivery_arrival_variant=delivery_arrival_variant,
                                 delivery_derival_variant=delivery_derival_variant,
                                 arrival_city_kladr=arrival_city_kladr,
                                 derival_city_kladr=derival_city_kladr)
        if len(jde_calc) == 2:
            jde_result = f"{float(jde_calc[0]):,} ₽, срок *{jde_calc[1]} дн.*"
        else:
            jde_result = jde_calc

        if delivery_arrival_variant == 'terminal' and delivery_derival_variant == 'terminal':
            output_top = [f"Расчет межтерминальной перевозки *{derival_city}* - *{arrival_city}*\n"
                          f"------------------------------\n"]
        elif delivery_arrival_variant == 'address' and delivery_derival_variant == 'terminal':
            output_top = [f"Расчет перевозки до адреса *{derival_city}* - *{arrival_city}*\n"
                          f"------------------------------\n"]
        else:
            output_top = [f"Расчет перевозки *{derival_city}* - *{arrival_city}*\n"
                          f"------------------------------\n"]
        if quantity == '1':
            output_head = [f"📦 _Параметры груза:_\n"
                           f"*Габариты:* {length}×{width}×{height} м (Д×Ш×В)\n"
                           f"*Вес:* {weight} кг, *Объём:* {float(get_total_volume):.2f} м3\n"
                           f"*Объявленная стоимость:* {float(insurance):,.0f} ₽\n"
                           f"------------------------------\n"]
        else:
            output_head = [f"📦 _Параметры груза:_\n"
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
        output = [*output_top, *output_head, *self.output_footer]

        return "".join(output)
        # return output_head, self.output_footer


if __name__ == "__main__":
    #TODO: Добавить экспресс доставку для СДЭК (смениться тариф)
    data_calc = ShippersTerminalCalculation()
    calculation_ = TotalTerminalResult()
    derival_city = 'Москва'
    arrival_city = 'Беломорск'
    derival_city_full_name = 'г. Москва'
    arrival_city_full_name = 'Беломорск г (Респ. Карелия)'
    derival_city_kladr = '7800000000000000000000000'
    arrival_city_kladr = '7700000000000000000000000'
    delivery_arrival_variant = 'address'
    # data = data_calc.delline_terminal_calc(derival_city=derival_city, arrival_city=arrival_city,
    #                                          delivery_arrival_variant=delivery_arrival_variant)
    data = calculation_.get_simple_result(delivery_type="auto", delivery_arrival_variant=delivery_arrival_variant,
                                          derival_city_full_name=derival_city_full_name,
                                          arrival_city_full_name=arrival_city_full_name,
                                          derival_city=derival_city, arrival_city=arrival_city)
    print(data)
    # print(datetime.datetime.now() - start_t)
    # print(timeit.timeit(calculation_.get_simple_result, number=1))
