from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMMain(StatesGroup):
    shipment_choice_1 = State()
    derival_city = State()
    arrival_city = State()
    calc_method_choice = State()
    quick_calc = State()  # пока это состояние не нужно, т.к. расчет происходит сразу после нажатия кнопки, пото м всё заново
    features_calc = State()
    cargo_choice_quantity = State()
    choise_express = State()


class FSMQuantityOne(StatesGroup):
    cargo_choice_size = State()  # ед.изм. габаритов для одного места
    cargo_weight = State()
    cargo_quantity = State()  # кол-во мест
    cargo_insurance = State()  # расчет страховки
    delivery_type = State()  # тип доставки - обычная/экспресс
    cargo_dimensions = State()  # размеры
    quantity_some_one = State()


class FSMQuantitySome(StatesGroup):
    cargo_choice_size = State()  # ед.изм. габаритов для одного места
    cargo_most_weight = State()  # самое тяжелое место
    cargo_total_volume = State()
    cargo_total_weight = State()
    cargo_quantity = State()  # кол-во мест
    cargo_insurance = State()  # расчет страховки
    delivery_type = State()  # тип доставки - обычная/экспресс
    cargo_dimensions = State()  # размеры
    quantity_some_calc = State()



