## Запуск на удаленном сервере Unix
---
### Поднимаем docker-контейнер с Postgres

```shell
# load image Postgres
docker pull postgres:14
```
```shell
#Create volume for data
docker volume create ton_nfts_data
```
```shell
# Run Docker container
docker run -d --name pg_ton_nfts -v ton_nfts_data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=admin -e POSTGRES_USER=admin -e POSTGRES_DB=ton_nfts_db -p 5632:5432 postgres:14
```
---
**Далее все команды запускать из рабочей директории с ботом** 
### Подготовить виртуальное окружение
```shell
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
### Данные для работы бота
Переименуйте файл:
```sh
mv import_modules/work_data_file_example.py import_modules/work_data_file.py
```
В файле *work_data_file.py* необходимо прописать ТОКЕН Бота, указать порт для подключения к Postgres, который был указан при поднятии контейнера (cловарь collections не изменять) и указать полный путь до директории *data*.
Делаем это следующей командой:
```shell
# укажите ваш токен и порт. Знаки "<" и ">" убрать.
BOT_TOKEN=<your_token_telegram_bot>

PG_PORT=5632
DATA_PARH=`pwd`/data/

sed -i -e "s/^TOKEN *=.*/TOKEN=\"$BOT_TOKEN\"/; s/^PORT *=.*/PORT=\"$PG_PORT\"/; s/^dir_data_path *=.*/dir_data_path=\"$DATA_PARH\"/" import_modules/work_data_file.py
```
### Преместить пакеты с модулями
Все написанные самостоятельно модули нужно переместить в каталог `./venv/lib/python3.8/site-packages/`
Иначе могут быть проблемы при вызове методов/функций (в Pycharm такого не наблюдалось).
Переместите пакеты с модулями в нужный каталог:
```shell
mv {crontab_mod/,handlers/,import_modules/,keyboards/,parsing/,pg_database} venv/lib/python3.8/site-packages/
```
### Парсинг данных
Парсинг занимает ~1ч.30 минут (в зависимости от количества данных). Можно его запустить прежде чем продолжить дальше.
Для начала создаем необходимые таблицы в базе данных:
```shell
# если находитесь внутри виртуального окружения
python3 ./venv/lib/python3.8/site-packages/crontab_mod/once_a_day.py > /dev/null 2>&1 &

# если не внутри виртуального окружения
./venv/bin/python3 ./venv/lib/python3.8/site-packages/crontab_mod/once_a_day.py > /dev/null 2>&1 &
```
Теперь запускаем процесс сбора данных и наполнения таблицы:
```shell
# если находитесь внутри виртуального окружения
python3 ./venv/lib/python3.8/site-packages/crontab_mod/every_two_hours.py > /dev/null 2>&1 &

# если не внутри виртуального окружения
./venv/bin/python3 ./venv/lib/python3.8/site-packages/crontab_mod/every_two_hours.py > /dev/null 2>&1 &
```
Эти процеццы необходимо автоматизировать, например, через **crontab**.
```shell
crontab -e

# таблицы будут обновляться каждый день в 01:40
# запускать парсер каждые 2 часа начиная с 02:00 до 23:00
# вместо ./ указать полный путь к директории
40 1 * * * ./venv/bin/python3 ./venv/lib/python3.8/site-packages/crontab_mod/once_a_day.py > /dev/null 2>&1
0 2-23/2 * * * ./venv/bin/python3 ./venv/lib/python3.8/site-packages/crontab_mod/every_two_hours.py > /dev/null 2>&1
```
### Запуск бота
Находясь в рабочей директории запустить команду:
```shell
# Run from work directory.
# Change file name for running bot in 'ExecStart'
# and change name for service file.

printf "[Unit]
Description=Research TON NFT bot
After=network-online.target

[Service]
User=$USER
WorkingDirectory=`pwd`
ExecStart=`pwd`/venv/bin/python3 research_ton_nft_bot.py
Restart=always
RestartSec=7

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/researchertonnft_bot.service
```
```shell
systemctl daemon-reload
systemctl enable researchertonnft_bot.service
systemctl restart researchertonnft_bot.service
```
