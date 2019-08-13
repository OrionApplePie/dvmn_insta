import requests
from requests.compat import urljoin


HUBBLE_API_URL = "http://hubblesite.org/api/v3/image/"

def get_file_extension(link=""):
    parts = link.split(".")
    return parts[-1]


def main():
    response = requests.get(
        url=urljoin(HUBBLE_API_URL, "1")
    )
    response.raise_for_status()
    image_files = response.json()["image_files"]

    links = []
    for image_file in image_files:
        links.append(
            image_file["file_url"]
        )
    for link in links:
        print(
            "link: {0} --> ext: {1} "
            .format(link, get_file_extension(link=link))
        )
    print(links[-1])



if __name__ == "__main__":
    main()
