from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMMain(StatesGroup):
    type_address_name = State()
