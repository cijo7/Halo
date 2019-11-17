from unittest import TestCase

from halo.SummaryView import SummaryView


class TestSummaryView(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.historic = SummaryView(True)
        self.forecast = SummaryView()

    def test_render(self):
        weather_data = [{
            'main':
                {
                    'temp': 25,

                },
            "weather": [{
                "icon": '10d'
            }],
            "dt": 1501970516,
        }]
        self.historic.render(weather_data, list(range(24)))
        self.assertEqual(self.historic.items[0][1].get_text(), "Yesterday")

        weather_data = [{
            'main':
                {
                    'temp': 25,

                },
            "weather": [{
                "icon": '10d'
            }],
            "dt": 1501970516,
        } for _ in range(5)]
        self.forecast.render(weather_data, list(range(24)))
