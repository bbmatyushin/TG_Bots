import requests
import os
import re


shipper_list_full_name = ['ВОЗОВОЗ', 'Деловые Линии', 'ЖелДорЭкспедиция', 'CDEK']
shipper_list = ['ВОЗОВОЗ', 'Деловые', 'ЖДЭ', 'CDEK']

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_json_data = re.sub("Shipping_Calculation.*", "Shipping_Calculation/json_data", dir_path)

def get_cdek_token(client_id, client_secret):
    """Получаем токен, который будет действителен в течении 1 часа
    описание здесь https://api-docs.cdek.ru/29923849.html"""

    url = 'https://api.cdek.ru/v2/oauth/token'
    params = {
        "grant_type": "client_credentials",
        "client_id": f"{client_id}",
        "client_secret": f"{client_secret}"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=params, json=headers)
    cdek_token = response.json()['access_token']

    return cdek_token


if __name__ == "__main__":
    print(dir_json_data)
