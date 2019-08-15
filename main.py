import glob
import os
import shutil
import time
from io import open
from pathlib import Path

import requests
from dotenv import load_dotenv
from instabot import Bot
from instabot.api.api_photo import (compatible_aspect_ratio, get_image_size,
                                    resize_image)
from PIL import Image, ImageFile
from requests.compat import urljoin, urlparse
from requests.exceptions import HTTPError


SPACEX_API_URL = "https://api.spacexdata.com/v3/"
HUBBLE_API_IMAGE_URL = "http://hubblesite.org/api/v3/image/"
HUBBLE_API_IMAGES_URL = "http://hubblesite.org/api/v3/images/"

DEFAULT_CHUNK_SIZE = 1024
TIMEOUT_BETWEEN_POSTS = 5

IMAGES_FOLDER = "images"
PICTURES_EXTENTIONS = (
    'jpg', 'JPG', 'jpeg', 'JPEG',
)
PICTURES_EXTENTIONS_FOR_CONVERTION = (
    'png', 'tif', 'PNG', 'TIF'
)

DEFAULT_HASHTAGS = [
    "#space", "#sky", "#galaxy", "#hubble",
    "#spacepics", "#stars", "#solar"
]


def get_file_extension(link=""):
    parts = link.split(".")
    return parts[-1]


def replace_ext(filename="", ext=""):
    filename_w_ext, _ = os.path.splitext(filename)
    return "".join([filename_w_ext, ext])


def convert_tif_to_jpg(filename=""):
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    image = Image.open(filename)
    image.save(
        replace_ext(filename, '.jpg'), 'JPEG'
    )


def convert_png_to_jpg(filename=""):
    image = Image.open(filename)
    rgb_image = image.convert('RGB')
    rgb_image.save(
        replace_ext(filename, '.jpg')
    )


def download_image(url="", folder="", img_name="", rewrite=False):
    """Function for downloading image by given url 
    and saving it to given folder."""
    try:
        os.makedirs(folder)
    except FileExistsError:
        pass

    file_name = os.path.join(folder, img_name)
    path = Path(file_name)

    # если есть опция перезаписи и если уже есть такой файл, то не скачиваем
    if not rewrite and path.is_file():
        print(("File with name {0} "
             "already exist... stop downloading").format(file_name))
        return

    print("Downloading {0}\n".format(url))
    response = requests.get(
        url=url, stream=True, verify=False
    )
    response.raise_for_status()

    with open(file_name, 'wb') as file:
        for chunk in response.iter_content(DEFAULT_CHUNK_SIZE):
            file.write(chunk)


def get_all_launches_with_images():
    """Returns dict with all last and previous launches if it having images."""
    all_launches_url_path = "launches"
    all_launches_url = urljoin(
        SPACEX_API_URL, all_launches_url_path
    )
    response = requests.get(
        url=all_launches_url
    )
    response.raise_for_status()

    launches_with_images = {}
    for launch in response.json():
        if launch['links']['flickr_images']:
            launches_with_images[
                launch['flight_number']
            ] = launch['links']['flickr_images'] 
    return launches_with_images


def get_latest_launch_images_links():
    """Return structure with latest links of spacex launches."""
    latest_launch_url_path = "launches/latest"
    latest_launch_url = urljoin(
        SPACEX_API_URL, latest_launch_url_path
    )
    response = requests.get(
        url=latest_launch_url
    )
    response.raise_for_status()

    latest_launch_images_links = response.json()['links']['flickr_images']
    if not latest_launch_images_links:
        all_launches = get_all_launches_with_images()
        # последний по номеру запуск
        latest_launch_images_links = all_launches[max(all_launches)]

    return latest_launch_images_links


def fetch_spacex_last_launch():
    """Download all pics from last SpaceX launch."""
    default_filename = "spacex"

    for num, link in enumerate(get_latest_launch_images_links()):
        file_ext = get_file_extension(link)
        file_name = ".".join(
            [default_filename + str(num), file_ext]
        )
        download_image(
            url=link,
            folder=IMAGES_FOLDER,
            img_name=file_name
        )


def fetch_image_hubble(image_id=""):
    """Download one pic by id from Hubble Site."""
    response = requests.get(
        url=urljoin(HUBBLE_API_IMAGE_URL, str(image_id))
    )
    response.raise_for_status()
    image_files = response.json()["image_files"]

    links = []
    for image_file in image_files:
        links.append(
            image_file["file_url"]
        )
    # берем последнюю ссылку, фото лучшего качества
    final_image_link = "".join(["https:", links[-1]])

    file_name = ".".join(
        [
            str(image_id),
            get_file_extension(final_image_link)
        ]
    )

    download_image(
        url=final_image_link,
        folder=IMAGES_FOLDER,
        img_name=file_name
    )


def fetch_hubble_collection_images(collection_name=""):
    """Fetch pics of collection from Hubble Site."""
    url = urljoin(HUBBLE_API_IMAGES_URL, collection_name)
    response = requests.get(url, verify=False)
    response.raise_for_status()
    images = response.json()

    for image in images:
        fetch_image_hubble(image["id"])


def convert_images_to_jpg(folder=""):
    """Function for convertation pics to Jpg format,
    https://github.com/mgp25/Instagram-API/issues/1"""
    pics = glob.glob(
        "".join(["./", IMAGES_FOLDER, "/*.*"])
    )
    pics = filter(
        lambda file: file.endswith(PICTURES_EXTENTIONS_FOR_CONVERTION),
        pics
    )
    for img in pics:
        ext = get_file_extension(img)
        if ext.lower() == 'tif':
            convert_tif_to_jpg(img)
        elif ext.lower() ==  'png':
            convert_png_to_jpg(img)
        else:
            pass


def post_pics():
    posted_pic_list = []
    timeout = 5
    try:
        with open('pics.txt', 'r', encoding='utf8') as f:
            posted_pic_list = f.read().splitlines()
    except Exception:
        posted_pic_list = []

    insta_login = os.getenv("INSTA_LOGIN")
    insta_password = os.getenv("INSTA_PASSWORD")
    bot = Bot()
    bot.login(
        username=insta_login,
        password=insta_password
    )

    while True:
        pics = glob.glob(
            "".join(["./", IMAGES_FOLDER, "/*.*"])
        )
        pics = filter(
            lambda file: file.endswith(PICTURES_EXTENTIONS),
            pics
        )
        pics = sorted(pics)
        try:
            for pic in pics:
                if pic in posted_pic_list:
                    continue

                caption = " ".join(DEFAULT_HASHTAGS)

                print("upload: " + pic)
                if not compatible_aspect_ratio(get_image_size(pic)):
                    old_pic = pic
                    pic = resize_image(pic)
                    print("old pic: {0} --> new pic {1}".format(old_pic, pic))

                bot.upload_photo(pic, caption=caption)

                if bot.api.last_response.status_code != 200:
                    print(bot.api.last_response)
                    break

                if pic not in posted_pic_list:
                    posted_pic_list.append(pic)
                    with open('pics.txt', 'a', encoding='utf8') as f:
                        f.write(pic + "\n")
                if old_pic not in posted_pic_list:
                    posted_pic_list.append(old_pic)
                    with open('pics.txt', 'a', encoding='utf8') as f:
                            f.write(old_pic + "\n")

                time.sleep(TIMEOUT_BETWEEN_POSTS)

        except Exception as e:
            print(str(e))
        time.sleep(5)


def main():
    load_dotenv()
    try:
        # download pics of last SpaceX launch
        fetch_spacex_last_launch()
    
        # download pics of collection from Hubble Site
        fetch_hubble_collection_images(
            "stsci_gallery"
        )
        convert_images_to_jpg()
    except HTTPError as error:
        exit("Невозможно получить данные с сервера:\n{0}\n".format(error))
    # post pics to instagram
    post_pics()


if __name__ == "__main__":
    main()
