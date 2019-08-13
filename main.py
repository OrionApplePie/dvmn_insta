import os
import glob

from instabot import Bot
import requests
from requests.compat import urlparse, urljoin


IMAGES_FOLDER = "images"
SPACEX_API_URL = "https://api.spacexdata.com/v3/"
HUBBLE_API_IMAGE_URL = "http://hubblesite.org/api/v3/image/"
HUBBLE_API_IMAGES_URL = "http://hubblesite.org/api/v3/images/"


def download_image(url="", folder="", img_name=""):
    """Function for downloading image by given url
    and saving it to given folder."""
    try:
        os.makedirs(folder)
    except FileExistsError:
        pass
    # print("Downloading {0}\n".format(url))
    response = requests.get(
        url=url, verify=False
    )
    response.raise_for_status()
    file_name = os.path.join(folder, img_name)

    with open(file_name, 'wb') as file:
        file.write(response.content)


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


def main():
    # download pics of last SpaceX launch
    fetch_spacex_last_launch()

    # download pics of collection from Hubble Site
    fetch_hubble_collection_images(
        "holiday_cards"
    )

    # # Upload pics from image folder to Instagram
    # bot = Bot()
    # bot.login()
    # pics = glob.glob("./images/*.jpg")

    # try:
    #     for pic in pics:
    #         print(pic)
    #         bot.upload_photo(pic, caption="testing")
    #         if bot.api.last_response.status_code != 200:
    #             print(bot.api.last_response)
    # except Exception as e:
    #     print(str(e))


if __name__ == "__main__":
    main()
