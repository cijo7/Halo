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
        self.store = DataStore()
        self.cities = self.store.get_cities()
        self.buttons = []

        if len(self.cities) > 0:
            label = Gtk.Label(label="Choose your city")
            self.box.pack_start(label, True, True, 5)
            txt = "Or enter a new city"
        else:
            txt = "Enter your city"

        # Retrieve and add the city to UI.
        for city in self.cities:
            btn = Gtk.Button()
            btn.connect("clicked", self.btn_click)
            btn.set_label(city[0] + "," + str(city[1]).upper())
            self.box.pack_start(btn, True, True, 0)
            self.buttons.append(btn)
        new_city = Gtk.Label(label=txt.capitalize())
        self.box.pack_start(new_city, True, True, 5)
        self.box.pack_start(self.place, True, True, 5)
        self.set_default_size(150, 100)
        area = self.get_content_area()
        area.add(self.box)
        self.show_all()

    def btn_click(self, widget):
        """
        Select a city.

        :param widget: button
        """
        self.place.set_text(widget.get_label())
        self.response(Gtk.ResponseType.OK)

    def get_city(self) -> str:
        """
        Retrieves the chosen city name.

        :return: city name
        """
        return self.place.get_text()
