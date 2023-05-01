FROM python:3.8

WORKDIR /Shipping_Calculation

COPY . .

RUN mv /Shipping_Calculation/data_files/data_file_example.py /Shipping_Calculation/data_files/data_file.py
RUN sed -i -e "s|^BOT_TOKEN *=.*|BOT_TOKEN = '<your_bot_token>'|; \
    s|^API_VOZOVOZ *=.*|API_VOZOVOZ = '<your_api_vozovoz>'|; \
    s|^API_DELLINE *=.*|API_DELLINE = '<your_api_delline>'|; \
    s|^cdek_client_id *=.*|cdek_client_id = '<your_cdek_client_id>'|; \
    s|^cdek_client_secret *=.*|cdek_client_secret = '<your_cdek_client_secret>'|; \
    s|^jde_user_id *=.*|jde_user_id = '<your_jde_user_id>'|; \
    s|^jde_apy_key *=.*|jde_apy_key = '<your_jde_apy_key>'|" /Shipping_Calculation/data_files/data_file.py
RUN pip install -r requirements.txt

CMD ["python3", "-u", "./shipper_calc_bot_start.py"]