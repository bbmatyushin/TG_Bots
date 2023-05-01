import logging


class LoggerForBot:
    def init_logger(self):
        format = '%(asctime)s [%(levelname)s] %(message)s'
        logging.basicConfig(format=format)
        logger = logging.getLogger('bot')
        if logger.hasHandlers():  # убирает дублирование логов
            logger.handlers.clear()
        logger.setLevel(logging.DEBUG)
        # sh = logging.StreamHandler()
        # sh.setFormatter(logging.Formatter(format))
        fh = logging.FileHandler(filename='bot_logs.log')
        fh.setFormatter(logging.Formatter(format))
        # logger.addHandler(sh)
        logger.addHandler(fh)

        return logger

    def message_logger_info(self, message):
        logger = self.init_logger()
        message_text = message.text.replace("\n", " ")
        logger.info(f'message from user_name={message.from_user.username} id={message.from_user.id} '
                    f'text={message_text}')

    def message_logger_warn(self, message):
        logger = self.init_logger()
        message_text = message.text.replace("\n", " ")
        logger.warning(f'message from user_name={message.from_user.username} id={message.from_user.id} '
                    f'text={message_text}')

    def callback_logger_info(self, callback):
        logger = self.init_logger()
        callback_message_text = callback.message.text.replace("\n", " ")
        logger.info(f'callback from user_name={callback.from_user.username} '
                    f'id={callback.from_user.id} '
                    f'callback_message_text={callback_message_text} '
                    f'callback_data={callback.data}')

    def callback_logger_warn(self, callback):
        logger = self.init_logger()
        callback_message_text = callback.message.text.replace("\n", " ")
        logger.warning(f'callback from user_name={callback.from_user.username} '
                       f'id={callback.from_user.id} '
                       f'callback_message_text={callback_message_text} '
                       f'callback_data={callback.data}')


if __name__ == "__main__":
    format = '%(asctime)s [%(levelname)s] %(message)s'
    sh = logging.StreamHandler()
    fh = logging.FileHandler(filename='bot.log')
    logging.basicConfig(handlers=(sh, fh), format=format,
                        datefmt='%m.%d.%Y %H:%M:%S', level=logging.INFO)

    logging.info("&&&")