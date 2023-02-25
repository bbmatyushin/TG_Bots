#### Запус через Dokcer
В Dockerfile необходимо прописать ваш токен бота.
Сохраняем в переменную ваш токен:
```shell
BOT_TOKEN=<your_bot_token>
```
Подставляем его в Dockerfile перед монтированием образа:
```shell
sed -i -e "s|<you_token_bot>|$BOT_TOKEN|" Dockerfile
```
Собираем образ:
```shell
sudo docker build -t realty_info_bot .
```
Поднимаем контейнер:
```shell
sudo docker run -d --name=realty_info_bot --restart=always realty_info_bot
```

#### Запуск как сервисную службу 
Находясь в рабочей директории с ботом, запустите команду
```shell
printf "[Unit]
Description=Realty RF bot
After=network-online.target

[Service]
User=$USER
WorkingDirectory=`pwd`
ExecStart=`pwd`/venv/bin/python3 bot_start.py
Restart=always
RestartSec=7

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/realty_search_info_bot.service
```
```shell
systemctl daemon-reload
systemctl enable realty_search_info_bot.service
systemctl restart realty_search_info_bot.service
```