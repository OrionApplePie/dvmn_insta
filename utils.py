import glob
import os
from pathlib import Path

import requests
from PIL import Image, ImageFile

DEFAULT_CHUNK_SIZE = 1024

IMAGES_FOLDER = "images"

PICTURES_EXTENTIONS_FOR_CONVERTION = (
    'png', 'tif', 'PNG', 'TIF'
)

def download_image(url="", img_path="", img_name="", rewrite=True):
    """Function for downloading image by given url 
    and saving it to given folder."""
    try:
        os.makedirs(img_path)
    except FileExistsError:
        pass

    file_name = os.path.join(img_path, img_name)
    path = Path(file_name)

    # если есть опция перезаписи и если уже есть такой файл, то не скачиваем
    if not rewrite and path.is_file():
        print(("File with name {0} "
             "already exist... stop downloading").format(file_name))
        return

    response = requests.get(
        url=url, stream=True, verify=False
    )
    response.raise_for_status()

    with open(file_name, 'wb') as file:
        for chunk in response.iter_content(DEFAULT_CHUNK_SIZE):
            file.write(chunk)


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
        ext = img.split(".")[-1]
        if ext.lower() == 'tif':
            convert_tif_to_jpg(img)
        elif ext.lower() ==  'png':
            convert_png_to_jpg(img)
        else:
            pass
