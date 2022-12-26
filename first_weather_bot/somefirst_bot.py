import telebot
import json

from first_bot_modules import get_weather


if __name__ == '__main__':
    """
    You need to create a file 'data_secret.json' in the root directory
    and put your data into it, as in the example - 'data_secret_example.json'
    """
    with open('data_secret.json', 'r') as f:
        data_secret = json.load(f)

    appid1 = data_secret['appid1']
    appid2 = data_secret['appid2']
    bot_token = data_secret['bot_token']

    bot_odject = get_weather.TGWeatherBot(appid1, appid2)
    bot = telebot.TeleBot(bot_token)


    # Command /start
    @bot.message_handler(commands=['start'])
    def start(m, res=False):
        bot.send_message(m.chat.id, "Hi there! Enter a city of the Russia.\nМожно на русском ツ")


    # Get message from user
    @bot.message_handler(content_types=['text'])
    def handle_text(message):
        bot.send_message(message.chat.id, bot_odject.get_result(message.text))


    bot.polling(none_stop=True, interval=0)
