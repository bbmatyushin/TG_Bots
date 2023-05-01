import asyncio
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

    async def delline_calc(self, **kwargs):

        if kwargs.get("delivery_type") == 'express':
            delivery_kladr = self.delline_cities_terminal[kwargs.get("derival_city")]['city_kladr']
            arrival_kladr = self.delline_cities_terminal[kwargs.get("arrival_city")]['city_kladr']
            delivery_express = DellineTerminals().delline_search_express_terminal(delivery_kladr)["express"]
            arrival_express = DellineTerminals().delline_search_express_terminal(arrival_kladr)["express"]
            if not delivery_express:  # если вернется пустой список, т.е. нет терминала под экспресс доставку
                return f"Эксперсс доставка из г.{kwargs.get('derival_city')} невозможна."
            if not arrival_express:
                return f"Эксперсс доставка в г.{kwargs.get('arrival_city')} невозможна."

        params = await self.params.delline_params(**kwargs)
        data = await self.delline_parser.delline_get_data(params=params)

        if isinstance(data, dict):
            price = data.get("price")
            shipment_day = data.get("orderDates").get("derivalFromOspSender")
            receipt_day = data.get("orderDates").get("arrivalToOspReceiver")
            shipping_days = (datetime.datetime.strptime(receipt_day, '%Y-%m-%d').date() -
                             datetime.datetime.strptime(shipment_day, '%Y-%m-%d').date()).days

            return price, shipping_days
        else:
            return data

    async def vozovoz_calc(self, **kwargs):
        params = await self.params.vozovoz_params(**kwargs)
        data = await self.vozovoz_parser.vozovoz_get_data(params)

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

    async def cdek_calc(self, **kwargs):
        """Тариф для расчета = Посылка склад-склад, режим доставки = склад -склад - это код 136
        код 483 - Экспресс склад-склад (https://api-docs.cdek.ru/63345519.html) """
        params = await self.params.cdek_params(**kwargs)

        try:
            data = await self.cdek_parser.cdek_get_data(params)

            if float(kwargs.get("weight")) <= 30.0:
                price, date_from, date_to = data["total_sum"], data["period_min"], data["period_max"]
                if date_from == date_to:
                    return price, date_to
                else:  # если даты разные то вернем сроки в виде 1-4
                    return price, "-".join(map(str, [date_from, date_to]))
            else:
                return "_Доставка доступна только для грузов весом менее 30 кг._"
        except KeyError:
            return "_По данному направлению при заданных условиях выбранный тариф недоступен._"
        
    async def jde_calc(self, **kwargs):

        type = '2' if kwargs.get("delivery_type") == "express" else '1'
        params = await self.params.jde_params(**kwargs, type=type)

        try:
            data = await self.jde_parser.jde_get_data(params)
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
            return "_Перевозка не осуществляется._"


class TotalTerminalResult(ShippersTerminalCalculation):
    def __init__(self):
        super().__init__()
        self.shipper_list = ut.shipper_list
        self.output_footer = []


    async def check_city(self, derival_city='Москва', arrival_city="Санкт-Петербург",
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

    async def dellin_get_result(self, **kwargs):
        delline_calc = await self.delline_calc(**kwargs)
        if len(delline_calc) == 2:
            return f'{delline_calc[0]:,} ₽, срок *{delline_calc[1]} дн.*'
        else:
            return delline_calc

    async def get_simple_result(self, **kwargs):
        check_cites_dict = await self.check_city(derival_city=kwargs.get("derival_city"),
                                           arrival_city=kwargs.get("arrival_city"),
                                           derival_city_full_name=kwargs.get("derival_city_full_name"),
                                           arrival_city_full_name=kwargs.get("arrival_city_full_name"))

        derival_city = check_cites_dict["derival_city"]
        arrival_city = check_cites_dict["arrival_city"]
        derival_city_kladr = check_cites_dict["derival_city_kladr"]
        arrival_city_kladr = check_cites_dict["arrival_city_kladr"]
        arrival_street_kladr = check_cites_dict["arrival_street_kladr"]
        derival_street_kladr = check_cites_dict["derival_street_kladr"]

        if float(kwargs.get("total_volume")) == 0.0:
            n = round((float(kwargs.get("length")) * float(kwargs.get("width")) * float(kwargs.get("height"))), 2)
            get_total_volume = '0.01' if n < 0.01 else str(n)
        else:
            get_total_volume = kwargs.get("total_volume")

        if kwargs.get("temperature") == 'no':  #
            """Если не требуется перевозка в тепле, то расчет идет
            по всем ТК. Иначе только для ЖДЭ."""
            # Проверяем входят ли города в список городов с терминалами ДЛ
            if kwargs.get("delivery_arrival_variant") == 'terminal' \
                    and kwargs.get("delivery_derival_variant") == 'terminal':
                if all([list(self.delline_cities_terminal.keys()).count(derival_city),
                        list(self.delline_cities_terminal.keys()).count(arrival_city)]):
                    # result_args = kwargs
                    delline_result = await self.dellin_get_result(**kwargs, derival_city_kladr=derival_city_kladr,
                                                            arrival_city_kladr=arrival_city_kladr,
                                                            arrival_street_kladr=arrival_street_kladr,
                                                            derival_street_kladr=derival_street_kladr)
                else:
                    delline_result = "_Межтерминальная перевозка не осуществляется._"
            else:
                delline_result = await self.dellin_get_result(**kwargs, derival_city_kladr=derival_city_kladr,
                                                        arrival_city_kladr=arrival_city_kladr,
                                                        arrival_street_kladr=arrival_street_kladr,
                                                        derival_street_kladr=derival_street_kladr)

            vozovoz_calc = await self.vozovoz_calc(**kwargs)
            if len(vozovoz_calc) == 2:
                vozovoz_result = f"{vozovoz_calc[0]:,} ₽, срок *{vozovoz_calc[1]} дн.*"
            else:
                vozovoz_result = vozovoz_calc

            if kwargs.get("quantity") == '1':
                cdek_calc = await self.cdek_calc(**kwargs)
                if len(cdek_calc) == 2:
                    cdek_result = f"{cdek_calc[0]:,} ₽, срок *{cdek_calc[1]} дн.*"
                else:
                    cdek_result = cdek_calc
            else:
                cdek_result = f"Для количества мест больше 1 расчет не реализован."
        else:
            vozovoz_result, delline_result, cdek_result = '', '', ''

        jde_calc = await self.jde_calc(**kwargs, arrival_city_kladr=arrival_city_kladr,
                                 derival_city_kladr=derival_city_kladr)
        if len(jde_calc) == 2:
            jde_result = f"{float(jde_calc[0]):,} ₽, срок *{jde_calc[1]} дн.*"
        else:
            jde_result = jde_calc

        get_handling = '(с учетом ПРР)' if kwargs.get("handling") == 'yes' else '(без учета ПРР)'

        if kwargs.get("delivery_arrival_variant") == 'terminal' \
                and kwargs.get("delivery_derival_variant") == 'terminal':
            output_top = [f"Расчет межтерминальной перевозки *{derival_city}* - *{arrival_city}*\n"
                          f"------------------------------\n"]
        elif kwargs.get("delivery_arrival_variant") == 'address' and \
                kwargs.get("delivery_derival_variant") == 'terminal':
            output_top = [f"Расчет перевозки до адреса *{derival_city}* - *{arrival_city}* "
                          f"_{get_handling}_\n"
                          f"------------------------------\n"]
        else:
            output_top = [f"Расчет перевозки *{kwargs.get('derival_city')}* - "
                          f"*{kwargs.get('arrival_city')}*\n"
                          f"------------------------------\n"]
        if kwargs.get('quantity') == '1':
            output_head = [f"📦 _Параметры груза:_\n"
                           f"*Габариты:* {kwargs.get('length')}×{kwargs.get('width')}×"
                           f"{kwargs.get('height')} м (Д×Ш×В)\n"
                           f"*Вес:* {kwargs.get('weight')} кг, *Объём:* {float(get_total_volume):.2f} м3\n"
                           f"*Объявленная стоимость:* {float(kwargs.get('insurance')):,.0f} ₽\n"
                           f"------------------------------\n"]
        else:
            output_head = [f"📦 _Параметры груза:_\n"
                           f"*Всего мест:* {kwargs.get('quantity')}, "
                           f"*Общий вес:* {kwargs.get('total_weight')} кг,\n"
                           f"*Общий объём:* {float(get_total_volume):.2f} м3, \n"
                           f"*Самое большое место:* {kwargs.get('length')}×"
                           f"{kwargs.get('width')}×{kwargs.get('height')} м\n"
                           f"*Объявленная стоимость:* {float(kwargs.get('insurance')):,.0f} ₽\n"
                           f"------------------------------\n"]
        if kwargs.get("temperature") == 'no':
            """Если не требуется перевозка в тепле, то выводится результат 
            по всем ТК. Иначе только для ЖДЭ."""
            if kwargs.get('delivery_type') == 'express':
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
        else:
            if kwargs.get('delivery_type') == 'express':
                self.output_footer = [f"⚡️ *{self.shipper_list[2]}* - {jde_result}\n"  # есть экспресс доставка
                                      f"------------------------------"]
            else:
                self.output_footer = [f"◗ *{self.shipper_list[2]}* - {jde_result}\n"
                                      f"------------------------------"]
        output = [*output_top, *output_head, *self.output_footer]

        return "".join(output)
        # return output_head, self.output_footer


async def main():
    calc_args = {
        "total_volume": '0',
        "quantity": '1',
        "weight": '8',
        "total_weight": '0',
        "length": '0.3',
        "width": '0.2',
        "height": '0.25',
        "insurance": '50000',
        "derival_city": 'Москва',
        "arrival_city": "Петрозаводск",
        "delivery_type": 'auto',
        "handling": 'yes',
        "temperature": "no",
        "delivery_arrival_variant": 'terminal',
        "delivery_derival_variant": 'terminal',
        "derival_city_full_name": 'г. Москва',
        "arrival_city_full_name": 'Петрозаводск г (Респ. Карелия)'
    }
    task1 = asyncio.create_task(TotalTerminalResult().get_simple_result(**calc_args))
    await task1
    print(task1.result())


if __name__ == "__main__":
    t0 = datetime.datetime.now()

    asyncio.run(main())

    print(datetime.datetime.now() - t0)