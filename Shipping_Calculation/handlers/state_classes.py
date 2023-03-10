from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMMain(StatesGroup):
    shipment_choice_1 = State()
    derival_city = State()
    check_derival_city = State()
    derival_city_full_name = State()
    arrival_city = State()
    check_arrival_city = State()
    arrival_city_full_name = State()
    calc_method_choice = State()
    quick_calc = State()  # пока это состояние не нужно, т.к. расчет происходит сразу после нажатия кнопки, пото м всё заново
    features_calc = State()
    cargo_choice_quantity = State()
    choise_express = State()
    delivery_derival_variant = State()  # terminal/address
    delivery_arrival_variant = State()  # terminal/address
    terminal_to_address = State()
    handling = State()  # ПРР


class FSMQuantityOne(StatesGroup):
    cargo_choice_size = State()  # ед.изм. габаритов для одного места
    cargo_weight = State()
    cargo_quantity = State()  # кол-во мест
    cargo_insurance = State()  # расчет страховки
    delivery_type = State()  # тип доставки - обычная/экспресс
    cargo_dimensions = State()  # размеры
    quantity_some_one = State()
    temperature = State()


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
    temperature = State()
