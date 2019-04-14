# Halo - The Weather App
[![Build Status](https://travis-ci.com/cijo7/Halo.svg?branch=master)](https://travis-ci.com/cijo7/Halo)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/45bd325b322f481087bcf325ef1217ec)](https://www.codacy.com/app/cijo360/Halo)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

Halo is a weather app written in python. You can quickly view the
weather in your city and checkout the forecast and historic temperature trends. 
Halo is smart enough to identify your location based on your ip.

<p align="center">
  <img  src="https://github.com/cijo7/Halo/raw/master/preview.gif">
</p>

<p align="center">
    <a href="https://snapcraft.io/halo-weather">
      <img alt="Get it from the Snap Store" src="https://snapcraft.io/static/images/badges/en/snap-store-black.svg" />
    </a>
</p>

## Prerequisites

1. Python 3
1. Pip

## Installation

### Snap

The easiest way to install halo is via snap. 


To install the latest stable version,

````console
user@ubuntu:~$ sudo snap install halo-weather
````

To install the latest build, 
````console
user@ubuntu:~$ sudo snap install --edge halo-weather
````

### Tarball
To install from the tarball, first download the latest from [releases](https://github.com/cijo7/Halo/releases)

````console
user@ubuntu:~$ wget https://github.com/cijo7/Halo/releases/download/<version>/<file_name>
````

Extract it with

````console
user@ubuntu:~$ tar -xf Halo-X.X.X.tar.gz
````

Change your directory to extracted folder

````console
user@ubuntu:~$ cd Halo-X.X.X
````

Installing required binaries:

````console
user@ubuntu:~$ sudo apt install python3-setuptools pkg-config libcairo2-dev libgirepository1.0-dev gir1.2-gtk-3.0 python3-dev
````

Installing the package

````console
user@ubuntu:~$ sudo python3 setup.py install
`````

## Usage
After installing it, you can directly launch it either by searching for Halo among your installed apps, or from terminal by running

````sh-session
$ halo-weather
````

### Running directly from Source

You can directly run this code without the need of installing anything into your system.
First, you will need to install the dependencies manually by running

````sh-session
$ pip3 install -r requirements.txt
````

Then run the python module by executing

````sh-session
$ python3 -m halo
````
