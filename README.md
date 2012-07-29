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

While searching around for the original source, I found out that the project I grabbed from was originally based on a [different script](http://apod.nasa.gov/apod/astropix.html), which I think is worth mentioning.

Installation:
=====
* Ensure you have Python installed (default in Ubuntu)
* Install python-imaging (sudo apt-get install python-imaging)
* Place the file wherever you like and chmod +x it to make it executable
* Set the defaults in the file 

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
* Make this download the file and append to an appropriate XML file so I can get the cycling background back.
* In addition to the XML file, I would like to have the script seed 10 images to scroll through to get started.
* Make a blog post / homepage.

License:
=====
Open-source and free for use.
>Copyright 2012 David Drake
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
