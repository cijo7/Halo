"""
Handles the data storage and retrieval.
"""

import sqlite3
import time
from functools import wraps
from os import path
from typing import Tuple

from halo.settings import DEFAULT_DB_LOCATION, DEFAULT_WEATHER_API_KEY, \
    DEFAULT_BACKGROUND_IMAGE, DEFAULT_SCREEN_HEIGHT, DEFAULT_SCREEN_WIDTH, DEFAULT_UNITS, SUPPORTED_UNITS


def query(fn):
    """A decorator which ensures if a database lock ever happen, then sqlite query is retired seamlessly."""
    @wraps(fn)
    def wrap(*args, **kwargs):
        while True:
            try:
                fn(*args, **kwargs)
                break
            except sqlite3.OperationalError as e:
                if "locked" in str(e):
                    time.sleep(1)
                    print("DB is in locked state. Retrying...")
                else:
                    raise
    return wrap


class DataStore:
    """sqlite3 database class that store user data and app settings."""
    __SCREEN_HEIGHT = DEFAULT_SCREEN_HEIGHT
    __SCREEN_WIDTH = DEFAULT_SCREEN_WIDTH
    __API_KEY = DEFAULT_WEATHER_API_KEY
    __BG_FILE = DEFAULT_BACKGROUND_IMAGE
    __UNITS = DEFAULT_UNITS

    def __init__(self, db_location: str = DEFAULT_DB_LOCATION):
        """
        Initialises the connection and create a cursor.

        :param db_location: File location of database.
        """
        self.__DB_LOCATION = db_location
        self.__conn = sqlite3.connect(self.__DB_LOCATION)
        if self.__conn is None:
            raise sqlite3.DatabaseError("Could not get a database connection")
        self.__cur = self.__conn.cursor()
        self._first_run()
        self.refresh_preference()

    def __del__(self):
        self.__conn.close()

    @query
    def _first_run(self):
        """Initially create the tables and row contents."""
        self.__cur.execute('''CREATE TABLE IF NOT EXISTS city(city_name text, 
        country_code text, UNIQUE(city_name, country_code) ON CONFLICT REPLACE)''')
        self.__cur.execute('''CREATE TABLE IF NOT EXISTS setting(name text, 
                value text, UNIQUE(name))''')
        self.__cur.execute('''INSERT or IGNORE INTO setting VALUES('api-key',?)''',
                           (DEFAULT_WEATHER_API_KEY,))
        self.__cur.execute('''INSERT or IGNORE INTO setting VALUES('bg-image',?)''',
                           (DEFAULT_BACKGROUND_IMAGE,))
        self.__cur.execute('''INSERT or IGNORE INTO setting VALUES('screen-width',?)''',
                           (DEFAULT_SCREEN_WIDTH,))
        self.__cur.execute('''INSERT or IGNORE INTO setting VALUES('screen-height',?)''',
                           (DEFAULT_SCREEN_HEIGHT,))
        self.__cur.execute('''INSERT or IGNORE INTO setting VALUES('units',?)''',
                           (DEFAULT_UNITS,))
        self.__conn.commit()

    def refresh_preference(self):
        """Loads latest preference values from db"""
        DataStore.__API_KEY = self.__fetch_settings('api-key')

        bg = self.__fetch_settings('bg-image')
        DataStore.__BG_FILE = bg if path.isfile(bg) else DEFAULT_BACKGROUND_IMAGE

        DataStore.__SCREEN_WIDTH = self.__fetch_settings('screen-width')
        DataStore.__SCREEN_HEIGHT = self.__fetch_settings('screen-height')
        DataStore.__UNITS = self.__fetch_settings('units')

    def __fetch_settings(self, name: str) -> str:
        """
        Fetches the specified settings from database.

        :param name: Name of preference to be fetched.
        :return: Returns the value of the preference.
        """
        return self.__cur.execute('''SELECT value FROM setting WHERE "name"=?''',
                                  (name,)).fetchone()[0]

    @query
    def __update_settings(self, name: str, value: str):
        """
        Updates specific preference value.

        :param name: name of preference to be updated.
        :param value: value of preference.
        """
        self.__cur.execute('''UPDATE setting SET "value"=? WHERE "name"=?''', (value, name))
        self.__conn.commit()

    def get_cities(self) -> list:
        """
        Get a list of all the cities

        :return: list of city name and country codes.
        """
        return list(self.__cur.execute('''SELECT * FROM city'''))

    @query
    def add_city(self, params: Tuple[str, str]):
        """
        Adds the city to db if it doesn't exists.

        :param params: a tuple of city and country code
        """
        self.__cur.execute('''INSERT INTO city VALUES (?,?)''', params)
        self.__conn.commit()

    @staticmethod
    def get_api_key() -> str:
        """
        Retrieves the api key

        :return: API key
        """
        return DataStore.__API_KEY if len(DataStore.__API_KEY) == 32 else DEFAULT_WEATHER_API_KEY

    def set_api_key(self, key: str):
        """
        Writes the new API key if it's valid.

        :param key: API key
        """
        if len(key) == 32:
            self.__update_settings('api-key', key)
        else:
            print("Invalid api key provided. Ignoring silently.")

    @staticmethod
    def get_bg_file() -> str:
        """
        Retrieves the background image path.

        :return: image file path
        """
        return DataStore.__BG_FILE if path.isfile(DataStore.__BG_FILE) else DEFAULT_BACKGROUND_IMAGE

    def set_bg_file(self, file_name: str):
        """
        Writes the new background image path if it exists.

        :param file_name: file path
        """
        if path.isfile(file_name):
            self.__update_settings('bg-image', file_name)
        else:
            print("Invalid background image file path provided. Ignoring silently.")

    @staticmethod
    def get_units():
        return DataStore.__UNITS

    def set_units(self, units):
        if units in SUPPORTED_UNITS.values():
            self.__update_settings('units', units)
        else:
            print("The unit provided is not supported.")

    def screen(self, width: int, height: int):
        """
        Save the screen width and height to the db.

        :param width: Width of screen.
        :param height: Height of screen.
        """
        try:
            self.__update_settings('screen-width', str(max(width, DEFAULT_SCREEN_WIDTH)))
            self.__update_settings('screen-height', str(max(height, DEFAULT_SCREEN_HEIGHT)))
        except sqlite3.OperationalError:
            pass

    @staticmethod
    def get_width() -> int:
        """Retrieves the screen width."""
        return int(DataStore.__SCREEN_WIDTH)

    @staticmethod
    def get_height() -> int:
        """Retrieves the screen height."""
        return int(DataStore.__SCREEN_HEIGHT)
