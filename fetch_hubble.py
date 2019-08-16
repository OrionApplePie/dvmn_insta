#!/usr/bin/env python3
import argparse

import requests
from requests.compat import urljoin
from requests.exceptions import HTTPError

from utils import download_image

HUBBLE_API_IMAGE_URL = "http://hubblesite.org/api/v3/image/"
HUBBLE_API_IMAGES_URL = "http://hubblesite.org/api/v3/images/"

IMAGES_FOLDER = "images"


def fetch_hubble_image(image_id=""):
    """Download one pic by id from Hubble Site."""
    file_name = "".join(
        ["hubble", str(image_id)]
    )
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
    file_ext = final_image_link.split(".")[-1]
    file_name = ".".join(
        [
            file_name,
            file_ext
        ]
    )
    print("Download by link: {0} ".format(final_image_link))
    download_image(
        url=final_image_link,
        img_path=IMAGES_FOLDER,
        img_name=file_name
    )
    print("File {0} saved".format(file_name))


def fetch_hubble_collection_images(collection_name=""):
    """Fetch pics of collection from Hubble Site."""
    url = urljoin(HUBBLE_API_IMAGES_URL, collection_name)

    response = requests.get(url, verify=False)
    response.raise_for_status()
    images = response.json()

    for image in images:
        fetch_hubble_image(image["id"])


def main():
    app_description = (
        "Консольная утилита для загрузки фотографий"
        " сделанных телескопом Хаббл."
    ) 
    parser = argparse.ArgumentParser(
        description=app_description
    )
    parser.add_argument(
        "collection",
        help="Назване коллекции фотоснимков Хаббла.",
        nargs="?", const="", type=str  # by default empty parameter is 'science' collection 
    )
    args = parser.parse_args()
    collection = args.collection
    try:
        fetch_hubble_collection_images(collection)
    except HTTPError as error:
        exit("Невозможно получить данные с сервера:\n{0}\n".format(error))


if __name__ == "__main__":
    main()
