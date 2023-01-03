import requests
from fake_headers import Headers
import time


def get_response(current_page):
    url = "https://ton.diamonds/api/v1/collections/ton-diamonds/list"
    params = {'perPage': '16',
              'currentPage': current_page,
              'traits[0][name]': 'Status',
              'traits[0][values][0]': 'sale',
              'sortBy[rarity]': 'desc'}
    headers = Headers().generate()
    response = requests.get(url, params=params, headers=headers, stream=True).json()

    return response

def get_diamond_attributes(url):
    headers = Headers().generate()
    attr_response = requests.get(url, headers=headers).json()
    size = attr_response['attributes'][0]['value']

    return size


def get_data():
    current_page = 1
    response = get_response(current_page)

    last_page = response['data']['lastPage']

    while current_page <= last_page:
        for i in range(len(response['data']['rows'])):
            url_for_attr = response['data']['rows'][i]['externalLink']
            url_image = response['data']['rows'][i]['rawImageUrl']
            name = response['data']['rows'][i]['name']
            size = get_diamond_attributes(url_for_attr)  # link for search size
            nft_status = response['data']['rows'][i]['nftStatus']
            last_sale_price = round(float(response['data']['rows'][i]['nftLastSalePrice']), 2)
            current_price = round(float(response['data']['rows'][i]['nftSalePrice']), 2)
            rarity = round(float(response['data']['rows'][i]['rarity']), 2)

            yield name, size, rarity, last_sale_price, current_price, nft_status, url_image

        current_page += 1
        time.sleep(2)
        response = get_response(current_page)


def parsing_diamonds():
    with open('../diamonds_data.txt', 'w') as f:
        for line in get_data():
            f.write(f'Name: {list(line)[0]}; Size: {list(line)[1]}; Price: {list(line)[4]} TON\n')
    # print(list(get_data()))
    print(1)


if __name__ == '__main__':
    parsing_diamonds()