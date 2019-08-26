import glob
import os
import time
from io import open

from dotenv import load_dotenv
from instabot import Bot
from instabot.api.api_photo import (compatible_aspect_ratio, get_image_size,
                                    resize_image)

from utils import convert_images_to_jpg

TIMEOUT_BETWEEN_POSTS = 5

IMAGES_FOLDER = "images"

PICTURES_EXTENTIONS = (
    'jpg', 'JPG', 'jpeg', 'JPEG',
)

DEFAULT_HASHTAGS = [
    "#space", "#sky", "#galaxy", "#hubble",
    "#spacepics", "#stars", "#solar"
]


def post_pics():
    posted_pic_list = []
    try:
        with open('pics.txt', 'r', encoding='utf8') as file:
            posted_pic_list = file.read().splitlines()
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
        pics = glob.glob(f"./{IMAGES_FOLDER}/*.*")
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
                    with open('pics.txt', 'a', encoding='utf8') as file:
                        file.write(pic + "\n")

                if old_pic not in posted_pic_list:
                    posted_pic_list.append(old_pic)
                    with open('pics.txt', 'a', encoding='utf8') as file:
                        file.write(old_pic + "\n")

                time.sleep(TIMEOUT_BETWEEN_POSTS)

        except Exception as exception:
            print(str(exception))
        time.sleep(5)

def main():
    load_dotenv()
    convert_images_to_jpg()
    post_pics()


if __name__ == "__main__":
    main()
