import os

import requests
from requests.compat import urlparse, urljoin


BASE_SPACEX_API_URL = "https://api.spacexdata.com/v3/"
IMAGES_FOLDER = "images"


def download_image(url="", folder="", img_name=""):
    """Function for downloading image by given url and save it to folder."""
    response = requests.get(url)
    response.raise_for_status()
    # TODO: make names by enumerate
    file_name = os.path.join(folder, img_name)
    with open(file_name, 'wb') as file:
        file.write(response.content)


def get_filename_by_link(link=""):
    url_path = urlparse(link).path
    filename = os.path.basename(url_path)
    return filename


def get_all_launches_with_images():
    all_launches_url_path = "launches"
    all_launches_url = urljoin(
        BASE_SPACEX_API_URL, all_launches_url_path
    )
    response = requests.get(
        url=all_launches_url
    )
    response.raise_for_status()
    launches_with_images = {}
    for launch in response.json():
        if launch['links']['flickr_images']:
            launches_with_images[launch['flight_number']] = {
                "launch_date": launch['launch_date_utc'],
                "flickr_images": launch['links']['flickr_images'] 
            }
    return launches_with_images


def get_latest_launch_images_links():
    """Return structure with latest links of spacex launches."""
    latest_launch_url_path = "launches/latest"
    latest_launch_url = urljoin(
        BASE_SPACEX_API_URL, latest_launch_url_path
    )
    response = requests.get(
        url=latest_launch_url
    )
    response.raise_for_status()
    latest_launch_images_links = response.json()['links']['flickr_images']
    if not latest_launch_images_links:
        all_launches = get_all_launches_with_images()
        latest_launch = all_launches[max(all_launches)]
        latest_launch_images_links = latest_launch['flickr_images']

    return latest_launch_images_links


def fetch_spacex_last_launch():
    try:
        os.makedirs(IMAGES_FOLDER)
    except FileExistsError:
        print("folder exist, skipping...")

    for link in get_latest_launch_images_links():
        file_name = get_filename_by_link(link)
        download_image(
            url=link,
            folder=IMAGES_FOLDER,
            img_name=file_name
        )


def main():
    fetch_spacex_last_launch()


if __name__ == "__main__":
    main()
