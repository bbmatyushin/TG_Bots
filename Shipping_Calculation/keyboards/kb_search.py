from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


def get_kb(search_list: list) -> ReplyKeyboardMarkup:
    """Сюда подставлять список из кнопок подсказок"""
    kb_list = []
    for i in range(0, len(search_list), 3):
        el = search_list[i:i + 3]
        add_list = []
        for n in el:
            add_list.append(KeyboardButton(f"{n}"))

        kb_list.append(add_list)
    kb = ReplyKeyboardMarkup(kb_list,
        resize_keyboard=True, row_width=3, one_time_keyboard=True)

    return kb


if __name__ == "__main__":
    get_kb([1, 2 , 3, 2])