from unittest import TestCase, main

from halo.Place import PlaceDialog
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402


class TestPlaceDialog(TestCase):
    """Tests for :class:`PlaceDialog` window."""
    def setUp(self):
        TestCase.setUp(self)
        self.dialogue = PlaceDialog(Gtk.ApplicationWindow())

    def test_btn_click(self):
        if len(self.dialogue.buttons) == 0:
            print("There is no button displayed.")

        for btn in self.dialogue.buttons:
            btn.clicked()
            self.assertEqual(btn.get_label(), self.dialogue.get_city(),
                             "Button label and entry mismatch")


if __name__ == "__main__":
    main()
