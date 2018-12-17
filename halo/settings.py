import os

DEBUG = False
VERSION = '0.1.2'
DEFAULT_WEATHER_API_KEY = "ed7d94c3231540d1a8b046f62a3fd8f2"
"""
This api key belongs to the service located at https://www.weatherbit.io.
You can create new api key by signing up at https://www.weatherbit.io/account/create.
"""

BASE = os.path.dirname(os.path.abspath(__file__))

HOME = os.getenv("HOME")
APP_DATA = HOME + "/.halo" if not DEBUG else BASE
os.makedirs(APP_DATA, exist_ok=True)  # Make the directory if it doesn't exists

DEFAULT_BACKGROUND_IMAGE = BASE + '/assets/bg.jpg'
DEFAULT_DB_LOCATION = APP_DATA + "/database.sqlite"

DEFAULT_SCREEN_WIDTH = 700
DEFAULT_SCREEN_HEIGHT = 550
