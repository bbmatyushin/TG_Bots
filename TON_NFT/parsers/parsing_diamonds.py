from requests import Session
from fake_headers import Headers
import time
from import_mylib.data_file import collections


def get_response(url, current_page):
    ses = Session()
    params = {'perPage': '16',
              'currentPage': current_page,
              'traits[0][name]': 'Status',
              'traits[0][values][0]': 'sale',
              'sortBy[rarity]': 'desc'}
    headers = Headers().generate()
    ses.headers.update(headers)
    response = ses.get(url, params=params, stream=True).json()

    return response


def get_attributes(url):
    ses = Session()
    headers = Headers().generate()
    ses.headers.update(headers)
    attr_response = ses.get(url).json()
    if not attr_response['attributes']:
        return 'Unknown'
    else:
        attr_value = attr_response['attributes'][0]['value']
        return attr_value


def get_data(collection='ton-diamonds'):
    """
    Сам объект храниться в модуле import_mylib.data_file"""
    url = f"https://ton.diamonds/api/v1/collections/{collection}/list"
    current_page = 1

    while True:
        time.sleep(2)
        response = get_response(url, current_page)
        for i in range(len(response['data']['rows'])):
            url_for_attr = response['data']['rows'][i]['externalLink']
            url_image = response['data']['rows'][i]['rawImageUrl']
            name = response['data']['rows'][i]['name']
            attribute = get_attributes(url_for_attr)  # link for search size
            nft_status = response['data']['rows'][i]['nftStatus']
            last_sale_price = round(float(response['data']['rows'][i]['nftLastSalePrice']), 2)
            current_price = round(float(response['data']['rows'][i]['nftSalePrice']), 2)
            rar_val = response['data']['rows'][i]['rarity']
            if rar_val is None:
                rarity = float(0)
            else:
                rarity = round(float(rar_val), 2)
            nft_address = response['data']['rows'][i]['nftAddress']
            collection_address = response['data']['rows'][i]['nftCollectionAddress']

            yield name, attribute, rarity, last_sale_price, current_price, nft_status, url_image, \
                nft_address, collection_address

        current_page += 1
        # last_page = 4  # for test
        last_page = response['data']['lastPage']
        if current_page > last_page:
            break


# Написано для теста, как отрабатывает парсер
def parsing_diamonds():
    with open('diamonds_data.txt', 'w') as f:
        for line in get_data():
            f.write(f'Name: {list(line)[0]}; Attribute: {list(line)[1]}; Price: {list(line)[4]} TON\n')
    # print(list(get_data()))
    print(1)


if __name__ == '__main__':
    parsing_diamonds()
