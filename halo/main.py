#!/usr/bin/env python3

import sys
import threading
from datetime import datetime

import gi
import pytz
from matplotlib import rcParams

from halo.API import API, APIError, RateLimitReached, NotFound
from halo.Icon import Icon
from halo.PlaceDialogue import PlaceDialog
from halo.SummaryView import SummaryView
from halo.settings import BACKGROUND_IMAGE, BASE

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk, GObject  # noqa: E402

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Lato', 'DejaVu Sans']


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        """Initialises the main window"""
        super().__init__(application=app)
        self.api = API()
        self.city = None
        self.city_tz = "UTC"
        self.currentWeather = None
        self.forecastWeather = []
        self.chartData = []
        self.historyWeather = []
        self.historyChartData = []

        # Background image
        self.overlay = Gtk.Overlay()
        self.add(self.overlay)
        self.bg = Gtk.Image()
        scrollable_wrapper = Gtk.ScrolledWindow()
        scrollable_wrapper.add(self.bg)
        scrollable_wrapper.set_size_request(700, 500)
        self.overlay.add(scrollable_wrapper)

        # Header
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Halo"
        self.set_titlebar(header)

        change_place = Gtk.Button(label="Change City")
        change_place.connect("clicked", self.switch_city)
        refresh_btn = Gtk.Button(label=None, image=Gtk.Image(stock=Gtk.STOCK_REFRESH))
        refresh_btn.connect("clicked", self.refresh)
        header.pack_end(change_place)
        header.pack_end(refresh_btn)

        # Weather Panel
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
        self.date = Gtk.Label()

        self.time.set_alignment(0, 0)
        self.date.set_alignment(0, 0)
        self.icon.set_alignment(1, 0)
        self.status.set_alignment(1, 0)
        self.place.set_alignment(1, 0)
        self.temperature.set_alignment(1, 0)

        self.time.set_name("time")
        self.date.set_name("date")
        self.status.set_name("status")
        self.place.set_name("place")
        self.temperature.set_name("temperature")

        left.pack_start(self.time, False, False, 0)
        left.pack_start(self.date, False, False, 0)
        right.pack_start(self.icon, False, False, 0)
        right.pack_start(self.status, False, False, 0)
        right.pack_start(self.place, False, False, 0)
        right.pack_start(self.temperature, False, False, 0)
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

        screen = Gdk.Screen().get_default()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(BASE + '/style.css')
        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.set_default_size(700, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect('check-resize', lambda w: self.check_resize())
        self.set_icon_from_file(BASE + "/assets/halo.svg")
        self.show_all()

        GObject.timeout_add_seconds(2, self.update_time)
        GObject.idle_add(self.refresh)
        stack_area.set_visible_child_name("forecast")

    def check_resize(self):
        """Resize the background image when window is resized."""
        screen = self.get_size()
        self.bg.set_size_request(screen.width, screen.height)

        buff = GdkPixbuf.Pixbuf.new_from_file(BACKGROUND_IMAGE)
        buff = buff.scale_simple(screen.width, screen.height, GdkPixbuf.InterpType.BILINEAR)
        self.bg.set_from_pixbuf(buff)

    # noinspection PyUnusedLocal
    def switch_city(self, widget):
        """Change the city for which weather data is displayed"""
        dialog = PlaceDialog(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            if dialog.get_city() != "":
                self.city = dialog.get_city()
                self.refresh()
        dialog.destroy()

    def fetch_weather(self, city=None):
        """Fetch the weather data from online endpoints and update ui"""
        # If no city is specified, then detect location based on user ip.
        query = "ip=auto" if city is None else "city=" + city

        def not_found(err):
            """
            Display an error message when the weather data for the
            searched city is not found

            :param err: Exception
            """
            error = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                      Gtk.ButtonsType.CLOSE, str(err))

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

            self.clear_cursor()
            r = error.run()
            error.destroy()
            if r == Gtk.ResponseType.OK:
                self.refresh()
            elif r == Gtk.ResponseType.CANCEL:
                pass
            else:
                exit(0)

        try:
            # current weather
            self.city, self.city_tz, self.currentWeather = self.api.get_current_weather(query)
            GObject.idle_add(self.render_weather)

            # Forecast
            self.forecastWeather, self.chartData = self.api.get_forecast_weather(query)
            GObject.idle_add(self.forecastArea.render, self.forecastWeather, self.chartData)

            # Weather history
            self.historyWeather, self.historyChartData = self.api.get_weather_history(query, self.city_tz)
            GObject.idle_add(self.historyArea.render, self.historyWeather, self.historyChartData)

            GObject.idle_add(self.clear_cursor)
        except NotFound as e:
            GObject.idle_add(not_found, e)
        except (APIError, RateLimitReached) as e:
            GObject.idle_add(api_error, e)
        return False

    def render_weather(self):
        """Update the current weather info of currently chosen city"""
        if self.currentWeather is None:
            print(self.currentWeather)
            return
        self.icon.set_from_pixbuf(Icon.get_icon(self.currentWeather['code'], 60))
        self.place.set_text(self.city)
        self.status.set_text(self.currentWeather['status'].title())
        self.temperature.set_text(str(int(self.currentWeather['temp'])) + "°")
        self.update_time()

    # noinspection PyUnusedLocal
    def refresh(self, w=None):
        """Fetch the latest data into the ui"""
        self.busy_cursor()
        thread = threading.Thread(target=self.fetch_weather, args=(self.city,))
        thread.start()

    # noinspection PyUnusedLocal
    def busy_cursor(self, w=None):
        watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.get_window().set_cursor(watch_cursor)

    def clear_cursor(self):
        arrow_cursor = Gdk.Cursor(Gdk.CursorType.ARROW)
        self.get_window().set_cursor(arrow_cursor)

    def update_time(self):
        """Updates the time shown as per the timezone of currently chosen city"""
        dt = datetime.now(pytz.utc).astimezone(pytz.timezone(self.city_tz))
        self.time.set_text(dt.strftime("%I:%M %p"))
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
