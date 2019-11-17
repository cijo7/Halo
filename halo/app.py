#!/usr/bin/env python3

import concurrent.futures
import sys
import threading
from datetime import datetime

import gi
import pytz
from matplotlib import rcParams

from halo.API import OpenWeatherMap, APIError, RateLimitReached, NotFound, get_location
from halo.DataStore import DataStore
from halo.Icon import Icon
from halo.Place import PlaceDialog
from halo.Preference import PreferenceDialog
from halo.SummaryView import SummaryView
from halo.settings import BASE, VERSION, DEFAULT_SCREEN_HEIGHT, DEFAULT_SCREEN_WIDTH, DISPLAY_TEMP_UNITS

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk, GObject, GLib  # noqa: E402

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Lato', 'DejaVu Sans']


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, application):
        """
        Initialises the main window
        """
        super().__init__(application=application)
        self.api = OpenWeatherMap()
        self.store = DataStore()
        self.city = None
        self.city_tz = "UTC"
        self.currentWeather = None
        self.forecastWeather = []
        self.chartData = []
        self.historyWeather = []
        self.historyChartData = []
        self.LH = 0
        self.LW = 0

        # Background image
        self.overlay = Gtk.Overlay()
        self.add(self.overlay)
        self.bg = Gtk.Image()
        scrollable_wrapper = Gtk.ScrolledWindow()
        scrollable_wrapper.add(self.bg)
        scrollable_wrapper.set_size_request(DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT)
        self.overlay.add(scrollable_wrapper)

        # Header
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Halo"
        self.set_titlebar(header)

        refresh_btn = Gtk.Button(label=None, image=Gtk.Image(icon_name='view-refresh-symbolic',
                                                             icon_size=Gtk.IconSize.BUTTON))
        refresh_btn.connect("clicked", self.refresh)

        # Dropdown menu
        menubar = Gtk.MenuBar()
        ac_grp = Gtk.AccelGroup()
        self.add_accel_group(ac_grp)

        menu = Gtk.ImageMenuItem()
        menu.set_image(Gtk.Image(icon_name='view-more-symbolic',
                                 icon_size=Gtk.IconSize.MENU))
        menu.set_always_show_image(True)
        menu_dropdown = Gtk.Menu()

        menu_refresh = Gtk.MenuItem("Refresh", ac_grp)
        menu_preference = Gtk.MenuItem("Preference")
        menu_city_change = Gtk.MenuItem("Change City")
        menu_about = Gtk.MenuItem("About")
        menu_exit = Gtk.MenuItem("Exit")

        menu_refresh.add_accelerator("activate", ac_grp, ord('R'), Gdk.ModifierType.CONTROL_MASK,
                                     Gtk.AccelFlags.VISIBLE)
        menu_city_change.add_accelerator("activate", ac_grp, ord('C'), 0, Gtk.AccelFlags.VISIBLE)

        menu_refresh.connect('activate', self.refresh)
        menu_preference.connect('activate', self.show_preference)
        menu_city_change.connect('activate', self.switch_city)
        menu_about.connect('activate', self.show_about)
        menu_exit.connect('activate', lambda w: application.quit())

        menu_dropdown.append(menu_refresh)
        menu_dropdown.append(menu_preference)
        menu_dropdown.append(menu_city_change)
        menu_dropdown.append(menu_about)
        menu_dropdown.append(Gtk.SeparatorMenuItem())
        menu_dropdown.append(menu_exit)
        menu.set_submenu(menu_dropdown)
        menubar.append(menu)

        header.pack_end(menubar)
        header.pack_end(refresh_btn)

        # Weather Panel
        tm = Gtk.Box(spacing=0)
        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        top = Gtk.Box(spacing=10)
        view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left.set_homogeneous(False)
        right.set_homogeneous(False)

        self.icon = Gtk.Image()
        self.place = Gtk.Label()
        self.status = Gtk.Label()
        self.temperature = Gtk.Label()
        self.time = Gtk.Label()
        self.t_follow = Gtk.Label()
        self.date = Gtk.Label()

        self.time.set_alignment(0, 1)
        self.t_follow.set_alignment(0, 1)
        self.date.set_alignment(0, 0)
        self.icon.set_alignment(1, 0)
        self.status.set_alignment(1, 0)
        self.place.set_alignment(1, 0)
        self.temperature.set_alignment(1, 0)

        self.time.set_name("time")
        self.t_follow.set_name("t_follow")
        self.date.set_name("date")
        self.status.set_name("status")
        self.place.set_name("place")
        self.temperature.set_name("temperature")
        view.set_name("box")

        tm.pack_start(self.time, False, False, 2)
        tm.pack_start(self.t_follow, False, False, 2)
        left.pack_start(tm, False, False, 0)
        left.pack_start(self.date, False, False, 0)
        right.pack_start(self.icon, False, False, 0)
        right.pack_start(self.status, False, False, 0)
        right.pack_start(self.place, False, False, 0)
        right.pack_start(self.temperature, False, False, 10)
        top.pack_start(left, True, True, 20)
        top.pack_start(right, True, True, 20)

        # Summary and Trend View
        switcher = Gtk.StackSwitcher()
        stack_area = Gtk.Stack()
        self.forecastArea = SummaryView()
        self.historyArea = SummaryView(True)

        stack_area.add_titled(self.historyArea.get_view(), "history", "History")
        stack_area.add_titled(self.forecastArea.get_view(), "forecast", "Forecast")
        stack_area.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack_area.set_transition_duration(150)
        stack_area.set_homogeneous(True)
        switcher.set_name("toggle")
        switcher.set_opacity(0.92)
        switcher.set_stack(stack_area)
        sw_b = Gtk.Box(spacing=10)
        sw_b.pack_start(switcher, False, False, 25)

        view.pack_start(top, True, True, 10)
        view.pack_start(sw_b, False, False, 0)
        view.pack_start(stack_area, False, False, 0)
        self.overlay.add_overlay(view)

        # Styling
        screen = Gdk.Screen().get_default()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(BASE + '/style.css')
        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.set_default_size(DataStore.get_width(), DataStore.get_height())
        self.set_position(Gtk.WindowPosition.CENTER)

        self.connect('size-allocate', lambda w, rect: GObject.idle_add(
            self.win_resize, rect, priority=GLib.PRIORITY_HIGH))
        self.set_icon_from_file(BASE + "/assets/halo.svg")
        self.show_all()

        GObject.timeout_add_seconds(2, self.update_time)
        GObject.idle_add(self.refresh)
        stack_area.set_visible_child_name("forecast")

    def win_resize(self, screen):
        """
        Resize the background image when window is resized
        and store new screen size to db.
        """
        if self.LW is not screen.width or self.LH is not screen.height:
            self.bg.set_size_request(screen.width, screen.height)
            buff = GdkPixbuf.Pixbuf.new_from_file(DataStore.get_bg_file())
            buff = buff.scale_simple(screen.width, screen.height, GdkPixbuf.InterpType.BILINEAR)
            self.bg.set_from_pixbuf(buff)

            self.store.screen(screen.width, screen.height)
            self.LW = screen.width
            self.LH = screen.height

    def switch_city(self, widget=None):
        """Change the city for which weather data is displayed"""
        dialog = PlaceDialog(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            if dialog.get_city() != "":
                self.city = dialog.get_city()
                self.refresh()
        dialog.destroy()

    def show_preference(self, w):
        """
        Shows the Preference dialog.

        :param w: Widget
        """
        preference = PreferenceDialog(self)
        preference.run()
        self.LH = 0  # This will force redraw of background on window
        preference.save_preference()
        preference.destroy()

    def show_about(self, w):
        """
        Shows the about dialog.

        :param w: Widget
        """
        about = Gtk.AboutDialog(transient_for=self, modal=True)

        buff = GdkPixbuf.Pixbuf.new_from_file(BASE + "/assets/halo.svg")
        buff = buff.scale_simple(75, 75, GdkPixbuf.InterpType.BILINEAR)
        about.set_logo(buff)

        author = ["Cijo Saju"]
        about.set_program_name("Halo")
        about.set_license_type(Gtk.License.MIT_X11)
        about.set_copyright("Copyrights © {} Cijo Saju".format(datetime.now().strftime("%Y")))
        about.set_authors(author)
        about.set_website("https://github.com/cijo7/Halo")
        about.set_website_label("View on Github")
        about.set_version(VERSION)
        about.run()
        about.destroy()

    def fetch_weather(self, city=None, widget=None):
        """
        Fetch the weather data from online endpoints and update the ui.

        :param city: City for which weather is fetched.
        :param widget: The GUI widget that triggered search.
        """
        # If no city is specified, then detect location based on user ip.
        if city is None and not self.api.has_ip_support:
            city = get_location()

        def not_found(err):
            """
            Display an error message when the weather data for the
            searched city is not found

            :param err: Exception
            """
            error = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                      Gtk.ButtonsType.CLOSE, str(err))
            self.clear_cursor(widget)
            error.run()
            error.destroy()

            self.city = None

        def api_error(err):
            """
            Display an error when something goes wrong with
            api call, like no internet connection and ask whether we should retry.

            :param err: Exception
            """
            error = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                      (Gtk.STOCK_QUIT, Gtk.ResponseType.CLOSE,
                                       Gtk.STOCK_CLEAR, Gtk.ResponseType.CANCEL,
                                       "Try Again", Gtk.ResponseType.OK), str(err))

            self.clear_cursor(widget)
            r = error.run()
            error.destroy()
            if r == Gtk.ResponseType.OK:
                self.refresh()
            elif r == Gtk.ResponseType.CANCEL:
                pass
            else:
                exit(0)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as exe:
                # Current weather
                current = exe.submit(self.api.get_current_weather, city)
                # Forecast
                forecast = exe.submit(self.api.get_forecast_weather, city)
                self.city, self.city_tz, self.currentWeather = current.result()

                # Historic data fetched with tz returned from previous call
                if self.api.has_historical:
                    history = exe.submit(self.api.get_weather_history, city, self.city_tz)
                self.forecastWeather, self.chartData = forecast.result()
                # Render current weather
                GObject.idle_add(self.render_weather)
                GObject.idle_add(self.forecastArea.render, self.forecastWeather, self.chartData)

                # Render history data
                if self.api.has_historical:
                    self.historyWeather, self.historyChartData = history.result()
                    GObject.idle_add(self.historyArea.render, self.historyWeather, self.historyChartData)
                GObject.idle_add(self.clear_cursor, widget)
        except NotFound as e:
            GObject.idle_add(not_found, e)
        except (APIError, RateLimitReached) as e:
            GObject.idle_add(api_error, e)

    def render_weather(self):
        """
        Update the current weather info of currently chosen city
        """
        if self.currentWeather is None:
            return
        self.icon.set_from_pixbuf(Icon.get_icon(self.currentWeather['code'], 60))
        self.place.set_text(self.city)
        self.status.set_text(self.currentWeather['status'].title())
        self.temperature.set_text(str(int(self.currentWeather['temp'])) + DISPLAY_TEMP_UNITS[DataStore.get_units()])
        self.update_time()

    def refresh(self, widget=None):
        """Fetch the latest data into the ui"""
        if widget is not None:
            widget.set_sensitive(False)
        self.busy_cursor()
        thread = threading.Thread(target=self.fetch_weather, args=(self.city, widget))
        thread.start()

    # noinspection PyUnusedLocal
    def busy_cursor(self, w=None):
        watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        win = self.get_window()
        if win:
            win.set_cursor(watch_cursor)

    def clear_cursor(self, widget=None):
        arrow_cursor = Gdk.Cursor(Gdk.CursorType.ARROW)
        win = self.get_window()
        if win:
            win.set_cursor(arrow_cursor)
        if widget is not None:
            widget.set_sensitive(True)

    def update_time(self):
        """Updates the time shown as per the timezone of currently chosen city"""
        dt = datetime.now(pytz.utc).astimezone(pytz.timezone(self.city_tz))
        self.time.set_text(dt.strftime("%I:%M "))
        self.t_follow.set_text(dt.strftime("%p"))
        self.date.set_text(dt.strftime("%A, %d %B %Y"))
        return True


class Halo(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        MainWindow(self)

    def do_startup(self):
        Gtk.Application.do_startup(self)


if __name__ == '__main__':
    app = Halo()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
