from unittest import TestCase

from halo.SummaryView import SummaryView


class TestSummaryView(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.historic = SummaryView(True)
        self.forecast = SummaryView()

    def test_render(self):
        weather_data = [{
            "ts": 1501970516,
            "temp": 1
        }]
        self.historic.render(weather_data, list(range(24)))
        self.assertEqual(self.historic.items[0][1].get_text(), "Yesterday")

        weather_data = [{
            "ts": 1501970516,
            "temp": 1,
            "weather": {
                "icon": "s02n",
                "code": "601",
                "description": "Snow"
            }} for _ in range(5)]
        self.forecast.render(weather_data, list(range(24)))
        self.assertEqual(self.forecast.items[0][1].get_text(), "Today")
