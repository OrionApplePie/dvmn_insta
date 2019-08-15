import glob
import os
import shutil
import time
from io import open

from pathlib import Path

import requests
from instabot import Bot
from instabot.api.api_photo import (compatible_aspect_ratio, get_image_size,
                                    resize_image)
from PIL import ImageFile, Image
from requests.compat import urljoin, urlparse

IMAGES_FOLDER = "images"
PICTURES_EXTENTIONS = (
    'jpg', 'JPG', 'jpeg', 'JPEG',
)
PICTURES_EXTENTIONS_FOR_CONVERTION = (
    'png', 'tif'
)

SPACEX_API_URL = "https://api.spacexdata.com/v3/"
HUBBLE_API_IMAGE_URL = "http://hubblesite.org/api/v3/image/"
HUBBLE_API_IMAGES_URL = "http://hubblesite.org/api/v3/images/"



def get_filename_and_extension_apart(file_path=""):
    filename_w_ext = os.path.basename(file_path)
    filename, file_extension = os.path.splitext(filename_w_ext)
    return filename, file_extension


def convert_tif_to_jpg(name=""):
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    im = Image.open(name)
    file_name = os.path.splitext(name)[0]
    im.save(file_name + '.jpg', 'JPEG')


def convert_png_to_jpg(name=""):
    filename, _ = get_filename_and_extension_apart(name)
    path, _ = os.path.split(name)
    im = Image.open(name)
    rgb_im = im.convert('RGB')
    rgb_im.save(os.path.join(path, filename) + '.jpg')


def download_image(url="", folder="", img_name=""):
    """Function for downloading image by given url 
    and saving it to given folder."""
    try:
        os.makedirs(folder)
    except FileExistsError:
        pass
    file_name = os.path.join(folder, img_name)
    path = Path(file_name)
    if path.is_file():
        print(("file with name {0}"
             "alredy exist... stop downloading").format(file_name))
        return

    print("Downloading {0}\n".format(url))
    response = requests.get(
        url=url, stream=True, verify=False
    )
    response.raise_for_status()

    with open(file_name, 'wb') as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)


def download_image2(url="", folder="", img_name=""):
    """Function for downloading image by given url
    and saving it to given folder."""
    try:
        os.makedirs(folder)
    except FileExistsError:
        pass
    print("Downloading {0}\n".format(url))
    r = requests.get(
        url=url, stream=True, verify=False
    )
    r.raise_for_status()

    file_name = os.path.join(folder, img_name)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)        


def download_file(url="", folder="", img_name=""):
    try:
        os.makedirs(folder)
    except FileExistsError:
        pass
    print("Downloading {0}\n".format(url))
    file_name = os.path.join(folder, img_name)
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True, verify=False) as r:
        r.raise_for_status()
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()


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
        # get last number
        latest_launch_images_links = all_launches[max(all_launches)]

    return latest_launch_images_links


def get_file_extension(link=""):
    parts = link.split(".")
    return parts[-1]


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
    # use last link - best quality image
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
    """https://github.com/mgp25/Instagram-API/issues/1"""
    pics = glob.glob("./images/*.*")
    pics = filter(
        lambda file: file.endswith(PICTURES_EXTENTIONS_FOR_CONVERTION),
        pics
    )
    for img in pics:
        _, ext = os.path.splitext(img)
        if ext.lower() == '.tif':
            convert_tif_to_jpg(img)
        elif ext.lower() ==  '.png':
            convert_png_to_jpg(img)
        else:
            pass


def post_pics():
    posted_pic_list = []
    try:
        with open('pics.txt', 'r', encoding='utf8') as f:
            posted_pic_list = f.read().splitlines()
    except Exception:
        posted_pic_list = []

    timeout = 5

    bot = Bot()
    bot.login()

    while True:
        pics = glob.glob("./images/*.*")
        pics = filter(
            lambda file: file.endswith(PICTURES_EXTENTIONS),
            pics
        )
        pics = sorted(pics)
        try:
            for pic in pics:
                if pic in posted_pic_list:
                    continue

                caption = pic[:-4].split(" ")
                caption = " ".join(caption[1:])

                print("upload: " + pic)
                if not compatible_aspect_ratio(get_image_size(pic)):
                    old_pic = pic
                    pic = resize_image(pic)
                    print("old pic; {0} --> new pic {1}".format(old_pic, pic))
                bot.upload_photo(pic, caption=caption)

                if bot.api.last_response.status_code != 200:
                    print(bot.api.last_response)
                    # snd msg
                    break

                if pic not in posted_pic_list:
                    posted_pic_list.append(pic)
                    with open('pics.txt', 'a', encoding='utf8') as f:
                        f.write(pic + "\n")
                if old_pic not in posted_pic_list:
                    posted_pic_list.append(old_pic)
                    with open('pics.txt', 'a', encoding='utf8') as f:
                            f.write(old_pic + "\n")
    
                time.sleep(timeout)

        except Exception as e:
            print(str(e))
        time.sleep(5)


def main():
    # download pics of last SpaceX launch
    fetch_spacex_last_launch()

    # download pics of collection from Hubble Site
    fetch_hubble_collection_images(
        "stsci_gallery"
    )
    convert_images_to_jpg()

    # post pics to instagram
    post_pics()


if __name__ == "__main__":
    main()
