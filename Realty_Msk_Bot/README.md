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