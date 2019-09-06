import glob
import logging
import os
import time
from io import open

from dotenv import load_dotenv
from instabot import Bot
from instabot.api.api_photo import (compatible_aspect_ratio, get_image_size,
                                    resize_image)
from requests.exceptions import ConnectionError

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

logging.basicConfig(filename="logs.log", level=logging.INFO)


def remember_pic(pics=[], posted_pic_list=None, file_name=""):
    """Записывает в файл имена файлов фотографий,
    которые еще не были опубликованы."""
    for pic in pics:
        if pic and pic not in posted_pic_list:
            posted_pic_list.append(pic)
            with open(file_name, 'a', encoding='utf8') as file:
                file.write(pic + "\n")


def pics_generator(pics=[], posted_pic_list=None):
    for pic in pics:
        new_pic = ""
        if pic not in posted_pic_list:
            if not compatible_aspect_ratio(get_image_size(pic)):
                new_pic = resize_image(pic)
            yield pic, new_pic 


def post_pics():
    posted_pic_list = []
    try:
        with open('pics.txt', 'r', encoding='utf8') as file:
            posted_pic_list = file.read().splitlines()
    except IOError:
        posted_pic_list = []

    caption = " ".join(DEFAULT_HASHTAGS)
    insta_login = os.getenv("INSTA_LOGIN")
    insta_password = os.getenv("INSTA_PASSWORD")
    bot = Bot()
    bot.login(
        username=insta_login,
        password=insta_password
    )

    while True:
        pics = [
            pic for pic in glob.glob(f"./{IMAGES_FOLDER}/*.*")
            if pic.endswith(PICTURES_EXTENTIONS)
        ]
        pics = sorted(pics)

        for pic, new_pic in pics_generator(pics, posted_pic_list):
            pic_load = new_pic if new_pic else pic
            print(f"Загрузка: {pic_load}")
            try:
                bot.upload_photo(pic_load, caption=caption)
            except ConnectionError as error:
                logging.error(str(error))
                print("connetion error ! continue!")
                continue

            if bot.api.last_response.status_code != 200:
                logging.error(bot.api.last_response)
                continue
            remember_pic(
                pics=[pic, new_pic],
                posted_pic_list=posted_pic_list,
                file_name="pics.txt"
            )
            time.sleep(TIMEOUT_BETWEEN_POSTS)
        time.sleep(5)


def main():
    load_dotenv()
    convert_images_to_jpg()
    post_pics()


if __name__ == "__main__":
    main()
