import argparse
import os
import glob

import requests
from requests.compat import urlparse, urljoin
from instabot import Bot


IMAGES_FOLDER = "images"
BASE_SPACEX_API_URL = "https://api.spacexdata.com/v3/"
HUBBLE_API_IMAGE_URL = "http://hubblesite.org/api/v3/image/"
HUBBLE_API_IMAGES_URL = "http://hubblesite.org/api/v3/images/"


def download_image(url="", folder="", img_name=""):
    """Function for downloading image by given url and save it to folder."""
    response = requests.get(
        url=url, verify=False
    )
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


def get_file_extension(link=""):
    parts = link.split(".")
    return parts[-1]


def fetch_image_hubble(image_id=""):
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
    final_image_link = "".join(["https:", links[-1]])
    print(final_image_link)
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

def get_hubble_collection_images_ids(collection_name=""):
    """Fetch id's of collection."""
    url = urljoin(HUBBLE_API_IMAGES_URL, collection_name)
    print(url)
    response = requests.get(url, verify=False)
    response.raise_for_status()
    images_ids = []
    images = response.json()
    for image in images:
        images_ids.append(image["id"])
    return images_ids


def main():
    # fetch_spacex_last_launch()
    # fetch_image_hubble(4001)
    # ids = get_hubble_collection_images_ids("spacecraft")
    # print(ids)
    # for id in ids:
    #     print("downloading {0}".format(id))
    #     fetch_image_hubble(id)
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('-u', type=str, help="username")
    parser.add_argument('-p', type=str, help="password")
    parser.add_argument('-caption', type=str, help="caption for photo")
    args = parser.parse_args()

    bot = Bot()
    bot.login()
    user_id = bot.get_user_id_from_username("north_viking_saw")
    user_info = bot.get_user_info(user_id)
    print(user_info['biography'])

    pics = glob.glob("./images/pics/*.jpg")
    try:
        for pic in pics:
            print(pic)
            bot.upload_photo(pic, caption="testing")
            if bot.api.last_response.status_code != 200:
                print(bot.api.last_response)
    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    main()
