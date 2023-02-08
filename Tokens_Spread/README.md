### Описание бота
Бот умеет находить спред цены по тикеру токена.
Отсеиваются биржи с низким уровнем доверия, который был им присвоин сервисом CoinMarketCap.
---

## Запуск на удаленном сервере Unix
---
Скачиваем репозиторий и переходим в папку сботом:
```shell
git clone https://github.com/bbmatyushin/TG_Bots.git
cd TG_Bots/Tokens_Spread/
```

**Все команды запускать из рабочей директории с ботом** 
### Подготовить виртуальное окружение
```shell
sudo apt update && sudo apt install -y python3-venv
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
### Данные для работы бота
Переименуйте файл:
```sh
mv data_files/data_file_example.py data_files/data_file.py
```
В файле *data_file.py* необходимо прописать ТОКЕН Бота и указать полный путь до файла *symbol_tokens.json*.
Делаем это следующей командой:
```shell
# укажите ваш токен. Знаки "<" и ">" убрать.
BOT_TOKEN=<your_token_telegram_bot>
```
```shell
sed -i -e "s|^BOT_TOKEN *=.*|BOT_TOKEN = '$BOT_TOKEN'|" data_files/data_file.py
```
### Преместить пакеты с модулями
Все написанные самостоятельно модули нужно переместить в каталог `./venv/lib/python3.8/site-packages/`
Иначе могут быть проблемы при вызове методов/функций (в Pycharm такого не наблюдалось).
Переместите пакеты с модулями в нужный каталог:
```shell
cp -a {crontab_mod/,data_files/,database/,handlers/,parsing/} venv/lib/python3.8/site-packages/ && \
rm -rf {crontab_mod/,data_files/,database/,handlers/,parsing/}
```
### Парсинг данных
Парсинг списка токенов занимает ~5мин. Можно его запустить прежде чем продолжить дальше.
```shell
# если находитесь внутри виртуального окружения
python3 ./venv/lib/python3.8/site-packages/crontab/every_two_hours.py > /dev/null 2>&1 &
```
```shell
# если не внутри виртуального окружения
./venv/bin/python3 ./venv/lib/python3.8/site-packages/crontab_mod/every_two_hours.py > /dev/null 2>&1 &
```
Этот процесс необходимо автоматизировать, например, через **crontab**.
```shell
crontab -e

# парсинг списока токенов будет запускаться каждую ночь в 01:40
# вместо ./ указать полный путь к директории

40 1 * * * ./venv/bin/python3 ./venv/lib/python3.8/site-packages/crontab_mod/once_a_day.py > /dev/null 2>&1
```
### Запуск бота
Находясь в рабочей директории запустить команду:
```shell
# Run from work directory.
# Change name for service file if you want.

printf "[Unit]
Description=Spread crypto currency Bot
After=network-online.target

[Service]
User=$USER
WorkingDirectory=`pwd`
ExecStart=`pwd`/venv/bin/python3 spread_bot_start.py
Restart=always
RestartSec=7

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/spread_tokens_bot.service
```
```shell
systemctl daemon-reload
systemctl enable spread_tokens_bot.service
systemctl restart spread_tokens_bot.service
```
