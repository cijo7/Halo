from unittest import TestCase

from DataStore import DataStore


class TestDataStore(TestCase):
    def test_rw(self):
        """
        Db Read write tests.
        """
        store = DataStore()
        store.add_city(("City", "AB"))
        self.assertTrue(("City", "AB") in store.get_cities(), "Unable to read items written to database")
