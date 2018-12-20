# Halo - The Weather App [![Build Status](https://travis-ci.com/cijo7/Halo.svg?branch=master)](https://travis-ci.com/cijo7/Halo)
Halo is a weather app written in python. You can quickly view the
weather in your city and checkout the forecast and historic temperature trends. 
Halo is smart enough to identify your location based on your ip.

<p align="center">
  <img  src="https://github.com/cijo7/Halo/raw/master/preview.gif">
</p>

## Prerequisites

1. Python 3
1. Pip

## Installation

### Ubuntu

#### Tarball
To install from [tarball](https://github.com/cijo7/Halo/releases/download/v0.1.3/Halo-0.1.3.tar.gz),

    wget https://github.com/cijo7/Halo/releases/download/v0.1.3/Halo-0.1.3.tar.gz

Extract it with

    tar -xf Halo-0.1.3.tar.gz

Change your directory to extracted folder

    cd Halo-0.1.3


Install required binaries:

    sudo apt install python3-setuptools pkg-config libcairo2-dev libgirepository1.0-dev gir1.2-gtk-3.0 python3-dev

Install the package by running

    sudo python3 setup.py install

## Usage
After installing it, you can directly launch it either by searching for Halo among your installed apps, or from terminal by running

    halo

### Running directly from Source

You can directly run this code without the need of installing anything into your system.
First, you will need to install the dependencies manually by running

    pip3 install -r requirements.txt
    
Then run the python module by executing

    python3 -m halo



