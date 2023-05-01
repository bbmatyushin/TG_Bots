#### Запуск через Docker

В **Dockerfile** необходимо прописать ваш токен бота и все необходимые ключи для подключения через API транспортных компаний.
Подставьте ваши значения токена и ключей в следующие переменные:
```shell
BOT_TOKEN = '<your_bot_token>'
API_VOZOVOZ = '<your_api_vozovoz>'
API_DELLINE = '<your_api_delline>'
CDEK_CLIENT_ID = '<your_cdek_client_id>'
CDEK_CLIENT_SECRET = '<your_cdek_client_secret>'
JDE_USER_ID = '<your_jde_user_id>'
JDE_API_KEY = '<your_jde_apy_key>'
```

Перед монтирование образа, добавляем значения переменных в Dockerfile:
```shell
sed -i -e "s|<your_bot_token>|$BOT_TOKEN|; \
    s|<your_api_vozovoz>|$API_VOZOVOZ|; \
    s|<your_api_delline>|$API_DELLINE|; \
    s|<your_cdek_client_id>|$CDEK_CLIENT_ID|; \
    s|<your_cdek_client_secret>|$CDEK_CLIENT_SECRET|; \
    s|<your_jde_user_id>|$JDE_USER_ID|; \
    s|<your_jde_apy_key>|$JDE_API_KEY|" ./Dockerfile
```

Собираем образ:
```shell
sudo docker build -t shipping_bot .
```

Поднимаем контейнер:
```shell
sudo docker run --name=shipping_bot --restart=always shipping_bot 
```

#### Запуск как сервисную службу 
Находясь в рабочей директории с ботом, запустите команду
```shell
printf "[Unit]
Description=Shipping Calculation bot
After=network-online.target

[Service]
User=$USER
WorkingDirectory=`pwd`
ExecStart=`pwd`/venv/bin/python3 shipper_calc_bot_start.py
Restart=always
RestartSec=7

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/shipping_calc_bot.service
```
```shell
systemctl daemon-reload
systemctl enable shipping_calc_bot.service
systemctl restart shipping_calc_bot.service
```
