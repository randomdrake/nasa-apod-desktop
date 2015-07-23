nasa-apod-desktop
=====

Python Script to Download the NASA APOD and Set it as Your Background for Ubuntu
-----

About:
=====
The popular NASA Astronomy Picture of the Day produces wonderful images that make for a great desktop background. This script will download the NASA APOD and set it as your background in Ubuntu.

![NASA APOD Example](http://randomdrake.com/nasa_apod.jpg "An example of a NASA APOD image.")

http://en.wikipedia.org/wiki/Astronomy_Picture_of_the_Day

http://apod.nasa.gov/apod/astropix.html

Tested on, and created for, Ubuntu 12.04.

How it Works:
=====
1. Grabs your current download path
2. Downloads the latest image of the day from NASA ([http://apod.nasa.gov/apod/](http://apod.nasa.gov/apod/))
3. Determines your desktop resolution, or uses the set default
4. Resizes the image to the given resolution
5. Sets the image as your desktop
6. Adds image to XML file used to scroll through desktop background images.

It's not very exciting to scroll through a single image, so it will attempt to download additional images (default: 10) to seed your list of images.

Development:
=====

I really enjoyed the NASA background images that were easily available in Windows 7. I wanted to recreate the experience for Ubuntu as I don't use Windows 7 at home, much.

Searching around in Google, I came across the [apodbackground](http://apod.nasa.gov/apod/astropix.html) project. Unfortunately, the git link was broken. I eventually found a mirror and took a look at the code. There were a few changes that I thought were necessary:
* Removal of the description text. I just wanted an image, no text as I live in a semi-transparent terminal most of the time.
* Instead of appropriately scaling the image based on the size and placing it on a black background, I wanted the image to be scaled to the size I specified no matter what so I didn't have distracting vertical lines.
* Cleaned up the code and the comments.
* Added debugging information to see what's going on.
* Checked to see if the file already existed before performing the download.
* Saving as a PNG instead of a JPG. Yes, the filesize is increased quite a bit but we remove the artifacts and get a much cleaner image.

After I modified the original script, I still wanted to allow for the image scrolling to return. I found the XML file that comes with Ubuntu in /usr/share/backgrounds/contest/precise.xml that is used to create the background scrolling. From there, I got a hold of lxml and went to town. 

But, generating the XML file wasn't enough. I also wanted to start with a number of images so I would actually have some to scroll through. 

While searching around for the original source, I found out that the project I grabbed from was originally based on a [different script](http://apod.nasa.gov/apod/astropix.html), which I think is worth mentioning.

Please note: I am not extremely well-versed in Python. I have been playing with the language and Django lately so, if improvements could be made, please let me know.

Installation:
=====
* Place the file wherever you like and `chmod +x` it to make it executable
* Ensure you have Python installed (default for Ubuntu) and the PIL and lxml packages:
* `pip install -f requirements.txt` or `sudo apt-get install python-imaging python-lxml`
  * pip may have trouble installing PIL, if so run `pip install PIL --allow-external PIL --allow-unverified PIL`
* Set the defaults in the file 
  
Defaults:
=====
While the script will detect as much as possible and has safe defaults, you may want to set your own.

* __DOWNLOAD\_PATH__ - where you want the file to be downloaded. Will be auto-detected if not set.
* __CUSTOM\_FOLDER__ - if we detect your download folder, this will be the target folder in there.
* __RESOUTION\_TYPE__ -   
    'stretch': single monitor or the combined resolution of your available monitors  
    'largest': largest resolution of your available monitors      
    'default': use the default resolution that is set
* __RESOLUTION\_X__ - horizontal resolution if RESOLUTION\_TYPE is not default or cannot be automatically determined
* __RESOLUTION\_Y__ - vertical resolution if RESOLUTION\_TYPE is not default or cannot be automatically determined
* __NASA\_APOD\_SITE__ - location of the current picture of the day
* __IMAGE_SCROLL__   - if true, will write also write an XML file to make the images scroll
* __IMAGE_DURATION__ - if IMAGE\_SCROLL is enabled, this is the duration each will stay in seconds
* __SEED_IMAGES__    - if > 0, it will download previous images as well to seed the list of images
* __SHOW\_DEBUG__ - whether to print useful debugging information or statuses

Run at Startup:
=====
If you want the file to automatically run at startup:

1. Click on the settings button (cog in top right)
2. Select "Startup Applications..."
3. Click the "Add" button
4. Enter whatever name and comment you like and make sure the "Command" is set to: python /path/to/nasa_apod_desktop.py
5. Click on the "Add" button

To Do:
=====
* Make a blog post / homepage.

License:
=====
Open-source and free for use.

Unfortunately, I don't have time to update this script at the moment. This software is currently as is and I would definitely recommend checking out some of the various forks for updates or fixes.

>Copyright (c) 2012 David Drake
>
>Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
>
>http://www.apache.org/licenses/LICENSE-2.0
>
>Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License. 

Author:
=====
David Drake 

[@randomdrake](https://twitter.com/randomdrake) | [http://randomdrake.com](http://randomdrake.com) | [LinkedIn](http://www.linkedin.com/pub/david-drake/52/247/465)
