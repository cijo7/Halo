from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any

import pytz
import requests

from halo.DataStore import DataStore


class API(ABC):
    """
    This class is a wrapper for the Rest API endpoints of provider.
    Currently it implements fetching current weather, forecast and 1 day
    historic weather data (disabled for now as not in free plan) .
    """
    has_historical = False
    has_ip_support = False

    def __init__(self):
        self._headers = {'Accept': 'application/json', 'Accept-Charset': 'UTF-8'}

    @abstractmethod
    def get_current_weather(self, city: str) -> Tuple[str, str, Dict[str, Any]]:
        """
        Fetches and returns current weather data.

        :param city: Can be none.
        :return: a tuple containing city, city timezone, current weather data.
        """
        pass

    @abstractmethod
    def get_forecast_weather(self, query: str) -> list:
        """
        Fetches and returns the forecast weather data.

        :param query: search query
        :return: forecast weather data.
        """
        pass

    @abstractmethod
    def get_weather_history(self, query: str, tz: str) -> list:
        """
        Fetches and returns the historic weather data(1 day).

        :param query: search query
        :param tz: city timezone
        :return: historic weather data.
        """
        pass

    @abstractmethod
    def _url_format(self, slug: str, query: str, city_tz: str = None, days_count: int = 1) -> str:
        pass

    @abstractmethod
    def _send_request(self, url: str, parent: str = "data") -> Any:
        """
        Return data from end point.
        :param url:
        :param parent:
        :return:
        """
        pass


class APIError(Exception):
    """
    An Exception class for exceptions that occur due to external problems
    with the API service.
    """
    pass


class NotFound(APIError):
    """
    An Exception that will occur when data for a city is not found.
    """
    pass


class RateLimitReached(APIError):
    """
    Daily rate limit of API service has been reached and we must wait until it resets.
    """
    pass


class OpenWeatherMap(API):
    """
    Implements openweathermap.org
    """
    has_historical = False
    """ set this to true if you have a paid api key."""

    def __init__(self):
        super().__init__()
        self._base_url = "https://api.openweathermap.org/data/2.5"

    @staticmethod
    def get_units():
        u = DataStore.get_units()
        if u == 'M':
            return 'metric'
        elif u == 'I':
            return 'imperial'
        elif u == 'S':
            return 'standard'
        else:
            return 'metric'

    @staticmethod
    def get_icons(icon):
        if icon == '11d' or icon == '11n':
            return 201
        elif icon == '01d' or icon == '01n':
            return 800
        elif icon == '02d' or icon == '02n':
            return 801
        elif icon == '03d' or icon == '03n':
            return 804
        elif icon == '04d' or icon == '04n':
            return 804
        elif icon == '09d' or icon == '09n':
            return 300
        elif icon == '10d' or icon == '10n':
            return 500
        elif icon == '13d' or icon == '13n':
            return 600
        elif icon == '50d' or icon == '50n':
            return 731
        else:
            return None

    def get_current_weather(self, query):
        if query is None:
            query = "q=London,GB"
        else:
            query = "q={}".format(query)
        res = self._send_request(self._url_format("weather", query), "weather info")
        current_weather = {
            'status': res['weather'][0]['main'],
            'code': self.get_icons(res['weather'][0]['icon']),
            'temp': res['main']['temp']
        }
        city = res['name'] + ", " + res['sys']['country']
        if res['sys']['country'] in pytz.country_timezones:
            city_tz = pytz.country_timezones(res['sys']['country'])[0]
        else:
            city_tz = pytz.utc
        DataStore().add_city((res['name'], res['sys']['country']))

        return city, city_tz, current_weather

    def get_forecast_weather(self, city: str) -> tuple:
        if city is None:
            query = "q=London,GB"
        else:
            query = "q={}".format(city)
        res = self._send_request(self._url_format("forecast", query), "forecast data")
        forecast_weather = res['list']
        chart_data = [item['main']['temp'] for item in res['list']]
        return forecast_weather, chart_data

    def get_weather_history(self, city: str, tz: str) -> tuple:
        res = self._send_request(self._url_format("history", city, tz), "historic data")
        history_weather = res['list']
        history_chart_data = [item['main']['temp'] for item in res['list']]
        return history_weather, history_chart_data

    def _url_format(self, slug: str, query: str, city_tz: str = None, days_count: int = 5) -> str:
        if city_tz:
            start = datetime.now(pytz.timezone(city_tz)).replace(hour=0, minute=0, second=0, microsecond=0) \
                        .astimezone(pytz.utc) - timedelta(days=days_count)
            end = datetime.now(pytz.timezone(city_tz)).replace(hour=0, minute=0, second=0, microsecond=0) \
                .astimezone(pytz.utc)
            return "{base}/{slug}?{query}&start={start}&end={end}&type=hour&appid={key}&units={units}" \
                .format(base=self._base_url, slug=slug, query=query,
                        start=start.timestamp(), end=end.timestamp(),
                        key=DataStore.get_api_key(), units=self.get_units())
        else:
            return "{base}/{slug}?{query}&appid={key}&units={units}".format(base=self._base_url, slug=slug,
                                                                            query=query, key=DataStore.get_api_key(),
                                                                            units=self.get_units())

    def _send_request(self, url: str, parent: str = "data") -> Any:
        try:
            r = requests.get(url, headers=self._headers)
            if r.status_code == 200:
                try:
                    return r.json()
                except ValueError:
                    raise APIError("Invalid response from server. Please try again later.")
            elif r.status_code == 204:
                raise NotFound("The weather information for the requested city is not found.")
            elif r.status_code == 429:
                raise RateLimitReached("The API rate limit has reached. Please wait until it resets or go to "
                                       "Menu -> Preference and enter your own API key.")
            else:
                raise APIError("Unable to fetch %s. Please make sure your API key given in Menu -> Preference is "
                               "valid or try again later." % parent)
        except requests.ConnectionError:
            raise APIError("Something went wrong. Check your internet connection or please try again later.")


def get_location():
    res = requests.get('https://ipapi.co/json/')
    if res.status_code == 200:
        try:
            r = res.json()
            return r['city'] + "," + r['country']
        except ValueError:
            pass
    else:
        return 'Kochi,IN'
