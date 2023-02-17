from aiogram import types, Dispatcher
from handlers.state_classes import FSMMain

from data_files.create_bot import bot, dp
from keyboards import client_kb as kb
from data_files.useful_tools import shipper_list_full_name

from logger.get_logs import LoggerForBot


async def command_start_help_restart(message: types.Message, state=None):
    LoggerForBot().message_logger_info(message)
    await message.delete()
    await state.reset_data()
    await bot.send_message(message.from_user.id,
                           f"Бот на связи! 👋\n\n"
                           f"Я могу помочь быстро рассчитать стоимость доставки груза "
                           f"и сравнить её между разными транспортными компаниями.\n\n"
                           f"Сейчас для сравнения доступны следующие ТК: *{', '.join(shipper_list_full_name)}*.",
                           parse_mode="Markdown",
                           reply_markup=kb.kb)
    await FSMMain.shipment_choice_1.set()
    await bot.send_message(chat_id=message.from_user.id,
                           text="📍 Выберите способ доставки:",
                           reply_markup=kb.ikb_shipment_choice_1)


def register_handler(dp: Dispatcher):
    dp.register_message_handler(command_start_help_restart,
                                lambda message: message.text in ['/start', '/help', 'Перезапустить'],
                                content_types=['text'], state="*")
