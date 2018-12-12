import gi

from halo.DataStore import DataStore

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402


class PlaceDialog(Gtk.Dialog):
    """
    Display the change city dialogue.
    """
    def __init__(self, parent):
        """
        Initialises the change city dialogue.
        """
        super().__init__(title="Enter your City", transient_for=parent, modal=True)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.add_button("Change", Gtk.ResponseType.OK)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.place = Gtk.Entry()
        label = Gtk.Label(label="Or choose from the following cities:")
        self.store = DataStore()
        self.cities = self.store.get_cities()
        self.box.pack_start(self.place, True, True, 0)
        self.buttons = []

        if len(self.cities) > 0:
            self.place.set_text(self.cities[0][0] + "," + self.cities[0][1].upper())
            self.box.pack_start(label, True, True, 5)

        # Retrieve and add the city to UI.
        for city in self.cities:
            btn = Gtk.Button()
            btn.connect("clicked", self.btn_click)
            btn.set_label(city[0] + "," + str(city[1]).upper())
            self.box.pack_start(btn, True, True, 2)
            self.buttons.append(btn)
        self.set_default_size(150, 100)
        area = self.get_content_area()
        area.add(self.box)
        self.show_all()

    def btn_click(self, widget):
        self.place.set_text(widget.get_label())

    def get_city(self):
        return self.place.get_text()
