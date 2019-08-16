# Space Instagram

A set of console utilities allows you to automatically download photos from open sources (spaceX, Hubble)
and post them on Instagram.

### How to install

Create the file `.env` in the project folder. Open in a text editor and type

```
INSTA_LOGIN=my_insta_login
INSTA_PASSWORD=my_insta_passwd
```
instead of __`my_insta_login`__ and __`my_insta_passwd`__, insert your username and password for your instagram account.

Python3 should be already installed. 
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```

### Usage

In the console, navigate to the project folder, and then run:
```
python fetch_spacex.py

python fetch_hubble.py <collection>
 
python post_pics.py
```

- fetch_spacex.py - script downloads photos of the last launch of SpaceX.
 
- fetch_hubble.py <collection> - script downloads the specified pictures photo collection from the Hubble's service (the default is an empty argument), instead of <collection> enter the name of one of the collections: "holiday_cards", "wallpaper", "spacecraft", "news", "printshop", "stsci_gallery" (without the quotes).

 - post_pics.py - script publishes photos in Your Instagram account.

### Project goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).