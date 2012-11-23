#!/usr/bin/env python
# 
# Copyright (c) 2012 David Drake
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# 
# nasa_apod_desktop.py
# https://github.com/randomdrake/nasa-apod-desktop
# 
# Written/Modified by David Drake
# http://randomdrake.com 
# http://twitter.com/randomdrake 
# 
# 
# Tested on Ubuntu 12.04
# 
# 
# DESCRIPTION
# 1) Grabs your current download path
# 2) Downloads the latest image of the day from NASA (http://apod.nasa.gov/apod/)
# 3) Determines your desktop resolution, or uses the set default.
# 4) Resizes the image to the given resolution.
# 5) Sets the image as your desktop.
# 6) Adds image to XML file used to scroll through desktop background images.
#
# It's not very exciting to scroll through a single image, so it will attempt to download 
# additional images (default: 10) to seed your list of images.
#
# 
# INSTALLATION
# Place the file wherever you like and chmod +x it to make it executable
# Ensure you have Python installed (default for Ubuntu) and the PIL and lxml packages:
# pip install -f requirements.txt or sudo apt-get install python-imaging python-lxml
# 
#
# RUN AT STARTUP
# To have this run whenever you startup your computer, perform the following steps:
# 1) Click on the settings button (cog in top right)
# 2) Select "Startup Applications..."
# 3) Click the "Add" button
# 4) Enter whatever Name and Comment you like with the following Command:
# python /path/to/nasa_apod_desktop.py
# 5) Click on the "Add" button
# 
# DEFAULTS
# While the script will detect as much as possible and has safe defaults, you may want to set your own.
# 
# DOWNLOAD_PATH  - where you want the file to be downloaded. Will be auto-detected if not set.
# CUSTOM_FOLDER  - if we detect your download folder, this will be the target folder in there.
# RESOUTION_TYPE - 
#     'stretch': single monitor or the combined resolution of your available monitors
#     'largest': largest resolution of your available monitors
#     'default': use the default resolution that is set
# RESOLUTION_X   - horizontal resolution if RESOLUTION_TYPE is not default or cannot be 
#                  automatically determined
# RESOLUTION_Y   - vertical resolution if RESOLUTION_TYPE is not default or cannot be
#                  automatically determined
# NASA_APOD_SITE - location of the current picture of the day
# IMAGE_SCROLL   - if true, will write also write an XML file to make the images scroll
# IMAGE_DURATION - if IMAGE_SCROLL is enabled, this is the duration each will stay in seconds
# SEED_IMAGES    - if > 0, it will download previous images as well to seed the list of images
# SHOW_DEBUG     - print useful debugging information or statuses

DOWNLOAD_PATH = '/tmp/backgrounds/'
CUSTOM_FOLDER = 'nasa-apod-backgrounds'
RESOLUTION_TYPE = 'stretch'
RESOLUTION_X = 1024
RESOLUTION_Y = 768
NASA_APOD_SITE = 'http://apod.nasa.gov/apod/'
IMAGE_SCROLL = True
IMAGE_DURATION = 1200
SEED_IMAGES = 10
SHOW_DEBUG = False

import glib
import subprocess
import commands
import urllib
import urllib2
import re
import os
import random
import glob
from PIL import Image
from sys import stdout
from sys import exit
from lxml import etree
from datetime import datetime, timedelta

# Use XRandR to grab the desktop resolution. If the scaling method is set to 'largest',
# we will attempt to grab it from the largest connected device. If the scaling method
# is set to 'stretch' we will grab it from the current value. Default will simply use
# what was set for the default resolutions.
def find_resolution():
    if RESOLUTION_TYPE == 'default':
        if SHOW_DEBUG:
            print "Using default resolution of %sx%s" % (RESOLUTION_X, RESOLUTION_Y)
        return RESOLUTION_X, RESOLUTION_Y

    res_x = 0
    res_y = 0

    if SHOW_DEBUG:
        print "Attempting to determine the current resolution."
    if RESOLUTION_TYPE == 'largest':
        regex_search = 'connected'
    else:
        regex_search = 'current'
        
    p1 = subprocess.Popen(["xrandr"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["grep", regex_search], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]

    if RESOLUTION_TYPE == 'largest':
        # We are going to go through the connected devices and get the X/Y from the largest
        matches = re.finditer(" connected ([0-9]+)x([0-9]+)+", output)
        if matches:
            largest = 0
            for match in matches:
                if int(match.group(1)) * int(match.group(2)) > largest:
                    res_x = match.group(1)
                    res_y = match.group(2)
        elif SHOW_DEBUG:
            print "Could not determine largest screen resolution."
    else:
        reg = re.search(".* current (.*?) x (.*?),.*", output)
        if reg:
            res_x = reg.group(1)
            res_y = reg.group(2)
        elif SHOW_DEBUG:
            print "Could not determine current screen resolution."

    # If we couldn't find anything automatically use what was set for the defaults
    if res_x == 0 or res_y == 0:
        res_x = RESOLUTION_X
        res_y = RESOLUTION_Y
        if SHOW_DEBUG:
            print "Could not determine resolution automatically. Using defaults."

    if SHOW_DEBUG:
        print "Using detected resolution of %sx%s" % (res_x, res_y)

    return int(res_x), int(res_y)

# Uses GLib to find the localized "Downloads" folder
# See: http://askubuntu.com/questions/137896/how-to-get-the-user-downloads-folder-location-with-python
def set_download_folder():
    downloads_dir = glib.get_user_special_dir(glib.USER_DIRECTORY_DOWNLOAD)
    if downloads_dir:
        # Add any custom folder
        new_path = os.path.join(downloads_dir, CUSTOM_FOLDER)
        if SHOW_DEBUG:
            print "Using automatically detected path:", new_path
    else:
        new_path = DOWNLOAD_PATH
        if SHOW_DEBUG:
            print "Could not determine download folder with GLib. Using default."
    return new_path

# Download HTML of the site
def download_site(url):
    if SHOW_DEBUG:
        print "Downloading contents of the site to find the image name"
    opener = urllib2.build_opener()
    req = urllib2.Request(url)
    try:
        response = opener.open(req)
        reply = response.read()
    except urllib2.HTTPError, error:
        if SHOW_DEBUG:
            print "Error downloading " + url + " - " + str(error.code) 
        reply = "Error: " + str(error.code)
    return reply

# Finds the image URL and saves it
def get_image(text):
    if SHOW_DEBUG:
        print "Grabbing the image URL"
    file_url, filename, file_size = get_image_info('a href', text)

    if SHOW_DEBUG:
        print "Found name of image:", filename

    save_to = os.path.join(DOWNLOAD_PATH, os.path.splitext(filename)[0] + '.png')

    if not os.path.isfile(save_to):
        # If the response body is less than 500 bytes, something went wrong
        if file_size < 500:
            print "Response less than 500 bytes, probably an error\nAttempting to just grab image source"
            file_url, filename, file_size = get_image_info('img src', text)
            print "Found name of image:", filename
            if file_size < 500:
                # Give up
                if SHOW_DEBUG:
                    print "Could not find image to download"
                exit()

        if SHOW_DEBUG:
            print "Retrieving image"
            urllib.urlretrieve(file_url, save_to, print_download_status)

            # Adding additional padding to ensure entire line 
            if SHOW_DEBUG:
                print "\rDone downloading", human_readable_size(file_size), "       "
        else: 
            urllib.urlretrieve(file_url, save_to)
    elif SHOW_DEBUG:
        print "File exists, moving on"

    return save_to

# Resizes the image to the provided dimensions
def resize_image(filename):
    if SHOW_DEBUG:
        print "Opening local image"

    image = Image.open(filename)
    current_x, current_y = image.size
    if (current_x, current_y) == (RESOLUTION_X, RESOLUTION_Y):
        if SHOW_DEBUG:
            print "Images are currently equal in size. No need to scale."
    else: 
        if SHOW_DEBUG:
            print "Resizing the image from", image.size[0], "x", image.size[1], "to", RESOLUTION_X, "x", RESOLUTION_Y
        image = image.resize((RESOLUTION_X, RESOLUTION_Y), Image.ANTIALIAS)

        if SHOW_DEBUG:
            print "Saving the image to", filename
        fhandle = open(filename, 'w')
        image.save(fhandle, 'PNG')

# Sets the new image as the wallpaper
def set_gnome_wallpaper(file_path):
    if SHOW_DEBUG:
        print "Setting the wallpaper"
    command = "gsettings set org.gnome.desktop.background picture-uri file://" + file_path
    status, output = commands.getstatusoutput(command)
    return status

def print_download_status(block_count, block_size, total_size):
    written_size = human_readable_size(block_count * block_size)
    total_size = human_readable_size(total_size)

    # Adding space padding at the end to ensure we overwrite the whole line
    stdout.write("\r%s bytes of %s         " % (written_size, total_size))
    stdout.flush()

def human_readable_size(number_bytes):
    for x in ['bytes', 'KB', 'MB']:
        if number_bytes < 1024.0:
            return "%3.2f%s" % (number_bytes, x)
        number_bytes /= 1024.0

# Creates the necessary XML so background images will scroll through
def create_desktop_background_scoll(filename):
    if not IMAGE_SCROLL:
        return filename

    if SHOW_DEBUG:
        print "Creating XML file for desktop background switching."

    filename = DOWNLOAD_PATH + '/nasa_apod_desktop_backgrounds.xml'

    # Create our base, background element
    background = etree.Element("background")

    # Grab our PNGs we have downloaded
    images = glob.glob(DOWNLOAD_PATH + "/*.png")
    num_images = len(images)

    if num_images < SEED_IMAGES:
        # Let's seed some images
        # Start with yesterday and continue going back until we have enough
        if SHOW_DEBUG:
            print "Downloading some seed images as well"
        days_back = 0
        seed_images_left = SEED_IMAGES
        while seed_images_left > 0:
            days_back+=1
            if SHOW_DEBUG:
                print "Downloading seed image (" + str(seed_images_left) + " left):"
            day_to_try = datetime.now() - timedelta(days=days_back)

            # Filenames look like /apYYMMDD.html
            seed_filename = NASA_APOD_SITE + "ap" + day_to_try.strftime("%y%m%d") + ".html"
            seed_site_contents = download_site(seed_filename)

            # Make sure we didn't encounter an error for some reason
            if seed_site_contents == "error":
                continue

            seed_filename = get_image(seed_site_contents)
            resize_image(seed_filename)

            # Add this to our list of images
            images.append(seed_filename)
            seed_images_left-=1
        if SHOW_DEBUG:
            print "Done downloading seed images"

    # Get our images in a random order so we get a new order every time we get a new file
    random.shuffle(images)
    # Recalculate the number of pictures
    num_images = len(images)

    for i, image in enumerate(images):
        # Create a static entry for keeping this image here for IMAGE_DURATION
        static = etree.SubElement(background, "static")

        # Length of time the background stays
        duration = etree.SubElement(static, "duration")
        duration.text = str(IMAGE_DURATION)

        # Assign the name of the file for our static entry
        static_file = etree.SubElement(static, "file")
        static_file.text = images[i]

        # Create a transition for the animation with a from and to
        transition = etree.SubElement(background, "transition")

        # Length of time for the switch animation
        transition_duration = etree.SubElement(transition, "duration")
        transition_duration.text = "5"

        # We are always transitioning from the current file
        transition_from = etree.SubElement(transition, "from")
        transition_from.text = images[i]

        # Create our tranition to element
        transition_to = etree.SubElement(transition, "to")

        # Check to see if we're at the end, if we are use the first image as the image to
        if i + 1 == num_images:
            transition_to.text = images[0]
        else:
            transition_to.text = images[i + 1]

    xml_tree = etree.ElementTree(background)
    xml_tree.write(filename, pretty_print=True)

    return filename

def get_image_info(element, text):
    # Grabs information about the image
    regex = '<' +  element + '="(image.*?)"'
    reg = re.search(regex, text, re.IGNORECASE)
    if reg:
        if 'http' in reg.group(1):
            # Actual URL
            file_url = reg.group(1)
        else:
            # Relative path, handle it
            file_url = NASA_APOD_SITE + reg.group(1)
    else: 
        if SHOW_DEBUG:
            print "Could not find an image. May be a video today."
        exit()

   # Create our handle for our remote file
    if SHOW_DEBUG:
        print "Opening remote URL"
        
    remote_file = urllib.urlopen(file_url)

    filename = os.path.basename(file_url)
    file_size = float(remote_file.headers.get("content-length"))

    return file_url, filename, file_size

if __name__ == '__main__':
    # Our program
    if SHOW_DEBUG: 
        print "Starting"

    # Find desktop resolution
    RESOLUTION_X, RESOLUTION_Y = find_resolution()

    # Set a localized download folder
    DOWNLOAD_PATH = set_download_folder()

    # Create the download path if it doesn't exist
    if not os.path.exists(os.path.expanduser(DOWNLOAD_PATH)):
        os.makedirs(os.path.expanduser(DOWNLOAD_PATH))

    # Grab the HTML contents of the file 
    site_contents = download_site(NASA_APOD_SITE)
    if site_contents == "error":
        if SHOW_DEBUG:
            print "Could not contact site."
        exit()

    # Download the image
    filename = get_image(site_contents)

    # Resize the image
    resize_image(filename)

    # Create the desktop switching xml
    filename = create_desktop_background_scoll(filename)

    # Set the wallpaper
    status = set_gnome_wallpaper(filename)
    if SHOW_DEBUG:
        print "Finished!"

