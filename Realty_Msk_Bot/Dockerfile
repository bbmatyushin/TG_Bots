FROM python:3.8

WORKDIR /bot_app

COPY . .

RUN mv /bot_app/data_files/secret_keys_example.py /bot_app/data_files/secret_keys.py
RUN sed -i -e "s|^BOT_TOKEN *=.*|BOT_TOKEN = '<you_token_bot>'|" /bot_app/data_files/secret_keys.py
RUN pip install -r requirements.txt

CMD ["python3", "-u", "./bot_start.py"]
