from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


kb_start = ReplyKeyboardMarkup([
    [KeyboardButton("🔎 начать поиск")]
], one_time_keyboard=True, resize_keyboard=True)

def get_address_kb(addr_list: list) -> ReplyKeyboardMarkup:
    """Сюда подставлять список из возможных вариантов адресов"""
    kb_list = []
    for i in range(0, len(addr_list)):
        el = addr_list[i:i + 1]
        add_list = [KeyboardButton(f"{n}") for n in el]
        kb_list.append(add_list)
    kb = ReplyKeyboardMarkup(kb_list[:50], resize_keyboard=True, one_time_keyboard=True)

    return kb


if __name__ == "__main__":
    l = ["Дом", "Строение", "Улица"]
    kb = get_address_kb(l)


