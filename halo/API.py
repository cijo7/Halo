from datetime import datetime, timedelta
from typing import Tuple, Dict, Any

import pytz
import requests

from halo.DataStore import DataStore


class API:
    """
    This class is a wrapper for the Rest API endpoints of www.weatherbit.io.
    Currently it implements fetching current weather, forecast and 1 day
    (limit on free plan) historic weather data.
    """
    def __init__(self):
        self._base_url = "https://api.weatherbit.io/v2.0"
        self._headers = {'Accept': 'application/json', 'Accept-Charset': 'UTF-8'}

    def get_current_weather(self, query: str) -> Tuple[str, str, Dict[str, Any]]:
        """
        Fetches and returns current weather data.

        :param query: search query
        :return: a tuple containing city, city timezone, current weather data.
        """
        res = self._send_request(self._url_format("current", query), "weather info")
        current_weather = {
            'status': res['data'][0]['weather']['description'],
            'code': res['data'][0]['weather']['code'],
            'temp': res['data'][0]['temp']
        }
        city = res['data'][0]['city_name'] + ", " + res['data'][0]['country_code']
        city_tz = res['data'][0]['timezone']
        DataStore().add_city((res['data'][0]['city_name'], res['data'][0]['country_code']))
        return city, city_tz, current_weather

    def get_forecast_weather(self, query: str) -> list:
        """
        Fetches and returns the forecast weather data.

        :param query: search query
        :return: forecast weather data.
        """
        query += "&days=5"
        res = self._send_request(self._url_format("forecast/daily", query), "forecast data")
        forecast_weather = res['data']
        return forecast_weather

    def get_forecast_weather_chart(self, query: str) -> list:
        """
        Fetches and returns the forecast weather chart data.

        :param query: search query
        :return: charting data.
        """
        query += "&days=5"
        res = self._send_request(self._url_format("forecast/3hourly", query), "forecast chart")
        chart_data = [item['temp'] for item in res['data']]
        return chart_data

    def get_weather_history(self, query: str, tz: str) -> list:
        """
        Fetches and returns the historic weather data(1 day).

        :param query: search query
        :param tz: city timezone
        :return: historic weather data.
        """
        res = self._send_request(self._url_format("history/daily", query, tz), "historic data")
        history_weather = res['data']
        return history_weather

    def get_weather_history_chart(self, query: str, tz: str) -> list:
        """
        Fetches and returns the historic weather data chart data(1 day).

        :param query: search query
        :param tz: city timezone
        :return: charting data.
        """
        res = self._send_request(self._url_format("history/hourly", query, tz), "historic chart data")
        history_chart_data = [item['temp'] for item in res['data']]
        return history_chart_data

    def _url_format(self, slug: str, query: str, city_tz: str = None, days_count: int = 1) -> str:
        if city_tz:
            start = datetime.now(pytz.timezone(city_tz)).replace(hour=0, minute=0, second=0, microsecond=0) \
                        .astimezone(pytz.utc) - timedelta(days=days_count)
            end = datetime.now(pytz.timezone(city_tz)).replace(hour=0, minute=0, second=0, microsecond=0) \
                .astimezone(pytz.utc)
            return "{base}/{slug}?{query}&start_date={start}&end_date={end}&key={key}&units={units}"\
                .format(base=self._base_url, slug=slug, query=query,
                        start=start.strftime("%Y-%m-%d:%H"), end=end.strftime("%Y-%m-%d:%H"),
                        key=DataStore.get_api_key(), units="I") # This should be switchable in Preferences (F/C) [Url parameter "M" vs. "I" here.
        else:
            return "{base}/{slug}?{query}&key={key}".format(base=self._base_url, slug=slug,
                                                            query=query, key=DataStore.get_api_key(), untis="I") # This should be switchable in Preferences (F/C) [Url parameter "M" vs. "I" here.

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
