import requests
from fake_headers import Headers
from pathlib import Path
from postgres_db import diamonds_select


def download_image(url: str, name: str, dir='diamonds'):
    headers = Headers().generate()
    response = requests.get(url, headers=headers, stream=True)
    with open(f"{Path('images', f'{dir}', f'{name}')}.png", "wb") as f:
        for value in response.iter_content(1024*100):
            f.write(value)


def get_diamonds_images():
    files_list = [str(file.name)[:-4] for file in Path(Path.cwd(), 'images', 'diamonds').iterdir()]

    return files_list


def get_path_to_images(img_name, dir='diamonds'):
    if img_name not in get_diamonds_images():

        image_path = ''
        # download_image(url, img_name, dir)
    else:
        image_path = f"{Path(Path.cwd(), 'images', f'{dir}', f'{img_name}')}.png"

    return image_path


if __name__ == '__main__':
    get_path_to_images('Diamond #880')

    # names = diamonds_select.ton_diamonds_top_5_select('10000')
    # for name in names:
    #     data = diamonds_select.ton_diamonds_url_images_select(name[0])
    #     for i in data:
    #         download_image(i[1], i[0])
    #         print(1)

    # url = 'https://nft.ton.diamonds/nft/3479/3479.svg'
    # name = 'Diamond #3480'
    # print(get_path_to_images(url, name))


