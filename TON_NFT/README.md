## Запуск на удаленном сервере Unix
---
### Поднимаем docker-контейнер с Postgres

```shell
# load image Postgres
docker pull postgres:14
```
```shell
#Create volume for data
docker volume create ton_data
```
```shell
# Run Docker container
docker run -d --name pg_ton -v ton_data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=admin -e POSTGRES_USER=admin -e POSTGRES_DB=ton_db -p 5432:5432 postgres:14
```
---
**Далее все команды запускать из рабочей директории с ботом** 
### Подготовить виртуальное окружение
```shell
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
### Преместить пакеты с модулями
Все написанные самостоятельно модули нужно переместить в папку `./venv/lib/python3.8/site-packages/`
Иначе будет проблема при вызове методов/функций (в Pycharm такого не наблюдалось), при запуске через терминал.
Для перемещения используйте команду:
```sh
mv {handlers/,import_mylib/,keyboards/,parsers/,postgres_db/} ./venv/lib/python3.8/site-packages/
```
В файле *secret_keys.py* (который тоже должен лежать в папке `./venv/lib/python3.8/site-packages/import_mylib/`) прописать ТОКЕН Бота и указать порт для подключения к Postgres, который был указан при поднятии контейнера.
Делаем это следующей командой:
```shell
mv ./venv/lib/python3.8/site-packages/import_mylib/secret_keys_example.py ./venv/lib/python3.8/site-packages/import_mylib/secret_keys.py
BOT_TOKEN=<your_token_telegram_bot>
PG_PORT=<port_docker_postgres>
sed -i -e "s/^TOKEN *=.*/TOKEN = \"$BOT_TOKEN\"/; s/^PORT *=.*/PORT = \"$PG_PORT\"/" ./venv/lib/python3.8/site-packages/import_mylib/secret_keys.py
```
### Парсинг данных
Парсинг занимает ~15 минут (в зависимости от количества данных). Можно его запустить прежде чем продолжить дальше.
Запуск процесса создания таблиц, сбор данных и наполнения таблиц в фоне:
```shell
# если находитесь внутри виртуального окружения
python3 ./venv/lib/python3.8/site-packages/postgres_db/diamonds_insert_tbl.py > /dev/null 2>&1 &

# если не внутри виртуального окружения
./venv/bin/python3 ./venv/lib/python3.8/site-packages/postgres_db/diamonds_insert_tbl.py > /dev/null 2>&1 &
```
Запуск парсинг и наполнения таблиц можно автоматизировать через **crontab**.
```shell
crontab -e

# запускать парсер каждые 2 часа
# вместо ./ указать полный путь к директории
0 */2 * * * ./venv/bin/python3 ./venv/lib/python3.8/site-packages/postgres_db/diamonds_insert_tbl.py > /dev/null 2>&1
```
