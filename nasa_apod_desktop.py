#!/usr/bin/env python
'''
Copyright (c) 2012 David Drake

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


nasa_apod_desktop.py
https://github.com/randomdrake/nasa-apod-desktop

Written/Modified by David Drake
http://randomdrake.com
http://twitter.com/randomdrake

Based on apodbackground: http://sourceforge.net/projects/apodbackground/
Which, is based on: http://0chris.com/nasa-image-day-script-python.html
-Removed adding text
-Resizing without scaling and adding black background
-Cleaned up code and comments
-Added debug lines
-Check to see if file already exists before attempting download
-Saving as PNG instead of JPG for improved quality


Tested on Ubuntu 12.04


DESCRIPTION
1) Grabs the latest image of the day from NASA (http://apod.nasa.gov/apod/).
2) Resizes the image to the given resolution.
3) Sets the image as your desktop.
4) Adds the image to a list of images that will be cycled through.


INSTALLATION
Ensure you have Python installed (default for Ubuntu) and the python-imaging package:
sudo apt-get install python-imaging

Set your resolution variables and your download path (make sure it's writeable):
'''
DOWNLOAD_PATH = '$HOME/backgrounds/'
RESOLUTION_X = None
RESOLUTION_Y = None
'''

RUN AT STARTUP
To have this run whenever you startup your computer, perform the following steps:
1) Click on the settings button (cog in top right)
2) Select "Startup Applications..."
3) Click the "Add" button
4) Enter the following:
Name: NASA APOD Desktop
Command: python /path/to/nasa_apod_desktop.py
Comment: Downloads the latest NASA APOD and sets it as the background.
5) Click on the "Add" button
'''
import commands
import urllib
import urllib2
import re
import os
import sys
import subprocess

# Configurable settings:
NASA_APOD_SITE = 'http://apod.nasa.gov/apod/'
SHOW_DEBUG = False


def download_site(url):
    ''' Download HTML of the site'''
    if SHOW_DEBUG:
        print "Downloading contents of the site to find the image name"
    opener = urllib2.build_opener()
    req = urllib2.Request(url)
    response = opener.open(req)
    reply = response.read()
    return reply


def get_image(text):
    ''' Finds the image URL and saves it '''
    if SHOW_DEBUG:
        print "Grabbing the image URL"
    reg = re.search('<a href="(image.*?)"', text, re.DOTALL)
    if 'http' in reg.group(1):
        # Actual url
        file_url = reg.group(1)
    else:
        # Relative path, handle it
        file_url = NASA_APOD_SITE + reg.group(1)

    filename = os.path.basename(file_url)
    save_to = DOWNLOAD_PATH + os.path.splitext(filename)[0] + '.png'
    if not os.path.isfile(save_to):
        if SHOW_DEBUG:
            print "Opening remote URL"
        remote_file = urllib.urlopen(file_url)

        if SHOW_DEBUG:
            file_size = float(remote_file.headers.get("content-length"))
            print "Retrieving image %s, saving to %s" % (file_url, save_to)
            urllib.urlretrieve(file_url, save_to, print_download_status)

            # Adding additional padding to ensure entire line
            print "\rDone downloading", human_readable_size(file_size), "       "
        else:
            urllib.urlretrieve(file_url, save_to)
    elif SHOW_DEBUG:
        print "File exists, moving on"

    return save_to


def resize_image(filename):
    ''' Resizes the image to the provided dimensions '''
    if SHOW_DEBUG:
        print "Opening local image"

    try:
        from PIL import Image
    except ImportError:
        print "Cannot import PIL! Trying ImageMagick's convert instead"
        import tempfile
        import shutil
        tempfd, tempfn = tempfile.mkstemp()
        os.close(tempfd)
        cmd = ['convert', filename, '-adaptive-resize', RESOLUTION_S, '-format', 'png',
            tempfn]
        if SHOW_DEBUG:
            print "Resizing with %s" % ' '.join(cmd)
        subprocess.check_call(cmd)
        shutil.copyfile(tempfn, filename)
    else:
        image = Image.open(filename)
        if SHOW_DEBUG:
            print "Resizing the image to", RESOLUTION_S
        image = image.resize((RESOLUTION_X, RESOLUTION_Y), Image.ANTIALIAS)

        if SHOW_DEBUG:
            print "Saving the image to", filename
        fhandle = open(filename, 'w')
        image.save(fhandle, 'PNG')


def set_wallpaper(file_path, flavor=None):
    if not flavor:
        try:
            xprop('XFCE_DESKTOP_WINDOW')
        except KeyError:
            flavor = 'gnome'
        else:
            subprocess.check_call(['xfconf-query', '-c', 'xfce4-desktop',
                '-p', '/backdrop/screen0/monitor0/image-path',
                '-s', file_path])

    if 'gnome' == flavor:
        set_gnome_wallpaper(file_path)


def set_gnome_wallpaper(file_path):
    ''' Sets the new image as the wallpaper '''
    if SHOW_DEBUG:
        print "Setting the wallpaper"
    command = "gsettings set org.gnome.desktop.background picture-uri file://" + file_path
    status, output = commands.getstatusoutput(command)
    return status


def print_download_status(block_count, block_size, total_size):
    written_size = human_readable_size(block_count * block_size)
    total_size = human_readable_size(total_size)

    # Adding space padding at the end to ensure we overwrite the whole line
    sys.stdout.write("\r%s bytes of %s         " % (written_size, total_size))
    sys.stdout.flush()


def human_readable_size(number_bytes):
    for x in ['bytes', 'KB', 'MB']:
        if number_bytes < 1024.0:
            return "%3.2f%s" % (number_bytes, x)
        number_bytes /= 1024.0


def xprop(atom, value=None):
    atom = str(atom)
    cmd = ['xprop', '-root']
    if value:
        value = str(value)
        cmd += ['-format', atom, '8s', '-set', atom, value]
    else:
        cmd.append(atom)
    if SHOW_DEBUG:
        print "Calling", cmd
    if not value:
        line = subprocess.check_output(cmd).splitlines()[0]
        if ' no such atom ' in line:
            raise KeyError
        else:
            return line.split('=' if '=' in line else ':')[1].strip()


def get_desktop_geometry():
    return map(int, xprop('_NET_DESKTOP_GEOMETRY').split(','))


if __name__ == '__main__':
    ''' Our program '''
    if not (RESOLUTION_X and RESOLUTION_Y):
        RESOLUTION_X, RESOLUTION_Y = get_desktop_geometry()
    from optparse import OptionParser
    op = OptionParser()
    op.add_option('-v', '--verbose', action='store_true', default=False)
    op.add_option('--download-path', default=DOWNLOAD_PATH)
    op.add_option('--site', default=NASA_APOD_SITE)
    op.add_option('-s', '--size',
        default='%dx%d' % (RESOLUTION_X, RESOLUTION_Y))
    opts, args = op.parse_args()
    SHOW_DEBUG = SHOW_DEBUG or opts.verbose
    DOWNLOAD_PATH = opts.download_path
    NASA_APOD_SITE = opts.site
    RESOLUTION_X, RESOLUTION_Y = map(int, opts.size.split('x', 1))
    RESOLUTION_S = '%dx%d' % (RESOLUTION_X, RESOLUTION_Y)
    if SHOW_DEBUG:
        print "Starting"
    # Create the download path if it doesn't exist
    DOWNLOAD_PATH = os.path.expandvars(DOWNLOAD_PATH)
    if not os.path.exists(os.path.expanduser(DOWNLOAD_PATH)):
        os.makedirs(os.path.expanduser(DOWNLOAD_PATH))

    # Grab the HTML contents of the file
    site_contents = download_site(NASA_APOD_SITE)

    # Download the image
    filename = get_image(site_contents)

    # Resize the image
    resize_image(filename)

    # Set the wallpaper
    status = set_wallpaper(filename)
    if SHOW_DEBUG:
        print "Finished!"

