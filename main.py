"""
Урок 4. Загрузите в Instagram фотографии космоса.
"""
import os
import requests

IMAGES_FOLDER = "images"


def download_image(url="", img_name=""):
    """Function for downloading image by given url."""
    file_name = os.path.join(IMAGES_FOLDER, img_name)

    response = requests.get(url)
    response.raise_for_status()

    with open(file_name, 'wb') as file:
        file.write(response.content)


def main():
    try:
        os.makedirs(IMAGES_FOLDER)
    except FileExistsError:
        print("folder exist, skipping...")
    
    BASE_SPACEX_API_URL = "https://api.spacexdata.com/v3"
    
    img_url = "https://upload.wikimedia.org/wikipedia/commons/3/3f/HST-SM4.jpeg"
    img_name = "hubble.jpeg"
    
    download_image(
        url=img_url,
        img_name=img_name
    )
    r = requests.get(
        url="https://api.spacexdata.com/v3/launches/latest"
    )
    print(r.text)


if __name__ == "__main__":
    main()
