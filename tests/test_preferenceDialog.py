from unittest import TestCase
from halo.Preference import PreferenceDialog
from halo import settings

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402


settings.DEFAULT_DB_LOCATION = 'test.sqlite'


class TestPreferenceDialog(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.preference = PreferenceDialog(Gtk.ApplicationWindow())

    def test_file_preview(self):
        d = Gtk.FileChooserDialog(
            title="Please choose a background image",
            transient_for=self.preference)

        d.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        d.add_button(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        self.reply = None
        fn = 'not-exists'

        def filename():
            return fn

        def widget_active(state):
            self.reply = state

        d.set_preview_widget_active = widget_active
        d.get_preview_filename = filename
        self.preference.file_preview(d)
        self.assertFalse(self.reply, 'Widget preview not removed.')

        self.reply = None
        fn = settings.DEFAULT_BACKGROUND_IMAGE

        self.preference.file_preview(d)
        print(self.reply)
        self.assertTrue(self.reply, 'Widget preview not added.')
