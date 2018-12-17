import gi

from halo.DataStore import DataStore

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf  # noqa: E402
from gi.repository.GLib import GError  # noqa: E402


class PreferenceDialog(Gtk.Dialog):
    """
    Display the Preference dialogue.
    """

    def __init__(self, parent):
        """
        Initialises the Preference dialogue.
        """
        super().__init__(title="Preference", transient_for=parent, modal=True)
        self.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        api = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        txt = Gtk.Label("Your API Key")
        desc = Gtk.Label()
        desc.set_markup('<a href="https://www.weatherbit.io/account/create">Sign up</a>'
                        ' to create new API key.')
        txt.set_alignment(0, 0)
        desc.set_alignment(1, 0)
        desc.set_line_wrap(True)
        self.key = Gtk.Entry()
        self.key.set_text(DataStore.get_api_key())
        api.pack_start(txt, True, True, 0)
        api.pack_start(self.key, True, True, 0)
        api.pack_start(desc, True, True, 0)

        bg = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.preview = Gtk.Image()
        txt = Gtk.Label("Choose a Background Image")
        txt.set_alignment(0, 0)
        self.bg = Gtk.Entry()
        self.bg.set_text(DataStore.get_bg_file())
        btn = Gtk.Button(label="Choose File")
        btn.connect("clicked", self.file_chooser)
        bg.pack_start(txt, True, True, 0)
        bg.pack_start(self.bg, True, True, 0)
        bg.pack_start(btn, False, False, 0)

        box.pack_start(api, True, True, 5)
        box.pack_start(bg, True, True, 5)
        self.set_default_size(300, 100)
        area = self.get_content_area()
        area.add(box)
        self.show_all()

    def save_preference(self):
        """ Saves the latest changes to preferences into the db."""
        key = self.key.get_text()
        bg = self.bg.get_text()
        store = DataStore()
        store.set_api_key(key)
        store.set_bg_file(bg)
        store.refresh_preference()

    def file_chooser(self, widget):
        dialog = Gtk.FileChooserDialog(
            "Please choose a background image",
            self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )

        filter_all = Gtk.FileFilter()
        filter_all.set_name("All Images")
        filter_all.add_mime_type("image/jpeg")
        filter_all.add_mime_type("image/png")
        dialog.add_filter(filter_all)

        filter_jpeg = Gtk.FileFilter()
        filter_jpeg.set_name("JPEG files")
        filter_jpeg.add_mime_type("image/jpeg")
        dialog.add_filter(filter_jpeg)

        filter_png = Gtk.FileFilter()
        filter_png.set_name("PNG files")
        filter_png.add_mime_type("image/png")
        dialog.add_filter(filter_png)
        dialog.set_preview_widget(self.preview)
        dialog.connect('update-preview', self.file_preview)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.bg.set_text(dialog.get_filename())
        dialog.destroy()

    def file_preview(self, widget):
        f = widget.get_preview_filename()
        try:
            buff = GdkPixbuf.Pixbuf.new_from_file(f)
        except (GError, TypeError, OSError, IOError):
            widget.set_preview_widget_active(False)
        else:
            # scale the image
            max_width, max_height = 300.0, 700.0
            width, height = buff.get_width(), buff.get_height()
            scale = min(max_width / width, max_height / height)
            if scale < 1:
                width, height = int(width * scale), int(height * scale)
                buff = buff.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
            self.preview.set_from_pixbuf(buff)
            widget.set_preview_widget_active(True)
