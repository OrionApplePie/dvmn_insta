#!/usr/bin/env python3
import requests
from requests.compat import urljoin
from requests.exceptions import HTTPError

from utils import download_image

SPACEX_API_URL = "https://api.spacexdata.com/v3/"

IMAGES_FOLDER = "images"


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
    """Return structure with links of latest spacex launch."""
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


def fetch_spacex_last_launch(images_path=IMAGES_FOLDER):
    """Download pics from last SpaceX launch."""
    default_filename = "spacex"

    for num, link in enumerate(get_latest_launch_images_links()):
        file_ext = link.split(".")[-1]
        file_name = f"{default_filename}{str(num)}.{file_ext}"

        print("Download by link: {0} ".format(link))
        download_image(
            url=link,
            img_path=images_path,
            img_name=file_name
        )
        print("File {0} saved".format(file_name))


def main():
    try:
        fetch_spacex_last_launch()
    except HTTPError as error:
        exit("Невозможно получить данные с сервера:\n{0}\n".format(error))


if __name__ == "__main__":
    main()
