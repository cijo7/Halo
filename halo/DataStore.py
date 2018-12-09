"""
Handles the data storage and retrieval.
"""

import sqlite3


class DataStore:
    """sqlite3 database class that store basic city info's."""
    __DB_LOCATION = "database.sqlite"

    def __init__(self, db_location=None):
        """
        Initialises the connection and create a cursor.
        :param db_location: File location of database.
        """
        if db_location:
            self.__DB_LOCATION = db_location
        self.__conn = sqlite3.connect(self.__DB_LOCATION)
        if self.__conn is None:
            raise sqlite3.DatabaseError("Could not get a database connection")
        self.__cur = self.__conn.cursor()
        self._first_run()

    def _first_run(self):
        """Initially create the table."""
        self.__cur.execute('''CREATE TABLE IF NOT EXISTS city(city_name text, 
        country_code text, UNIQUE(city_name, country_code) ON CONFLICT REPLACE)''')

    def get_cities(self):
        """
        Get a list of all the cities
        :return: list of city name and country codes.
        """
        return list(self.__cur.execute('''SELECT * FROM city'''))

    def add_city(self, params):
        """
        Adds the city to db if it doesn't exists.
        :param params: a tuple of city and country code
        """
        self.__cur.execute('''INSERT INTO city VALUES (?,?)''', params)
        self.__conn.commit()

    def __del__(self):
        self.__conn.close()
