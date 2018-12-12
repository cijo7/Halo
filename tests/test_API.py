import json
from unittest import TestCase, mock, main

from halo.API import API, NotFound, APIError, RateLimitReached

current = json.loads("""
{
"data": [
    {
      "city_name": "Raleigh",
      "state_code": "NC",
      "country_code": "US",
      "timezone": "America/New_York",
      "lat": 38,
      "lon": -78.25,
      "station": "KRDU",
      "vis": 10000,
      "rh": 75,
      "dewpt": 12,
      "wind_dir": 125,
      "wind_cdir": "ENE",
      "wind_cdir_full": "East-North-East",
      "wind_speed": 5.85,
      "temp": 13.85,
      "app_temp": 14.85,
      "clouds": 42,
      "weather": {
        "icon": "c02",
        "code": "802",
        "description": "Broken clouds"
      },
      "datetime": "2017-03-15:13",
      "ob_time": "2017-03-15 13:11",
      "ts": 1490990400,
      "sunrise": "06:22",
      "sunset": "19:34",
      "slp": 1013.12,
      "pres": 1010,
      "uv": 6.5,
      "dhi": 450.4,
      "elev_angle": 37,
      "hour_angle": 45,
      "pod": "string",
      "precip": 2,
      "snow": 10
    }
  ]
  }
""")
forecast_data = json.loads("""
{
  "city_name": "Raleigh",
  "state_code": "NC",
  "country_code": "US",
  "lat": "38.25",
  "lon": "-78.00",
  "timezone": "America/New_York",
  "data": [
    {
      "datetime": "2017-02-06",
      "ts": 1490990400,
      "snow": 10.45,
      "snow_depth": 45,
      "precip": 1.1,
      "temp": 1,
      "dewpt": 1,
      "max_temp": 1.5,
      "min_temp": -1.23,
      "app_max_temp": 4,
      "app_min_temp": -2,
      "rh": 95,
      "clouds": 100,
      "weather": {
        "icon": "s02n",
        "code": "601",
        "description": "Snow"
      },
      "slp": 1012.89,
      "pres": 1005,
      "uv": 6.5,
      "max_dhi": "655",
      "vis": 3,
      "pop": 75,
      "moon_phase": 0.87,
      "sunrise_ts": 1530331260,
      "sunset_ts": 1530331260,
      "moonrise_ts": 1530331260,
      "moonset_ts": 1530331260,
      "pod": "n",
      "wind_spd": 13.85,
      "wind_dir": 105,
      "wind_cdir": "ENE",
      "wind_cdir_full": "East-North-East"
    }
  ]
}
""")
historical_data_hourly = json.loads("""
{
  "city_name": "Seattle",
  "state_code": "WA",
  "country_code": "US",
  "timezone": "America/New_York",
  "lat": "47.61",
  "lon": "-122.33",
  "sources": [
    "12345-89083"
  ],
  "data": [
    {
      "ts": 1451606400,
      "datetime": "2016-01-01:00",
      "slp": 1020.1,
      "pres": 845,
      "rh": 85,
      "dewpt": -1.5,
      "temp": -1.2,
      "wind_spd": 14.7,
      "wind_dir": 325,
      "uv": 4,
      "ghi": 1500,
      "dhi": 200,
      "dni": 400,
      "h_angle": 15,
      "elev_angle": 27.5,
      "pod": "n",
      "weather": {
        "icon": "s01n",
        "code": "601",
        "description": "Light Snow"
      },
      "precip": 3,
      "precip6h": 6,
      "snow": 30,
      "snow6h": 60
    }
  ]
}
""")
chart_data = json.loads("""
{
  "city_name": "Raleigh",
  "state_code": "NC",
  "country_code": "US",
  "lat": "38.25",
  "lon": "-78.00",
  "timezone": "America/New_York",
  "data": [
    {
      "datetime": "2017-02-06:02",
      "ts": "1490990400",
      "snow": 10.45,
      "snow_depth": 45,
      "snow6h": 140.87,
      "precip": 1.1,
      "precip6h": 14.5,
      "temp": -1.5,
      "dewpt": -4,
      "app_temp": 4.5,
      "rh": 95,
      "clouds": 100,
      "weather": {
        "icon": "s02d",
        "code": "601",
        "description": "Snow"
      },
      "slp": 1012.89,
      "pres": 1005,
      "uv": 6.5,
      "ghi": 1500,
      "dhi": 200,
      "dni": 400,
      "vis": 1,
      "pod": "d",
      "pop": 75,
      "wind_spd": 13.85,
      "wind_dir": 105,
      "wind_cdir": "ENE",
      "wind_cdir_full": "East-North-East"
    }
  ]
}
""")
history_daily_data = json.loads("""
{
  "city_name": "Seattle",
  "state_code": "WA",
  "country_code": "US",
  "timezone": "America/New_York",
  "lat": "47.61",
  "lon": "-122.33",
  "sources": [
    "12345-89083"
  ],
  "data": [
    {
      "datetime": "2015-01-03",
      "ts": 1501970516,
      "slp": 1020.1,
      "pres": 885.1,
      "rh": 85,
      "dewpt": -1.5,
      "temp": 1,
      "max_temp": 1.5,
      "max_temp_ts": 1501970816,
      "min_temp": 11.7,
      "min_temp_ts": 1501970516,
      "wind_spd": 14.98,
      "wind_dir": 325,
      "wind_gust_spd": 340,
      "max_wind_spd": 19.98,
      "max_wind_dir": 325,
      "max_wind_spd_ts": 1501970516,
      "ghi": 125,
      "t_ghi": 4500,
      "dni": 125,
      "t_dni": 4500,
      "dhi": 125,
      "t_dhi": 4500,
      "max_uv": 6,
      "precip": 3,
      "precip_gpm": 3,
      "snow": 30,
      "snow_depth": 60
    }
  ]
}
""")
MOCK_DATA = None


def mock_request(*args, **kwargs):
    class FakeResponse:
        def __init__(self, status, response):
            self.status_code = status
            self.response = response

        def json(self):
            return self.response

    if "ip=0.0.0.1" in args[0]:
        return FakeResponse(204, MOCK_DATA)
    elif "ip=0.0.0.2" in args[0]:
        return FakeResponse(500, MOCK_DATA)
    elif "ip=0.0.0.3" in args[0]:
        return FakeResponse(429, MOCK_DATA)
    if "3hourly" in args[0]:
        return FakeResponse(200, chart_data)
    elif "history/hourly" in args[0]:
        return FakeResponse(200, historical_data_hourly)
    return FakeResponse(200, MOCK_DATA)


class TestAPI(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.api = API()

    @mock.patch('requests.get', side_effect=mock_request)
    def test_get_current_weather(self, mock_get):
        global MOCK_DATA
        MOCK_DATA = current
        with self.assertRaises(NotFound):
            self.api.get_current_weather("ip=0.0.0.1")
        with self.assertRaises(APIError):
            self.api.get_current_weather("ip=0.0.0.2")
        with self.assertRaises(RateLimitReached):
            self.api.get_current_weather("ip=0.0.0.3")

        city, city_tz, current_weather = self.api.get_current_weather("ip=auto")
        self.assertIsNotNone(city, "Invalid city.")
        self.assertIsNotNone(city_tz, "Invalid timezone.")
        self.assertDictEqual({
            'status': 'Broken clouds', 'code': '802', 'temp': 13.85
        }, current_weather, "Invalid current weather data.")

    @mock.patch('requests.get', side_effect=mock_request)
    def test_get_forecast_weather(self, mock_get):
        global MOCK_DATA
        MOCK_DATA = forecast_data
        with self.assertRaises(NotFound):
            self.api.get_forecast_weather("ip=0.0.0.1")
        with self.assertRaises(APIError):
            self.api.get_forecast_weather("ip=0.0.0.2")
        with self.assertRaises(RateLimitReached):
            self.api.get_forecast_weather("ip=0.0.0.3")

        forecast_weather, chart = self.api.get_forecast_weather("ip=auto")
        self.assertIsNotNone(forecast_weather, "Invalid forecast data.")
        self.assertIsNotNone(chart, "Invalid forecast chart data.")

    @mock.patch('requests.get', side_effect=mock_request)
    def test_get_weather_history(self, mock_get):
        global MOCK_DATA
        MOCK_DATA = history_daily_data
        with self.assertRaises(NotFound):
            self.api.get_weather_history("ip=0.0.0.1", "America/New_York")
        with self.assertRaises(APIError):
            self.api.get_weather_history("ip=0.0.0.2", "America/New_York")
        with self.assertRaises(RateLimitReached):
            self.api.get_weather_history("ip=0.0.0.3", "America/New_York")

        history_weather, chart = self.api.get_weather_history("ip=auto", "America/New_York")
        self.assertIsNotNone(history_weather, "Invalid history data.")
        self.assertIsNotNone(chart, "Invalid history chart data.")


if __name__ == '__main__':
    main()
