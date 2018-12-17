import os
from unittest import TestCase, main

from halo.DataStore import DataStore
from halo.settings import DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT


class TestDataStore(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.store = DataStore('test.sqlite')

    def test_rw(self):
        """
        Db Read write tests.
        """
        self.store.add_city(("City", "AB"))
        self.assertTrue(("City", "AB") in self.store.get_cities(),
                        "Unable to read items written to database")

    def test_settings(self):
        """
        Tests the :class:`DataStore` ability to store settings.
        """
        self.store.set_api_key("x" * 32)
        self.store.set_bg_file('not-exists-file.jpg')
        self.store.refresh_preference()

        self.assertEqual(self.store.get_api_key(), "x" * 32)
        self.assertNotEqual(self.store.get_bg_file(), 'not-exists-file.jpg')
        self.store.set_bg_file(os.path.abspath(__file__))
        self.store.refresh_preference()
        self.assertEqual(self.store.get_bg_file(), os.path.abspath(__file__))

    def test_screen(self):
        """
        Tests storing last screen size.
        """
        self.store.screen(800, 500)
        self.store.refresh_preference()
        self.assertEqual(self.store.get_width(), max(DEFAULT_SCREEN_WIDTH, 800))
        self.assertEqual(self.store.get_height(), max(DEFAULT_SCREEN_HEIGHT, 500))


if __name__ == "__main__":
    main()
